import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
import requests

TOKEN = "7953800384:AAGUF3MW1H_zlT3gTOjvyUBX9bxMvNCO5l4"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Lokal kitoblar ro'yxati
books = [
    "Ufq – Cho‘lpon",
    "Mehrobdan chayon – Pirimqul Qodirov",
    "Ikki eshik orasi – O‘tkir Hoshimov",
    "Dunyoning ishlari – O‘tkir Hoshimov",
    "Qorako‘z Majnun – Erkin Vohidov"
]

def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📚 Kitob qidirish"), KeyboardButton("ℹ️ Bot haqida"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📓 Istalgan kitobingizni topib beradgan bot!\n\n"
                              "Iltimos, menyudan tanlang:", reply_markup=get_main_menu())

@bot.message_handler(func=lambda msg: msg.text == "ℹ️ Bot haqida")
def about(message):
    bot.send_message(message.chat.id,
                     "Bu bot orqali siz O‘zbek adabiyotiga oid kitoblarni tezda topishingiz mumkin.\n"
                     "Agar kitob chiqmasa, demak bazamizga qo‘shilmagan!")

@bot.message_handler(func=lambda msg: msg.text == "📚 Kitob qidirish")
def ask_book(message):
    bot.send_message(message.chat.id, "Qidirayotgan kitob nomini kiriting:")

def search_online_books(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    try:
        response = requests.get(url)
        data = response.json()
        results = []
        for item in data.get("items", []):
            title = item["volumeInfo"].get("title", "Noma'lum kitob")
            authors = item["volumeInfo"].get("authors", ["Muallif noma'lum"])
            results.append(f"{title} - {', '.join(authors)}")
        return results
    except Exception:
        return []

@bot.message_handler(func=lambda msg: True)
def search_book(message):
    text = message.text.lower()
    found = [book for book in books if text in book.lower()]
    online_found = search_online_books(text) if not found else []

    if found:
        reply = "🔍 Bazadan topilgan kitoblar:\n\n" + "\n".join(f"• {b}" for b in found)
        if online_found:
            reply += "\n\n🌐 Internetdan topilgan kitoblar:\n" + "\n".join(f"• {b}" for b in online_found[:5])
    elif online_found:
        reply = "🌐 Internetdan topilgan kitoblar:\n" + "\n".join(f"• {b}" for b in online_found[:5])
    else:
        reply = "😔 Afsuski, bu kitob bazamizda ham internetda topilmadi."

    bot.send_message(message.chat.id, reply)

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    # Bu yerga o'zingizning deploy qilingan URL manzilingizni qo'ying:
    bot.set_webhook(url="https://SIZNING_APP_MANZILINGIZ/")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
