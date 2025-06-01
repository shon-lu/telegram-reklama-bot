# Reklama Telegram botining to‘liq funksional kodi (Railway uchun)

import telebot
import json
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from fpdf import FPDF
import os
from flask import Flask, request

# Token va Webhook konfiguratsiyasi
TOKEN = "8083606281:AAGh0eRUDablA_K-TlXhI6sCzwjdPnYAMWQ"
bot = telebot.TeleBot(TOKEN)
WEBHOOK_URL = "https://telegram-reklama-bot-production.up.railway.app/"

# Google Sheets ulanishi
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
client = gspread.authorize(creds)
spreadsheet = client.open("reklama")

# Foydalanuvchilar va filiallarga bog‘lash
user_filials = {
    3404866775: "Admin",
    1854573770: "Juydam",
    925139085: "Muhayyo",
    7210982662: "Namangan",
    7031729411: "Tekstil"
}

fields = [
    "Mijoz ismi", "Proekt nomi", "Telefon raqami", "Adres",
    "Buyurtma turi", "Oʻlcham yoki miqdori", "Kelishuv summasi",
    "Avans", "Muddati", "Izoh", "Menejer ismi"
]

user_sessions = {}
debt_search_results = {}

# Matnni tozalash

def clean_text(text):
    replace_map = {'o‘': "o'", 'g‘': "g'", 'O‘': "O'", 'G‘': "G'", 'ў': "o'", 'қ': "q", 'ҳ': "h", 'ё': "yo", 'ш': "sh", 'ғ': "g'"}
    for k, v in replace_map.items():
        text = text.replace(k, v)
    return ''.join(c if ord(c) < 128 else '-' for c in text)

# Start komandasi
@bot.message_handler(commands=['start'])
def start_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🟢 Buyurtma", "📤 Qarzni yopish", "📊 Kunlik tushum", "📄 Chek olish")
    bot.send_message(message.chat.id, "Assalomu alaykum. Tanlang:", reply_markup=markup)

# Buyurtma boshlanishi
@bot.message_handler(func=lambda msg: msg.text == "🟢 Buyurtma")
def buyurtma_start(message):
    user_sessions[message.chat.id] = {"step": 0, "data": {}}
    ask_next_field(message)

# Har bir maydonni so‘rash
@bot.message_handler(func=lambda msg: msg.chat.id in user_sessions)
def handle_form_input(message):
    session = user_sessions[message.chat.id]
    current_step = session["step"]
    session["data"][fields[current_step]] = message.text
    session["step"] += 1

    if session["step"] < len(fields):
        ask_next_field(message)
    else:
        preview_and_confirm(message)

def ask_next_field(message):
    step = user_sessions[message.chat.id]["step"]
    bot.send_message(message.chat.id, f"{fields[step]}:")

def preview_and_confirm(message):
    data = user_sessions[message.chat.id]["data"]
    text = "✅ Buyurtma ma'lumotlari:\n"
    for field in fields:
        text += f"<b>{field}:</b> {data[field]}\n"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Saqlash", callback_data="save_order"))
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "save_order")
def save_order(call):
    data = user_sessions[call.message.chat.id]["data"]
    data_row = [datetime.now().strftime("%d.%m.%Y %H:%M")] + [data.get(f, "") for f in fields] + [user_filials.get(call.from_user.id, "")] + [data["Kelishuv summasi"] + " - " + data["Avans"]]
    sheet = spreadsheet.sheet1
    sheet.append_row(data_row)
    send_pdf_check(call.message.chat.id, data)
    bot.send_message(call.message.chat.id, "✅ Buyurtma saqlandi!")
    del user_sessions[call.message.chat.id]

def send_pdf_check(chat_id, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reklama markazi", ln=True, align="C")
    pdf.ln(5)
    for f in fields:
        pdf.cell(0, 10, txt=f"{f}: {data[f]}", ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, txt="Tasdiqlayman: __________", ln=True)
    filename = f"check_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    with open(filename, 'rb') as f:
        bot.send_document(chat_id, f, caption="Buyurtma uchun chek")
    os.remove(filename)

# Flask server (Railway uchun)
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + TOKEN)
    return "Bot ishga tayyor.", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
