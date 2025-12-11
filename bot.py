# -*- coding: utf-8 -*-
"""
Telegram bot using Application.run_polling() so hosted platforms (Railway/Render)
handle shutdown signals gracefully and we avoid noisy asyncio.CancelledError logs.
"""

import os
import json
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s"
)
logger = logging.getLogger(__name__)

# Read token from environment (do NOT commit a real token in code)
FALLBACK_FAKE_TOKEN = "8580858808:AAHwRlkUoIIE1kpTHBZ0r9YnH5f_WNfkio4"
BOT_TOKEN = os.getenv("8580858808:AAHwRlkUoIIE1kpTHBZ0r9YnH5f_WNfkio4") or FALLBACK_FAKE_TOKEN

if not BOT_TOKEN:
    logger.error("BOT_TOKEN not provided. Exiting.")
    raise SystemExit(1)

VIDEOS_JSON = "videos.json"


def load_videos():
    try:
        with open(VIDEOS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        logger.warning("Failed to load videos.json: %s", e)
        return []


def save_videos(list_of_ids):
    try:
        with open(VIDEOS_JSON, "w", encoding="utf-8") as f:
            json.dump(list_of_ids, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("Failed to save videos.json: %s", e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Get Video ▶️", callback_data="get_video")]]
    await update.message.reply_text(
        "Tap to get a random video:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def get_video_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    videos = load_videos()
    if not videos:
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await query.message.reply_text("No videos available yet. Upload a video to save it.")
        return

    video_file_id = random.choice(videos)

    # send video
    try:
        await context.bot.send_video(chat_id=query.message.chat_id, video=video_file_id)
    except Exception as e:
        await query.message.reply_text(f"Failed to send video: {e}")
        return

    # remove inline keyboard from previous message (if any) and send new button
    try:
        await query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    keyboard = [[InlineKeyboardButton("Get Video ▶️", callback_data="get_video")]]
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Get another video:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    video_obj = msg.video or msg.animation
    if not video_obj:
        await msg.reply_text("Please send a video file (mp4) or an animation (gif).")
        return

    file_id = video_obj.file_id
    videos = load_videos()
    if file_id not in videos:
        videos.append(file_id)
        save_videos(videos)
        await msg.reply_text("Video saved ✔️")
    else:
        await msg.reply_text("This video is already saved.")


def build_and_run():
    logger.info("Using BOT_TOKEN: %s", "provided" if os.getenv("BOT_TOKEN") else "fallback (local)")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(get_video_callback, pattern="get_video"))
    app.add_handler(MessageHandler(filters.VIDEO | filters.ANIMATION, handle_video))

    # run_polling handles signals / graceful shutdown on hosted platforms
    logger.info("Starting polling (this will block until stopped)...")
    app.run_polling(poll_interval=1.0)


if __name__ == "__main__":
    try:
        build_and_run()
    except Exception as e:
        logger.exception("Unhandled exception in main: %s", e)
        raise
