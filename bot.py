import os
from flask import Flask, request
import telebot

# ==========================================
# НАСТРОЙКИ
# ==========================================
TOKEN = "8712123830:AAFM9v0-mlHTiHPD_Xbub3aJe8MLEVD5SdA"
# Укажите ссылку на ваш проект на Render без слеша на конце!
# Пример: "https://my-vin-bot.onrender.com"
RENDER_URL = "https://carrbott.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(_name_)


# ==========================================
# ВЕБ-СЕРВЕР И ПРИЕМ СООБЩЕНИЙ ОТ TELEGRAM
# ==========================================
@app.route("/")
def home():
  return "Bot is alive and working via Webhook!", 200


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
  """Этот маршрут принимает сообщения от Telegram"""
  if request.headers.get("content-type") == "application/json":
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "", 200
  else:
    return "Forbidden", 403


# ==========================================
# ЛОГИКА БОТА (генерация VIN)
# ==========================================
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "Привет! 🚘\nОтправь мне VIN-код машины, и я сгенерирую коды активации.",
  )


@bot.message_handler(func=lambda message: True)
def handle_vin(message):
  vin = message.text.strip().upper()

  if len(vin) < 6:
    bot.reply_to(
        message,
        "❌ Ошибка: VIN-код слишком короткий (нужно минимум 6 символов).",
    )
    return

  try:
    last6 = vin[-6:]
    d1 = last6[0]
    d2 = last6[1]
    d3 = last6[2]
    d4 = last6[3]
    d5 = last6[4]
    d6 = last6[5]

    part1 = f"{d1}{d4}0{d3}{d6}"
    part2 = f"{d2}{d5}"

    code1 = f"{part1}1{part2}"
    code2 = f"{part1}2{part2}"
    code3 = f"{part1}0{part2}"

    response_text = (
        f"🚘 <b>VIN:</b> {vin}\n\n"
        f"🔑 <b>Возможные пароли активации:</b>\n"
        f"1. <code>{code1}</code>\n"
        f"2. <code>{code2}</code>\n"
        f"3. <code>{code3}</code>"
    )

    bot.reply_to(message, response_text, parse_mode="HTML")

  except Exception as e:
    bot.reply_to(message, f"❌ Произошла ошибка при расчете: {e}")


# ==========================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ==========================================
if _name_ == "_main_":
  # Сбрасываем старый вебхук и устанавливаем новый
  bot.remove_webhook()
  bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")

  # Запускаем Flask на порту Render
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
