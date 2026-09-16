import os
from flask import Flask, render_template_string

app = Flask(__name__)
BOT_USERNAME = os.getenv("BOT_USERNAME", "LgotaInfo_bot")

PAGE = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Льгота.Бот — навигация по мерам поддержки</title>
  <meta name="description" content="Справочный Telegram-бот: помогает сориентироваться в возможных мерах поддержки и найти официальные страницы.">
  <style>
    :root { --bg:#101827; --card:#fff; --accent:#2878ff; --muted:#61708a; }
    * { box-sizing:border-box; } body { margin:0; font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif; color:#15213a; background:#f4f7fc; }
    .hero { background:radial-gradient(circle at top left,#3b82f6,#132040 67%); color:#fff; padding:76px 22px 100px; text-align:center; }
    .wrap { max-width:1040px; margin:auto; } h1 { font-size:clamp(2.2rem,6vw,4.4rem); line-height:1.04; margin:0 0 22px; } .lead { max-width:670px; margin:0 auto 30px; font-size:1.18rem; opacity:.92; }
    .button { display:inline-block; background:#fff; color:#175cd3; border-radius:12px; text-decoration:none; padding:15px 24px; font-weight:800; box-shadow:0 10px 30px #07112755; }
    main { max-width:1040px; margin:-54px auto 0; padding:0 22px 60px; } .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; } .card { background:#fff; border-radius:18px; padding:26px; box-shadow:0 10px 30px #17234012; } .card h2 { margin:0 0 10px; font-size:1.14rem; } .card p { margin:0; color:var(--muted); }
    section { margin-top:18px; } .wide { background:#fff; padding:34px; border-radius:18px; box-shadow:0 10px 30px #17234012; } ol { margin:16px 0 0; padding-left:21px; } li { padding:5px 0; color:#37445a; } .notice { border-left:4px solid #f59e0b; background:#fff8e7; padding:18px; border-radius:8px; margin-top:18px; color:#6b4c08; }
    footer { text-align:center; padding:30px; color:#64748b; font-size:.9rem; } @media(max-width:700px){.grid{grid-template-columns:1fr}.hero{padding-top:55px}.wide,.card{padding:22px}}
  </style>
</head>
<body>
  <header class="hero"><div class="wrap">
    <div>🎯 Льгота.Бот</div><h1>Понятная навигация по мерам поддержки</h1>
    <p class="lead">Ответьте на несколько вопросов в Telegram и получите предварительный список категорий льгот со ссылками на официальные источники.</p>
    <a class="button" href="https://t.me/{{ bot_username }}">Открыть бота в Telegram</a>
  </div></header>
  <main>
    <section class="grid">
      <article class="card"><h2>Без документов в чат</h2><p>Бот не просит паспорт, СНИЛС, реквизиты карты и фотографии документов.</p></article>
      <article class="card"><h2>Официальная проверка</h2><p>Каждая карточка ведёт на официальный ресурс для уточнения условий.</p></article>
      <article class="card"><h2>Регион имеет значение</h2><p>Суммы и правила часто различаются, поэтому результат носит справочный характер.</p></article>
    </section>
    <section class="wide"><h2>Как это работает</h2><ol><li>Откройте бота.</li><li>Ответьте на пять коротких вопросов.</li><li>Откройте предложенные карточки.</li><li>Проверьте актуальные условия на официальном сайте и подайте заявление через подходящий канал.</li></ol>
    <div class="notice">Информация не является юридической консультацией и не гарантирует назначение выплаты. Решение принимают уполномоченные органы.</div></section>
  </main>
  <footer>© Льгота.Бот · Справочный сервис</footer>
</body>
</html>"""

@app.get("/")
def index():
    return render_template_string(PAGE, bot_username=BOT_USERNAME)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
