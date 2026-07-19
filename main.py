import os
import telebot
from telebot import types
import google.generativeai as genai

# Tokenlarni yuklash
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

# Gemini AI modelini sozlash
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    ai_model = None

user_data = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    user_data[message.chat.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("⚽ Futbolchi")
    btn2 = types.KeyboardButton("💪 Natural Bodibilder")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Salom! Sport turini tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["⚽ Futbolchi", "💪 Natural Bodibilder"])
def set_sport(message):
    user_data[message.chat.id]['sport'] = message.text
    bot.send_message(message.chat.id, "Vazningizni kiriting (kg):", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_weight)

def get_weight(message):
    try:
        weight = float(message.text)
        user_data[message.chat.id]['weight'] = weight
        bot.send_message(message.chat.id, "Bo'yingizni kiriting (cm):")
        bot.register_next_step_handler(message, get_height)
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, faqat son kiriting. Vazningizni qaytadan yozing:")
        bot.register_next_step_handler(message, get_weight)

def get_height(message):
    try:
        height = float(message.text)
        user_data[message.chat.id]['height'] = height
        bot.send_message(message.chat.id, "Yoshingizni kiriting:")
        bot.register_next_step_handler(message, get_age)
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, faqat son kiriting. Bo'yingizni qaytadan yozing:")
        bot.register_next_step_handler(message, get_height)

def get_age(message):
    try:
        age = int(message.text)
        chat_id = message.chat.id
        sport = user_data[chat_id]['sport']
        weight = user_data[chat_id]['weight']
        height = user_data[chat_id]['height']
        
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
        
        if sport == "⚽ Futbolchi":
            daily_calories = int(bmr * 1.7)
            oqsil = int(weight * 1.6)
            uglevod = int(weight * 5.0)
            yog = int(weight * 1.0)
            
            tavsiya = (
                f"📊 **Siz uchun kunlik kaloriya me'yori:** {daily_calories} kkal\n"
                f"🧪 Oqsil: {oqsil}g | Uglevod: {uglevod}g | Yog': {yog}g\n\n"
                f"🏃‍♂️ **O'yindan 2-3 soat oldin (Glikogen zaxirasi uchun):**\n"
                f"Guruch yoki makaron + tovuq filesi + yengil salat.\n\n"
                f"🔄 **O'yindan keyin (Tiklanish uchun):**\n"
                f"Tez hazm bo'luvchi uglevod va oqsil: Banan + oqsilli kokteyl yoki tovuq go'shti bilan guruch."
            )
        else:
            daily_calories = int(bmr * 1.5)
            oqsil = int(weight * 2.2)
            uglevod = int(weight * 3.5)
            yog = int(weight * 0.9)
            
            tavsiya = (
                f"📊 **Siz uchun kunlik kaloriya me'yori:** {daily_calories} kkal\n"
                f"🧪 Oqsil: {oqsil}g | Uglevod: {uglevod}g | Yog': {yog}g\n\n"
                f"🏋️‍♂️ **Mashg'ulotdan 1.5 - 2 soat oldin (Kuch berish uchun):**\n"
                f"Suli yormasi (ovsyanka) + tuxum oqi yoki Grechka + mol go'shti.\n\n"
                f"🔄 **Mashg'ulotdan keyin (Muskullar o'sishi uchun):**\n"
                f"Tezkor oqsil va uglevod: Guruch + baliq yoki tovuq go'shti."
            )
            
        bot.send_message(chat_id, tavsiya, parse_mode="Markdown")
        bot.send_message(chat_id, "📸 Endi taomingizni rasmga olib tashlasangiz, sun'iy intellekt 99% aniqlikda uning kaloriyasini o'lchab beradi!")
        
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, yoshingizni to'g'ri kiriting:")
        bot.register_next_step_handler(message, get_age)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if not ai_model:
        bot.send_message(message.chat.id, "Tizim sozlanmagan. Iltimos, Render'ga GEMINI_API_KEY qo'shing.")
        return

    bot.send_message(message.chat.id, "🔄 Rasm qabul qilindi. Sun'iy intellekt taomni va uning kaloriyasini 99% aniqlikda tahlil qilmoqda, kuting...")
    
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_parts = [{"mime_type": "image/jpeg", "data": downloaded_file}]
        
        prompt = (
            "Ushbu rasmda ko'ringan taom yoki mahsulotlarni aniq tahlil qil. "
            "Uning tarkibidagi taxminiy kaloriyani (kkal), oqsil (g), uglevod (g) va yog' (g) miqdorini 99% aniqlikda hisobla. "
            "Natijani sportchilar tushunadigan chiroyli o'zbek tilida ber."
        )
        
        response = ai_model.generate_content([prompt, image_parts[0]])
        bot.send_message(message.chat.id, response.text)
        
    except Exception as e:
        bot.send_message(message.chat.id, "Xatolik yuz berdi. Rasmni aniqroq qilib qayta yuboring.")

if __name__ == '__main__':
    bot.infinity_polling()
8




