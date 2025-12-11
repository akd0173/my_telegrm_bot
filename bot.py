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

# ⏺️ Load BOT_TOKEN from Railway Environment Variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

print("Loaded token:", BOT_TOKEN)
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not found! Exiting...")
    exit()

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
        await query.message.reply_text("No videos found in the list.")
        return

    video_id = random.choice(videos)

    keyboard = [[InlineKeyboardButton("Get Video ▶️", callback_data="get_video")]]

    await query.message.reply_animation(
        animation=video_id,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin uploads a new video → saves its file_id."""
    video = update.message.animation or update.message.video
    if not video:
        return

    file_id = video.file_id
    videos = load_videos()
    videos.append(file_id)

    with open(VIDEOS_JSON, "w") as f:
        json.dump(videos, f)

    await update.message.reply_text("Video saved successfully!")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(get_video_callback))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Animation, handle_video))

    app.run_polling()


if __name__ == "__main__":
    main()
