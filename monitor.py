import telebot
import requests
import time
import os
from threading import Thread
from telebot import types
from datetime import datetime 

# --- SOZLAMALAR ---
# Sozlamalar
TOKEN = '8603403846:AAF1E-6UV0uoMV83aC2tIvsRWaAdYl-YrJw'
URL = "https://openbudget.uz/api/v2/info/initiative/count/9e041ec6-6c70-4b37-9053-02fc53f0f2e9"
USER_FILE = "bot_users.txt"

bot = telebot.TeleBot(TOKEN)

# --- FUNKSIYALAR ---

def get_current_votes():
    """Saytdan joriy ovozlar sonini olish"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        print(URL)
        response = requests.get(URL, timeout=20)
        if response.status_code == 200:
            data = response.json()
            return data.get('count')
        return None
    except:
        return None
def get_now():
    """Hozirgi vaqtni chiroyli formatda olish"""
    return datetime.now().strftime("%H:%M:%S")

def save_user(user_id):
    """Yangi foydalanuvchini faylga saqlash"""
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f: pass
    
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(str(user_id) + "\n")

# --- BOT BUYRUQLARI ---

@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id)
    
    # Tugma yaratish
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("📊 Ovozlar sonini bilish")
    markup.add(btn)
    
    welcome_text = (
        "👋 Assalomu alaykum!\n\n"
        "Open Budget monitoring botiga xush kelibsiz.\n"
        "Ovozlar o'zgarganda sizga xabar yuborib turaman.\n\n"
        "Hozirgi holatni bilish uchun quyidagi tugmani bosing:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📊 Ovozlar sonini bilish")
def manual_check(message):
    bot.send_chat_action(message.chat.id, 'typing')
    votes = get_current_votes()
    
    if votes is not None:
        xabar = f"✅ **Hozirgi ovozlar soni:!**\n\n" \
                    f"🔢 Jami: {votes}\n" \
                    f"🕒 Vaqt: {get_now()}"
            
        bot.reply_to(message, f"`{xabar}`", parse_mode="Markdown")
        
    else:
        bot.reply_to(message, "⚠️ Sayt hozircha javob bermayapti. Birozdan so'ng qayta urining.")

# --- AVTOMATIK MONITORING (Alohida oqimda) ---

def auto_monitor():
    last_votes = 0
    while True:
        current_votes = get_current_votes()
        
        if current_votes is not None:
            current_votes = int(current_votes)
            if current_votes != last_votes and last_votes != 0:
                diff = current_votes - last_votes
                msg = f"🔔 **Yangi ovozlar qo'shildi!**\n\n📊 Jami: `{current_votes}`\n📈 O'zgarish: `+{diff}`"
                
                # Barcha foydalanuvchilarga yuborish
                if os.path.exists(USER_FILE):
                    with open(USER_FILE, "r") as f:
                        users = f.read().splitlines()
                        for user_id in users:
                            try:
                                bot.send_message(user_id, msg, parse_mode="Markdown")
                            except: pass
                
                last_votes = current_votes
            elif last_votes == 0:
                last_votes = current_votes
        
        time.sleep(60) # Har 1 daqiqada tekshirish

# --- ISHGA TUSHIRISH ---

if __name__ == "__main__":
    # Avtomatik monitoringni orqa fonda boshlash
    Thread(target=auto_monitor, daemon=True).start()
    print("Bot va Monitoring ishga tushdi...")
    bot.infinity_polling()
