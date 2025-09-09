import os
import requests
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from keep_alive import keep_alive

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 Hello {user.mention_html()}!\n\n"
        "✨ Welcome to <b>TikTok Downloader Bot</b>\n\n"
        "📌 Features:\n"
        "➡️ Download Without Watermark\n"
        "➡️ Download HD Video\n"
        "➡️ Extract MP3 Audio\n\n"
        "🚀 CREATED BY @Swygen_bd"
    )
    keyboard = [["📥 DOWNLOAD VIDEO", "👨‍💻 DEVELOPER INFO"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_html(welcome_text, reply_markup=reply_markup)

# ---------- HANDLE MESSAGES ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # DOWNLOAD VIDEO
    if text == "📥 DOWNLOAD VIDEO":
        await update.message.reply_text("🔗 Please send me a TikTok video link to download.")
        return

    # DEVELOPER INFO
    if text == "👨‍💻 DEVELOPER INFO":
        info = (
            "👨‍💻 <b>Developer Info</b>\n\n"
            "This bot allows you to download TikTok videos:\n"
            "➡️ Without Watermark\n"
            "➡️ HD Video\n"
            "➡️ MP3 Audio\n\n"
            "🚀 CREATED BY @Swygen_bd"
        )
        keyboard = [[InlineKeyboardButton("📩 Contact Developer", url="https://t.me/Swygen_bd")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_html(info, reply_markup=reply_markup)
        return

    # TikTok Link Processing
    if "tiktok.com" in text:
        await update.message.reply_text("⏳ Fetching video links, please wait...")

        url = f"https://tiktok-video-no-watermark2.p.rapidapi.com/video/url?url={text}"
        headers = {
            "x-rapidapi-host": "tiktok-video-no-watermark2.p.rapidapi.com",
            "x-rapidapi-key": RAPIDAPI_KEY
        }

        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            if "data" not in data:
                await update.message.reply_text("❌ Video not found or API error.")
                return

            no_wm = data["data"].get("no_watermark")
            hd = data["data"].get("hd")
            audio = data["data"].get("audio")

            msg = "<b>✅ Download Options:</b>\n\n"
            if no_wm:
                msg += f"🎥 <a href='{no_wm}'>Without Watermark</a>\n"
            if hd:
                msg += f"🎥 <a href='{hd}'>HD Video</a>\n"
            if audio:
                msg += f"🎵 <a href='{audio}'>MP3 Audio</a>\n"

            await update.message.reply_html(msg)
        except Exception as e:
            await update.message.reply_text("⚠️ Something went wrong. Please try again.")
            print("Error:", e)

# ---------- MAIN ----------
def main():
    keep_alive()  # Start Flask server for Render + Uptime Robot
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
