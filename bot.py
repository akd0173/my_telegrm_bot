# bot.py – random video bot with “Get Video” button reappearing after each send

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

# Railway will inject your token here (DO NOT PUT YOUR TOKEN IN THE CODE)
BOT_TOKEN = os.getenv("8580858808:AAHJwQeXeQpGNa4jrg2WqMhhSfZP_XhbV4s")

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
    await query.answer()  # acknowledge the button press quickly

    videos = load_videos()

    if not videos:
        await query.message.reply_text("No videos found in the list.")
        return

    # Pick a random video file_id
    video_id = random.choice(videos)

    # Rebuild keyboard for next video
    keyboard = [[InlineKeyboardButton("Get Video ▶️", callback_data="get_video")]]

    # Send the video + new button
    await query.message.reply_animation(
        animation=video_id,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin uploads a new video → its file_id gets stored into videos.json"""
    video = update.message.animation or update.message.video
    if not video:
        return

    file_id = video.file_id
    videos = load_videos()
    videos.append(file_id)

    with open(VIDEOS_JSON, "w") as f:
        js

