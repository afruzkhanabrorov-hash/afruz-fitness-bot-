import os
import telebot
from telebot import types

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

FOOD_BASE = {
    "Tovuq filesi": {"kcal": 165, "p": 31, "c": 0, "f": 3.6},
    "Mol go'shti (yog'siz)": {"kcal": 250, "p": 26, "c": 0, "f": 15},
    "Tuxum (1 dona - ~50g)": {"kcal": 70, "p": 6, "c": 0.5, "f": 5},
    "Baliq": {"kcal": 120, "p": 20, "c": 0, "f": 4},
    "Guruch (quruq)": {"kcal": 360, "p": 7, "c": 79, "f": 1},
    "Grechka (quruq)": {"kcal": 343, "p": 13, "c": 72, "f": 3.3},
    "Suli yormasi (Ovsyanka)": {"kcal": 389, "p": 16.9, "c": 66, "f": 6.9},
    "Kartoshka": {"kcal": 77, "p": 2, "c": 17, "f": 0.1},
    "Tvorog 5%": {"kcal": 121, "p": 17, "c": 3, "f": 5},
    "Sut 2.5%": {"kcal": 52, "p": 3, "c": 4.7, "f": 2.5},
    "Yong'oq (Greciya)": {"kcal": 654, "p": 15, "c": 14, "f": 65},
    "Bodom": {"kcal": 579, "p": 21, "c": 22, "f": 50}
}

user_data = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [types.KeyboardButton(food) for food in FOOD_BASE.keys()]
    markup.add(*buttons)
    bot.send_message(
        message.chat.id, 
        f"Salom Afruz! **AFRUZ FITNESS** botiga xush kelibsiz.\n\nHisoblamoqchi bo'lgan mahsulotingizni tanlang:", 
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.text in FOOD_BASE)
def food_selected(message):
    food_name = message.text
    user_data[message.chat.id] = food_name
    hide_markup = types.ReplyKeyboardRemove()
    bot.send_message(
        message.chat.id, 
        f"⚡️ **{food_name}** tanlandi.\nNecha gramm yedingiz? (Faqat raqam kiriting, masalan: 150)",
        reply_markup=hide_markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.chat.id in user_data)
def calculate_macros(message):
    chat_id = message.chat.id
    food_name = user_data[chat_id]
    try:
        grams = float(message.text)
        if grams <= 0:
            bot.send_message(chat_id, "Iltimos, 0 dan katta raqam kiriting.")
            return
        base = FOOD_BASE[food_name]
        factor = grams / 100.0
        kcal = round(base["kcal"] * factor, 1)
        p = round(base["p"] * factor, 1)
        c = round(base["c"] * factor, 1)
        f = round(base["f"] * factor, 1)
        
        result = (
            f"📊 **Natija ({grams}g {food_name}):**\n\n"
            f"🔥 **Kaloriya:** {kcal} kkal\n"
            f"🥩 **Oqsil (Protein):** {p} g\n"
            f"🌾 **Uglevod:** {c} g\n"
            f"🥑 **Yog':** {f} g\n\n"
            f"Keyingi mahsulot uchun /start buyrug'ini bosing."
        )
        bot.send_message(chat_id, result, parse_mode="Markdown")
        del user_data[chat_id]
    except ValueError:
        bot.send_message(chat_id, "Iltimos, faqat raqam yuboring.")

print("Bot ishga tushdi...")
bot.infinity_polling()




