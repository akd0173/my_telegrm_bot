# -*- coding: utf-8 -*-
"""
Render-ready Telegram bot.
It reads BOT_TOKEN from the environment. If not found, it falls back to a fake token
(useful for local testing). When deploying to Render, add BOT_TOKEN in the service
Environment Variables so the real token is used.
"""

import os
import json
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ---------- TOKEN (env preferred) ----------
# Render/Heroku/Railway: set the environment variable BOT_TOKEN in the service settings.
# Fallback to the fake token provided (only for local testing; OK to keep here because it's fake).
FALLBACK_FAKE_TOKEN = "8580858808:AAHwRlkUoIIE1kpTHBZ0r9YnH5f_WNfkio4"
BOT_TOKEN = os.getenv("8580858808:AAHwRlkUoIIE1kpTHBZ0r9YnH5f_WNfkio4") or FALLBACK_FAKE_TOKEN

if BOT_TOKEN is None or BOT_TOKEN.strip() == "":
    print("ERROR: No BOT_TOKEN provided (env or fallback). Exiting.")
    raise SystemExit(1)

VIDEOS_JSON = "videos.json"


# ---------- Utilities ----------
def load_videos():
    try:
        with open(VIDEOS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception:
        return []


def save_videos(list_of_ids):
    with open(VIDEOS_JSON, "w", encoding="utf-8") as f:
        json.dump(list_of_ids, f, indent=2, ensure_ascii=False)


# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Get Video ▶️", callback_data="get_video")]]
    await update.message.reply_text(
        "Tap to get a random video:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def get_video_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # acknowledge

    videos = load_videos()
    if not videos:
        # remove button from original message (if possible) and inform
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

    # remove inline keyboard from previous message and send new button below the video
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
    """When a user (or admin) uploads a video or animation, save its file_id."""
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


# ---------- Main (async) ----------
async def main():
    print("Starting bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(get_video_callback, pattern="get_video"))
    app.add_handler(MessageHandler(filters.VIDEO | filters.ANIMATION, handle_video))

    # initialize and run
    await app.initialize()
    await app.start()
    print("Bot is running (polling)...")
    await app.updater.start_polling()
    await app.idle()


if __name__ == "__main__":
    asyncio.run(main())

