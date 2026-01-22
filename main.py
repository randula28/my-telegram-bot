import os
import yt_dlp
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '8476056413:AAHD_ZpEfonhZt3_KTeJdFBsWXpO2OOsxcI'

# --- 1. ලින්ක් එකක් ආ විට Button පෙන්වීම ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        # බොත්තම් සකස් කිරීම
        keyboard = [
            [
                InlineKeyboardButton("🎵 Audio (MP3)", callback_data=f"mp3|{url}"),
                InlineKeyboardButton("🎬 Video (720p)", callback_data=f"mp4|{url}")
            ],
            [InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📥 කරුණාකර ඔබට අවශ්‍ය Format එක තෝරන්න:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ කරුණාකර වලංගු YouTube ලින්ක් එකක් එවන්න.")

# --- 2. Button එකක් ක්ලික් කළ විට සිදුවන දේ (Callback) ---
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Button එකේ කැරකෙන එක නතර කිරීමට
    
    data = query.data.split("|")
    action = data[0]
    
    if action == "cancel":
        await query.edit_message_text("❌ ක්‍රියාවලිය අවලංගු කරන ලදී.")
        return

    url = data[1]
    user_id = update.effective_user.id
    
    if action == "mp3":
        status_text = "📥 MP3 එක සකසමින් පවතී..."
        file_path = f"{user_id}.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_path,
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
            'quiet': True
        }
    else: # mp4
        status_text = "📥 වීඩියෝව (MP4) ඩවුන්ලෝඩ් වෙමින් පවතී..."
        file_path = f"{user_id}.mp4"
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': file_path,
            'quiet': True
        }

    await query.edit_message_text(text=status_text)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if action == "mp3":
            await context.bot.send_audio(chat_id=user_id, audio=open(file_path, 'rb'), caption="✅ සාර්ථකයි!")
        else:
            await context.bot.send_video(chat_id=user_id, video=open(file_path, 'rb'), caption="✅ සාර්ථකයි!")
            
        os.remove(file_path)
        await query.delete_message()
    except Exception as e:
        await query.edit_message_text(text=f"❌ දෝෂයක්: {str(e)}")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # ලින්ක් එකක් ආ විට හසුරුවන ආකාරය
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Button Click හසුරුවන ආකාරය
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("🚀 Buttons Bot is running...")
    app.run_polling()
