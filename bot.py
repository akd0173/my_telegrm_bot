import os
import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Railway injects this automatically
BOT_TOKEN = os.getenv("8580858808:AAHJwQeXeQpGNa4jrg2WqMhhSfZP_XhbV4s")  # <-- MUST match Railway variable name

VIDEOS_JSON = "videos.json"


def load_videos():
    try:
        with open(VIDEOS_JSON, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Get Video ▶️", callback_data="get_video")]]
    await update.message.reply_text(
        "Tap to get a random video:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def get_video_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    videos = load_videos()
    if not videos:
        await query.message.reply_text("No videos found.")
        return

    video_id = random.choice(videos)

    keyboard = [[InlineKeyboardButton("Get Video ▶️", callback_data="get_video")]]
    await query.message.reply_animation(
        animation=video_id,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store new file_id when admin uploads video"""
    video = update.message.animation or update.message.video
    if not video:
        return

    file_id = video.file_id

    videos = load_videos()
    videos.append(file_id)

    with open(VIDEOS_JSON, "w") as f:
        json.dump(videos, f, indent=4)

    await update.message.reply_text("Video saved ✔️")


async def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not found!")
        return

    print("Bot starting with token loaded...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))

    # Callback (Get Video)
    app.add_handler(CallbackQueryHandler(get_video_callback))

    # Save uploaded videos (admin only)
    app.add_handler(MessageHandler(filters.VIDEO | filters.ANIMATION, handle_video))

    # Start bot
    await app.initialize()
    await app.start()
    print("Bot is running...")
    await app.updater.start_polling()
    await app.idle()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
