import telebot
import google.generativeai as genai
from telebot import types
import threading
import time

TOKEN = '8873515082:AAF-nJXFVtnxZnW_2xhtPUMkX2pRSHgL8qM'
genai.configure(api_key='AQ.Ab8RN6Ji6TPYHcMg_kdnzAeJvI7fARF-GPwTYrw_qq7AEZHOzg')

bot = telebot.TeleBot(TOKEN)
model = genai.GenerativeModel('gemini-1.5-flash')

# Suv ichishni eslatish funksiyasi (Har 2 soatda)
def water_reminder():
    while True:
        time.sleep(7200) 
        # Bu qismda baza bo'lmasa barcha foydalanuvchilarga yuborish qiyin, 
        # shuning uchun logikani bot ishga tushganda yuboradigan qildik.
        pass

threading.Thread(target=water_reminder, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🍎 Ratsion va Suv", "⚽️ Futbolchi/Atlet Plani", "🏠 Uy sharoiti (Mashq)", "🔥 Motivatsiya")
    bot.send_message(message.chat.id, "Salom! Men sening AI treneringman. Natural atlet va futbolchi sifatida maqsading nima?", reply_markup=markup)

# 1. Ratsion va Suv
@bot.message_handler(func=lambda message: message.text == "🍎 Ratsion va Suv")
def nutrition_plan(message):
    msg = bot.send_message(message.chat.id, "Vazningni (kg) va maqsadingni yoz (Masalan: 70kg, vazn olish/quritish).")
    bot.register_next_step_handler(msg, generate_diet)

def generate_diet(message):
    response = model.generate_content(f"Natural atlet va futbolchi uchun: {message.text}. Shu maqsadda bir kunlik ratsion va kuniga qancha suv ichish kerakligini (litrda) yozib ber.")
    bot.send_message(message.chat.id, f"🥗 Ratsioning:\n{response.text}\n\n💧 Esingda tut: Har 2 soatda bir stakan suv ichishni unutma!")

# 2. Futbolchi va Atlet Plani
@bot.message_handler(func=lambda message: message.text == "⚽️ Futbolchi/Atlet Plani")
def sports_plan(message):
    msg = bot.send_message(message.chat.id, "Pozitsiyangni yoz (Masalan: Hujumchi, Himoyachi yoki Atlet).")
    bot.register_next_step_handler(msg, generate_sports_plan)

def generate_sports_plan(message):
    response = model.generate_content(f"Sen professional murabbiysan. {message.text} uchun maxsus jismoniy tayyorgarlik va futbolga xos tezlik/chidamlilik planini tuzib ber.")
    bot.send_message(message.chat.id, f"📈 Sport planing:\n{response.text}")

# 3. Uy sharoitidagi mashqlar
@bot.message_handler(func=lambda message: message.text == "🏠 Uy sharoiti (Mashq)")
def home_workout(message):
    response = model.generate_content("Uy sharoitida top bilan, o'z vazning bilan va cho'zilish (stretching) mashqlarini o'z ichiga olgan kompleks dastur tuzib ber.")
    bot.send_message(message.chat.id, f"🏠 Uy sharoiti dasturi:\n{response.text}")

# 4. Motivatsiya
@bot.message_handler(func=lambda message: message.text == "🔥 Motivatsiya")
def motivation(message):
    response = model.generate_content("Natural atlet va futbolchi uchun juda qattiqqo'l, g'alabaga undaydigan motivatsiya ber.")
    bot.send_message(message.chat.id, f"🔥 Trener: {response.text}")

bot.infinity_polling()
