import os
import requests
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- WEB SERVER FOR RENDER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- CONFIG ---
BOT_TOKEN = os.environ.get('8637306574:AAEsbT1MsJB4Q_IVMkAR8_ZnJISt9oQ9wP4')
HF_TOKEN = os.environ.get('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')
API_URL = "https://api-inference.huggingface.co/models/sczhou/CodeFormer"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ Processing...")
    try:
        photo_file = await update.message.photo[-1].get_file()
        input_path = "temp_in.jpg"
        await photo_file.download_to_drive(input_path)
        
        with open(input_path, "rb") as f:
            response = requests.post(API_URL, headers=headers, data=f.read(), timeout=120)

        if response.status_code == 200:
            output_path = "temp_out.png"
            with open(output_path, "wb") as f: f.write(response.content)
            await update.message.reply_photo(photo=open(output_path, "rb"))
            os.remove(output_path)
        else:
            await update.message.reply_text(f"Error: {response.status_code}")
    except Exception as e:
        await update.message.reply_text("Connection Slow. Try Again.")
    if os.path.exists(input_path): os.remove(input_path)

if __name__ == '__main__':
    # Start Web Server
    Thread(target=run).start()
    # Start Bot
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Cloud Bot Started...")
    bot_app.run_polling()

