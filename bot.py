import os
import requests
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from keep_alive import keep_alive
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# Reply Keyboard
reply_keyboard = [
    [KeyboardButton("🎬 DOWNLOAD VIDEO")],
    [KeyboardButton("👨‍💻 DEVELOPER INFO")]
]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 হ্যালো {user.mention_html()}!\n\n"
        "📥 *TikTok Downloader Bot* এ স্বাগতম 🎉\n\n"
        "👉 এখানে আপনি সহজেই TikTok ভিডিও ডাউনলোড করতে পারবেন:\n"
        "   • Without Watermark\n"
        "   • HD Quality Video\n"
        "   • MP3 Audio\n\n"
        "✨ CREATED BY @Swygen_bd"
    )
    await update.message.reply_html(welcome_text, reply_markup=markup)

# Handle DOWNLOAD VIDEO / DEVELOPER INFO / Links
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # DOWNLOAD VIDEO button
    if text == "🎬 DOWNLOAD VIDEO":
        await update.message.reply_text(
            "🔗 অনুগ্রহ করে একটি *TikTok ভিডিও লিংক* পাঠান…",
            parse_mode="Markdown"
        )
        return

    # If user sends TikTok link
    if text.startswith("http"):
        await update.message.reply_text("⏳ অনুগ্রহ করে অপেক্ষা করুন, ভিডিও প্রসেস করা হচ্ছে…")

        url = f"https://tiktok-video-no-watermark2.p.rapidapi.com/video/url?url={text}"
        headers = {
            "x-rapidapi-host": "tiktok-video-no-watermark2.p.rapidapi.com",
            "x-rapidapi-key": RAPIDAPI_KEY
        }

        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            if "data" not in data:
                await update.message.reply_text("❌ ভিডিও পাওয়া যায়নি বা API বর্তমানে কাজ করছে না।")
                return

            no_watermark = data["data"].get("no_watermark")
            hd = data["data"].get("hd")
            audio = data["data"].get("audio")

            msg = "✅ *ডাউনলোড অপশন সমূহ:*\n\n"
            if no_watermark:
                msg += f"🔹 [Without Watermark Video]({no_watermark})\n"
            if hd:
                msg += f"🔹 [HD Quality Video]({hd})\n"
            if audio:
                msg += f"🔹 [MP3 Audio Download]({audio})\n"

            await update.message.reply_markdown(msg)

        except Exception as e:
            await update.message.reply_text("⚠️ কোনো সমস্যা হয়েছে। আবার চেষ্টা করুন।")
            print("Error:", e)

    # Developer Info
    elif text == "👨‍💻 DEVELOPER INFO":
        info = (
            "💡 *Bot Information:*\n\n"
            "এই বটের মাধ্যমে আপনি TikTok ভিডিও ডাউনলোড করতে পারবেন:\n"
            "   • Without Watermark\n"
            "   • HD Quality\n"
            "   • MP3 Format\n\n"
            "🚀 দ্রুত, নিরাপদ এবং সহজ ব্যবহারযোগ্য।\n\n"
            "✨ CREATED BY @Swygen_bd"
        )
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("📩 Contact Developer", url="https://t.me/Swygen_bd")]]
        )
        await update.message.reply_markdown(info, reply_markup=keyboard)

# Run the bot
def main():
    keep_alive()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
