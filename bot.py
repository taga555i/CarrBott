import logging
import os
from flask import Flask, request
import telebot

# Включаем логирование, чтобы видеть всё в консоли Render
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

TOKEN = "8817276619:AAEvkaK2sYE_R1NtzhWj74SsYSEFI1MDnVM"
RENDER_URL = "https://carrbott.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is alive and working via Webhook!", 200


@app.route("/webhook", methods=["POST"])
def webhook():
  logging.info("Получен запрос от Telegram в вебхук!")
  if request.headers.get("content-type") == "application/json":
    json_string = request.get_data().decode("utf-8")
    try:
      update = telebot.types.Update.de_json(json_string)
      bot.process_new_updates([update])
      logging.info("Обновление успешно обработано ботом.")
    except Exception as e:
      logging.error(f"Ошибка при обработке обновления: {e}")
    return "", 200
  else:
    logging.warning("Получен запрос с неверным content-type")
    return "Forbidden", 403


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  logging.info(f"Команда /start получена от пользователя {message.chat.id}")
  bot.reply_to(
      message,
      "Привет! 🚘\nОтправь мне VIN-код машины, и я сгенерирую код активации.",
  )


@bot.message_handler(func=lambda message: True)
def handle_vin(message):
  logging.info(f"Получен текст: {message.text}")
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

    # Оставляем ровно один итоговый вариант в самом низу
    code = f"{part1}0{part2}"

    response_text = (
        f"🚘 <b>VIN:</b> {vin}\n\n"
        f"🔑 <b>Пароль активации:</b>\n"
        f"<code>{code}</code>"
    )

    bot.reply_to(message, response_text, parse_mode="HTML")
    logging.info(f"Успешно отправлен ответ для VIN: {vin}")

  except Exception as e:
    logging.error(f"Ошибка при расчете VIN: {e}")
    bot.reply_to(message, f"❌ Произошла ошибка при расчете: {e}")


if __name__ == "__main__":
  # Устанавливаем вебхук прямо перед запуском сервера
  try:
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/webhook")
    print("Webhook successfully set to /webhook!")
  except Exception as e:
    print(f"Error setting webhook: {e}")

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
