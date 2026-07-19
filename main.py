import telebot
import google.generativeai as genai
from telebot import types
import threading
import time
import io
from PIL import Image

# Token va API kalitlarni kiriting
TOKEN = 'SIZNING_BOT_TOKENINGIZ'
genai.configure(api_key='SIZNING_GEMINI_API_KEY')

bot = telebot.TeleBot(TOKEN)
model = genai.GenerativeModel('gemini-1.5-flash')

# 1. Foydalanuvchini saqlash (Suv eslatmasi uchun)
def save_user(chat_id):
    try:
        with open("users.txt", "a+") as f:
            f.seek(0)
            if str(chat_id) not in f.read():
                f.write(f"{chat_id}\n")
    except: pass

# 2. Avtomatik suv eslatmasi (har 2 soatda)
def send_water_reminders():
    while True:
        time.sleep(7200) # 2 soat
        try:
            with open("users.txt", "r") as f:
                users = set(f.readlines())
                for user_id in users:
                    bot.send_message(user_id.strip(), "💧 Trener buyrug'i: 2 soat o'tdi! Suv ichish vaqti bo'ldi! 5 litr limitni unutmadingmi?")
        except: pass

threading.Thread(target=send_water_reminders, daemon=True).start()

# 3. Asosiy menyu
@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🍎 Ratsion/Kaloriya", "💪 Trener Maslahati")
    bot.send_message(message.chat.id, "Salom! Men sening shaxsiy AI fitness treneringman. Maqsading nima?", reply_markup=markup)

# 4. AI Vision (Ovqat tahlili)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⏳ Trener ovqatni tekshirmoqda...")
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    image = {'mime_type': 'image/jpeg', 'data': downloaded_file}
    response = model.generate_content(["Sen qattiqqo'l fitness trenerisan. Bu ovqatni tahlil qil: kaloriyasi, foydasi va qancha yeyish kerakligi bo'yicha ayovsiz maslahat ber.", image])
    bot.reply_to(message, response.text)

# 5. Trener maslahati
@bot.message_handler(func=lambda message: message.text == "💪 Trener Maslahati")
def coach_advice(message):
    response = model.generate_content("Fitness bo'yicha qisqa, motivatsion va juda qattiqqo'l trener maslahati ber.")
    bot.send_message(message.chat.id, f"🔥 Trener: {response.text}")

bot.polling()
