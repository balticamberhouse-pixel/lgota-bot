import json
import logging
import os
from pathlib import Path

import telebot
from telebot import types

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "benefits_database.json"
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set. Create a token with @BotFather and set it as an environment variable. "
        "Never commit a real token to GitHub."
    )

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
user_answers: dict[int, list[int]] = {}

QUESTIONS = [
    ("Есть ли у вас дети?", ["Да", "Нет"]),
    ("Ваш возраст?", ["До 35", "35–55", "56+ "]),
    ("Есть ли у вас инвалидность?", ["Да", "Нет"]),
    ("Расходы на ЖКХ заметно превышают возможности семьи?", ["Да", "Нет", "Не знаю"]),
    ("Получаете ли вы пенсию?", ["Да", "Нет"]),
]


def load_data() -> dict:
    with DATABASE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_benefits() -> list[dict]:
    return load_data()["benefits"]


def main_menu() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎯 Подобрать льготы")
    markup.row("📋 Каталог", "ℹ️ Важно")
    return markup


def options_keyboard(options: list[str]) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for index, label in enumerate(options):
        markup.add(types.InlineKeyboardButton(label, callback_data=f"audit:{index}"))
    return markup


def catalogue_keyboard(items: list[dict]) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for item in items:
        markup.add(types.InlineKeyboardButton(item["name"][:60], callback_data=f"benefit:{item['id']}"))
    return markup


def detail_keyboard(item: dict) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    if item.get("official_url"):
        markup.add(types.InlineKeyboardButton("Официальная страница", url=item["official_url"]))
    markup.add(types.InlineKeyboardButton("← К каталогу", callback_data="catalogue"))
    return markup


def show_question(chat_id: int, question_index: int) -> None:
    if question_index >= len(QUESTIONS):
        show_results(chat_id)
        return
    question, options = QUESTIONS[question_index]
    bot.send_message(chat_id, f"<b>Вопрос {question_index + 1}/{len(QUESTIONS)}</b>\n{question}", reply_markup=options_keyboard(options))


def select_recommendations(answers: list[int]) -> list[dict]:
    benefits = get_benefits()
    categories: set[str] = {"Все граждане"}
    if answers and answers[0] == 0:
        categories.add("Семьи с детьми")
    if len(answers) > 2 and answers[2] == 0:
        categories.add("Инвалиды")
    if len(answers) > 3 and answers[3] == 0:
        categories.add("ЖКХ и доход")
    if len(answers) > 4 and answers[4] == 0:
        categories.add("Пенсионеры")
    return [item for item in benefits if item["category"] in categories]


def show_results(chat_id: int) -> None:
    answers = user_answers.pop(chat_id, [])
    selected = select_recommendations(answers)
    if not selected:
        bot.send_message(chat_id, "По ответам не удалось подобрать категорию. Откройте каталог и проверьте официальные условия.", reply_markup=main_menu())
        return
    text = "<b>Предварительный подбор</b>\n\nЭто не решение о назначении выплаты. Условия и суммы зависят от региона и вашей ситуации. Откройте каждую карточку и проверьте данные на официальном сайте."
    bot.send_message(chat_id, text, reply_markup=catalogue_keyboard(selected))


@bot.message_handler(commands=["start"])
def start(message: types.Message) -> None:
    name = message.from_user.first_name or "!"
    bot.send_message(
        message.chat.id,
        f"Здравствуйте, {name} 👋\n\nЯ помогаю сориентироваться в возможных мерах поддержки и найти официальные страницы для проверки условий.",
        reply_markup=main_menu(),
    )


@bot.message_handler(commands=["help"])
def help_command(message: types.Message) -> None:
    bot.send_message(message.chat.id, "Нажмите «Подобрать льготы», ответьте на вопросы и откройте карточки результатов. Не отправляйте боту паспорт, СНИЛС, реквизиты карты или документы.", reply_markup=main_menu())


@bot.message_handler(func=lambda message: message.text == "🎯 Подобрать льготы")
def audit_start(message: types.Message) -> None:
    user_answers[message.chat.id] = []
    show_question(message.chat.id, 0)


@bot.message_handler(func=lambda message: message.text == "📋 Каталог")
def catalogue(message: types.Message) -> None:
    items = get_benefits()
    bot.send_message(message.chat.id, "<b>Каталог</b>\nВыберите интересующую меру поддержки:", reply_markup=catalogue_keyboard(items))


@bot.message_handler(func=lambda message: message.text == "ℹ️ Важно")
def important(message: types.Message) -> None:
    bot.send_message(
        message.chat.id,
        "<b>Важно</b>\n\n• Бот даёт справочную навигацию, а не юридическую консультацию.\n• Условия, размеры выплат и порядок оформления меняются и могут отличаться по регионам.\n• Проверяйте информацию только на официальных ресурсах.\n• Не присылайте персональные и платёжные данные.",
        reply_markup=main_menu(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("audit:"))
def audit_answer(call: types.CallbackQuery) -> None:
    answer = int(call.data.split(":", 1)[1])
    answers = user_answers.setdefault(call.message.chat.id, [])
    answers.append(answer)
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    show_question(call.message.chat.id, len(answers))


@bot.callback_query_handler(func=lambda call: call.data == "catalogue")
def catalogue_callback(call: types.CallbackQuery) -> None:
    bot.answer_callback_query(call.id)
    items = get_benefits()
    bot.edit_message_text("<b>Каталог</b>\nВыберите интересующую меру поддержки:", call.message.chat.id, call.message.message_id, reply_markup=catalogue_keyboard(items))


@bot.callback_query_handler(func=lambda call: call.data.startswith("benefit:"))
def benefit_detail(call: types.CallbackQuery) -> None:
    benefit_id = int(call.data.split(":", 1)[1])
    item = next((benefit for benefit in get_benefits() if benefit["id"] == benefit_id), None)
    bot.answer_callback_query(call.id)
    if not item:
        bot.send_message(call.message.chat.id, "Карточка не найдена. Откройте каталог ещё раз.")
        return
    requirements = "\n".join(f"• {value}" for value in item["requirements"])
    documents = "\n".join(f"• {value}" for value in item["documents"])
    text = (
        f"<b>{item['name']}</b>\n\n"
        f"<b>Ориентир:</b> {item['amount_note']}\n"
        f"<b>Категория:</b> {item['category']}\n\n"
        f"<b>Кому может подойти</b>\n{requirements}\n\n"
        f"<b>Что обычно проверяют</b>\n{documents}\n\n"
        f"<b>Куда обращаться:</b> {item['where_to_apply']}\n\n"
        "Проверьте точные условия и актуальные суммы на официальной странице по кнопке ниже."
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=detail_keyboard(item))


if __name__ == "__main__":
    logging.info("Starting Lgota.Bot")
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
