# ✅ TO‘LIQ TELEGRAM REKLAMA BOTI - RAILWAY UCHUN
# Fayl: main.py

import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from fpdf import FPDF
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("7620186002:AAEOKCs5i3uwS__j6Iwg3KvfqDkEzmbKDOc")
bot = telebot.TeleBot(TOKEN)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
spreadsheet = client.open("reklama")

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

def clean_text(text):
    replace_map = {'o‘': "o'", 'g‘': "g'", 'O‘': "O'", 'G‘': "G'", 'ў': "o'", 'қ': "q", 'ҳ': "h", 'ё': "yo", 'ш': "sh", 'ғ': "g'"}
    for k, v in replace_map.items():
        text = text.replace(k, v)
    return ''.join(c if ord(c) < 128 else '-' for c in text)

@bot.message_handler(commands=['start'])
def start_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🟢 Buyurtma", "📤 Qarzni yopish", "📊 Kunlik tushum", "📄 Chek olish")
    bot.send_message(message.chat.id, "Assalomu alaykum. Tanlang:", reply_markup=markup)

# ... KODNING QOLGAN QISMI AVVALGI HOLATDA QOLADI ...

print("Bot ishga tushdi...")
bot.polling(non_stop=True)
