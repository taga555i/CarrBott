import os
import threading
from flask import Flask
import telebot

# ==========================================
# 1. ВЕБ-СЕРВЕР ДЛЯ RENDER (чтобы не было ошибки портов)
# ==========================================
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is alive!", 200


def run_flask():
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)


# Запускаем Flask в фоновом потоке
threading.Thread(target=run_flask, daemon=True).start()


# ==========================================
# 2. ВАШ КОД БОТА (генерация VIN)
# ==========================================
TOKEN = (
    "8712123830:AAFM9v0-mlHTiHPD_Xbub3aJe8MLEVD5SdA"  # Убедитесь, что здесь указан ваш реальный токен
)

bot = telebot.TeleBot(TOKEN)


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
    # Точный алгоритм из вашего v7-KeyGen.bat
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

    # Формируем красивый ответ с тремя вариантами
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


# Запуск бота
if __name__ == "__main__":
  print("🚀 Бот успешно запущен и работает по алгоритму v7-KeyGen!")
  bot.infinity_polling()
