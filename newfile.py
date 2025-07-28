import json
import os
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8414838681:AAGfZml3NjOtP36qTi-iGs_n6rrulcT1S7Q"
ADMIN_ID = 8345668613          # آی‌دی عددی ادمین

VIDEOS_FILE = os.path.join(os.path.dirname(__file__), "videos.json")
videos = {}

def save_videos():
    with open(VIDEOS_FILE, "w") as f:
        json.dump(videos, f)

def load_videos():
    global videos
    if os.path.exists(VIDEOS_FILE):
        with open(VIDEOS_FILE, "r") as f:
            videos = json.load(f)
    else:
        videos = {}

def add(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ دسترسی غیرمجاز.")
        return

    if len(context.args) != 2:
        update.message.reply_text("فرمت صحیح:\n/add کد https://t.me/channel/33")
        return

    code = context.args[0].lower()
    link = context.args[1]

    try:
        parts = link.split("/")
        if "t.me/" not in link or len(parts) < 5:
            update.message.reply_text("❌ لینک نامعتبر است.")
            return

        if "/c/" in link:
            # لینک خصوصی
            channel_id = int("-100" + parts[-2])
            message_id = int(parts[-1])
        else:
            # لینک عمومی
            channel_id = "@" + parts[3]
            message_id = int(parts[4])

        videos[code] = [channel_id, message_id]
        save_videos()
        update.message.reply_text(f"✅ ویدیو با کد «{code}» ثبت شد.")
    except Exception as e:
        update.message.reply_text("❌ خطا در پردازش لینک.")
        print("Error in /add:", e)

def start(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        update.message.reply_text("🔹 برای دریافت ویدیو، کد رو بعد از /start بنویس.")
        return

    code = args[0].lower()
    if code not in videos:
        update.message.reply_text("❌ کد یافت نشد.")
        return

    chat_id = update.effective_chat.id
    channel_id, message_id = videos[code]

    print(f"Forwarding from channel_id: {channel_id}, message_id: {message_id}")

    try:
        sent_message = context.bot.forward_message(
            chat_id=chat_id,
            from_chat_id=channel_id,
            message_id=message_id
        )

        try:
            context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        except:
            pass  # اگر پیام کاربر پاک نشد، نادیده بگیر

        time.sleep(30)
        context.bot.delete_message(chat_id=chat_id, message_id=sent_message.message_id)
    except Exception as e:
        update.message.reply_text("⚠️ خطا در ارسال ویدیو.")
        print("Error in /start:", e)

def list_codes(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ دسترسی غیرمجاز.")
        return

    if not videos:
        update.message.reply_text("📬 هنوز هیچ ویدیویی ثبت نشده.")
        return

    text = "\n".join([f"{code} → {data[0]}/{data[1]}" for code, data in videos.items()])
    update.message.reply_text(f"📄 لیست کدها:\n{text}")

def delete_code(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ دسترسی غیرمجاز.")
        return

    if not context.args:
        update.message.reply_text("فرمت صحیح:\n/delete کد")
        return

    code = context.args[0].lower()
    if code in videos:
        del videos[code]
        save_videos()
        update.message.reply_text(f"✅ کد «{code}» حذف شد.")
    else:
        update.message.reply_text("❌ کد پیدا نشد.")

def main():
    load_videos()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("list", list_codes))
    dp.add_handler(CommandHandler("delete", delete_code))

    print("Bot started...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()