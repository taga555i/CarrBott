import os
from flask import Flask, request
import telebot

# ==========================================
# НАСТРОЙКИ
# ==========================================
TOKEN = "8712123830:AAFM9v0-mIHTiHPD_Xbub3aJe8MLEVD5SdQ"
RENDER_URL = "https://carrbott.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# Принудительно устанавливаем вебхук при старте Flask
with app.app_context():
  try:
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    print("Webhook successfully set!")
  except Exception as e:
    print(f"Error setting webhook: {e}")


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
      "Привет! 🚘\nОтправь мне VIN-код машины, и я сгенерирую код активации.",
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

    # 3-я цифра заменена на '1'
    part1 = f"{d1}{d4}1{d3}{d6}"
    part2 = f"{d2}{d5}"

    # Оставляем только один итоговый вариант в самом низу
    code = f"{part1}0{part2}"

    response_text = (
        f"🚘 <b>VIN:</b> {vin}\n\n"
        f"🔑 <b>Пароль активации:</b>\n"
        f"<code>{code}</code>"
    )

    bot.reply_to(message, response_text, parse_mode="HTML")

  except Exception as e:
    bot.reply_to(message, f"❌ Произошла ошибка при расчете: {e}")


# ==========================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ==========================================
if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
