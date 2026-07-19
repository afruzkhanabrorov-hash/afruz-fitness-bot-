import telebot
import google.generativeai as genai
from PIL import Image
import io

# API kalitlarni o'zingizniki bilan almashtiring
TOKEN = 'SIZNING_BOT_TOKENINGIZ'
genai.configure(api_key='SIZNING_GEMINI_API_KEY')

bot = telebot.TeleBot(TOKEN)
model = genai.GenerativeModel('gemini-1.5-flash')

# 1. Rasm va ovqat tahlili (Vision)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "⏳ Tahlil qilinmoqda...")
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image = Image.open(io.BytesIO(downloaded_file))
        
        response = model.generate_content([
            "Sen qattiqqo'l fitness murabbiyisan. Bu rasmdagi ovqatni tahlil qil: kaloriyasini ayt, sog'lommi yoki yo'q, va qancha yeyish kerakligini maslahat ber. Ayovsiz bo'l!", 
            image
        ])
        
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Xatolik yuz berdi: {e}")

# 2. Ayovsiz trener maslahati (Matnli)
@bot.message_handler(commands=['maslahat'])
def coach_advice(message):
    prompt = "Sen qattiqqo'l trenerdan. Fitness va sog'lom turmush tarzi bo'yicha qisqa va qattiq motivatsion maslahat ber."
    response = model.generate_content(prompt)
    bot.send_message(message.chat.id, f"🔥 Trener deydi: {response.text}")

# 3. /start menyusi
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Men sening shaxsiy ayovsiz treneringman. Ovqatni rasmga olib yubor, tahlil qilaman!")

bot.polling()






