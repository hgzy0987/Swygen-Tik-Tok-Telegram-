#!/usr/bin/env python3
# bot.py

import logging
import tempfile
import requests
import yt_dlp
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
)
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackQueryHandler, ConversationHandler, CallbackContext
)
from keep_alive import keep_alive

# ========= FIXED TOKENS =========
BOT_TOKEN = "8229272037:AAFm-TulEar5Zoa0KCVR-QybnizmCWcU0qY"
RAPIDAPI_KEY = "1cb3246d70msh6ed8addcd1e333ap1f9eaajsnb3b89d5ec2b5"

# ========= LOGGING =========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

WAIT_LINK = 1

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("Download Video"), KeyboardButton("Developer Contact")]],
    resize_keyboard=True
)

# ========= START =========
def start(update: Update, context: CallbackContext):
    name = update.effective_user.first_name or "বন্ধু"
    text = (
        f"✨ স্বাগতম, *{name}*!\n\n"
        "এটি *SSS TIK TOK DOWNLOAD BOT* 🚀\n\n"
        "TikTok ভিডিও ডাউনলোড করুন — HD, Without Watermark বা MP3 ফরম্যাটে।"
    )
    update.message.reply_text(text, reply_markup=MAIN_KEYBOARD, parse_mode=ParseMode.MARKDOWN)

# ========= DEV CONTACT =========
def developer_contact(update: Update, context: CallbackContext):
    text = (
        "👨‍💻 Developer: *Ayman Hasan Shaan*\n"
        "📩 Contact: @Swygen_bd\n"
        "🌐 Website: https://swygen.netlify.app"
    )
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=MAIN_KEYBOARD)

# ========= ASK LINK =========
def download_video_request(update: Update, context: CallbackContext):
    update.message.reply_text("🎬 TikTok ভিডিও লিঙ্ক দিন:", reply_markup=None)
    return WAIT_LINK

# ========= HANDLE LINK =========
def handle_link(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    if not url.startswith("http"):
        update.message.reply_text("❌ সঠিক একটি URL দিন।", reply_markup=MAIN_KEYBOARD)
        return ConversationHandler.END

    context.user_data['last_url'] = url
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("HD Video", callback_data="opt_hd")],
        [InlineKeyboardButton("Without Watermark", callback_data="opt_nowm")],
        [InlineKeyboardButton("MP3 (Audio)", callback_data="opt_mp3")],
    ])
    update.message.reply_text("✅ লিঙ্ক পাওয়া গেছে!\nকোন ফরম্যাট চান?", reply_markup=kb)
    return ConversationHandler.END

# ========= YTDLP DOWNLOAD =========
def download_with_ydl(url, outdir, format_str):
    ydl_opts = {
        "outtmpl": f"{outdir}/%(id)s.%(ext)s",
        "format": format_str,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return info

# ========= RAPIDAPI CALL =========
def get_no_watermark_url(tiktok_url):
    url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
    querystring = {"url": tiktok_url, "hd": "1"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
    }
    resp = requests.get(url, headers=headers, params=querystring, timeout=20)
    data = resp.json()
    if "data" in data and "play" in data["data"]:
        return data["data"]["play"]
    elif "data" in data and "wmplay" in data["data"]:
        return data["data"]["wmplay"]
    return None

# ========= CALLBACK =========
def callback_query_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    url = context.user_data.get('last_url')
    chat_id = update.effective_chat.id

    if not url:
        query.message.reply_text("❌ প্রথমে Download Video চাপুন।")
        return

    query.message.reply_text("⏳ Processing...")

    try:
        with tempfile.TemporaryDirectory() as td:
            if data == "opt_hd":
                download_with_ydl(url, td, "best")
                file = os.listdir(td)[0]
                context.bot.send_video(chat_id, video=open(f"{td}/{file}", "rb"))

            elif data == "opt_nowm":
                dl_url = get_no_watermark_url(url)
                if not dl_url:
                    query.message.reply_text("❌ No-watermark লিংক পাওয়া যায়নি।")
                    return
                resp = requests.get(dl_url, stream=True)
                file_path = f"{td}/no_wm.mp4"
                with open(file_path, "wb") as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
                context.bot.send_video(chat_id, video=open(file_path, "rb"))

            elif data == "opt_mp3":
                ydl_opts = {
                    "outtmpl": f"{td}/%(id)s.%(ext)s",
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }]
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(url, download=True)
                file = [f for f in os.listdir(td) if f.endswith(".mp3")][0]
                context.bot.send_audio(chat_id, audio=open(f"{td}/{file}", "rb"))

        query.message.reply_text("✅ ডাউনলোড সম্পন্ন!", reply_markup=MAIN_KEYBOARD)

    except Exception as e:
        logger.exception("Error")
        query.message.reply_text(f"❌ সমস্যা: {e}", reply_markup=MAIN_KEYBOARD)

# ========= CANCEL =========
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("বাতিল করা হলো।", reply_markup=MAIN_KEYBOARD)
    return ConversationHandler.END

# ========= MAIN =========
def main():
    keep_alive()
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex("^Developer Contact$"), developer_contact))
    dp.add_handler(MessageHandler(Filters.regex("^Download Video$"), download_video_request))

    conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("^Download Video$"), download_video_request)],
        states={WAIT_LINK: [MessageHandler(Filters.text & ~Filters.command, handle_link)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv)
    dp.add_handler(CallbackQueryHandler(callback_query_handler))
    dp.add_handler(MessageHandler(Filters.entity("url") | Filters.regex(r"https?://"), handle_link))

    updater.start_polling()
    logger.info("Bot started 🚀")
    updater.idle()

if __name__ == "__main__":
    main()
