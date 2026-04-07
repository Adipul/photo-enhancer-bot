import os, requests, asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- WEB SERVER FOR KEEP-ALIVE ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Running!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- CONFIG ---
BOT_TOKEN = os.environ.get('8637306574:AAEsbT1MsJB4Q_IVMkAR8_ZnJISt9oQ9wP4')
HF_TOKEN = os.environ.get('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')
# Stable AI Model URL
API_URL = "https://api-inference.huggingface.co/models/google/real-esrgan-x2plus"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await update.message.reply_text("⏳ AI Model photo enhance kar raha hai...")
    try:
        photo_file = await update.message.photo[-1].get_file()
        input_path = "in.jpg"
        await photo_file.download_to_drive(input_path)
        
        with open(input_path, "rb") as f:
            response = requests.post(API_URL, headers=headers, data=f.read(), timeout=120)

        if response.status_code == 200:
            with open("out.png", "wb") as f: f.write(response.content)
            await update.message.reply_photo(photo=open("out.png", "rb"), caption="✅ Enhanced by Cloud Bot")
            os.remove("out.png")
        else:
            await update.message.reply_text(f"❌ Server Busy (Code: {response.status_code}). Thodi der baad try karein.")
    except Exception as e:
        await update.message.reply_text("⚠️ Connection lost. Retrying...")
    if os.path.exists(input_path): os.remove(input_path)

if __name__ == '__main__':
    Thread(target=run).start()
    bot = ApplicationBuilder().token(BOT_TOKEN).build()
    bot.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Cloud Bot Started Successfully!")
    bot.run_polling()
