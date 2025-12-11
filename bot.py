# bot.py — random video bot with "Get Video" button reappearing after each send
import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8580858808:AAGN5DlACmPHI78xjTmfNnTpHBWXsPVwqK4"  # <-- put your token here on your machine
VIDEOS_JSON = "videos.json"

def load_videos():
    try:
        with open(VIDEOS_JSON, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Get Video ▶️", callback_data="get_video")]]
    await update.message.reply_text("Tap to get a random video:", reply_markup=InlineKeyboardMarkup(keyboard))

async def get_video_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # acknowledge the button press quickly

    videos = load_videos()
    if not videos:
        # Edit original message markup (remove button) and tell user
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await query.message.reply_text("No videos added yet. Send me a video to store it.")
        return

    # send the random video
    video = random.choice(videos)
    try:
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=video["id"],
            caption=video.get("title", "")
        )
    except Exception as e:
        # if sending fails, inform the user and keep the button
        await query.message.reply_text(f"Failed to send video: {e}")
        return

    # remove the inline keyboard from the original message (so it doesn't stay there)
    try:
        await query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        # ignore if we can't edit (e.g., older message or already removed)
        pass

    # send a new message with the Get Video button so it's always visible below the latest video
    keyboard = [[InlineKeyboardButton("Get Video ▶️", callback_data="get_video")]]
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Get another video:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def upload_logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg and msg.video:
        file_id = msg.video.file_id
        title = msg.caption or "Uploaded video"

        videos = load_videos()
        entry = {"id": file_id, "title": title}

        if entry not in videos:
            videos.append(entry)
            with open(VIDEOS_JSON, "w") as f:
                json.dump(videos, f, indent=2)

        await msg.reply_text(f"Video saved!\nFile ID:\n`{file_id}`", parse_mode="Markdown")
    else:
        await msg.reply_text("Send me a video to save it.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(get_video_callback, pattern="get_video"))
    app.add_handler(MessageHandler(filters.VIDEO & filters.ChatType.PRIVATE, upload_logger))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
