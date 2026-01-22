import os
import asyncio
import logging
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# බොට්ගේ ක්‍රියාකාරීත්වය පරීක්ෂා කිරීමට (Logging)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- මෙතනට ඔබේ BOT TOKEN එක දාන්න ---
TOKEN = '8476056413:AAHD_ZpEfonhZt3_KTeJdFBsWXpO2OOsxcI'

# --- Welcome Message ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 **ආයුබෝවන් {user.first_name}!**\n\n"
        "🚀 මම ඔබගේ **Premium Downloader Bot**.\n"
        "YouTube සින්දු ඉතා ඉක්මනින් මගෙන් ලබාගන්න පුළුවන්.\n\n"
        "📂 **භාවිතා කරන ආකාරය:**\n"
        "YouTube Music හෝ Video ලින්ක් එකක් මට එවන්න.\n"
    )
    keyboard = [[InlineKeyboardButton("Developer 👨‍💻", url='https://t.me/your_username')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# --- Download & Upload Function ---
async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        status_msg = await update.message.reply_text("🔎 **ලින්ක් එක පරීක්ෂා කරමින්...**", parse_mode='Markdown')
        
        # ඩවුන්ලෝඩ් කරන ගොනුවේ නම (Filename)
        file_path = f"{update.effective_user.id}.mp3"

        # yt-dlp settings
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }

        try:
            await status_msg.edit_text("⚡ **සර්වර් එක හරහා ඩවුන්ලෝඩ් වෙමින් පවතී...**", parse_mode='Markdown')
            
            # YouTube එකෙන් Download කිරීම
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            await status_msg.edit_text("📤 **Telegram වෙත අප්ලෝඩ් වෙමින් පවතී...**", parse_mode='Markdown')
            
            # Telegram එකට Audio එක යැවීම
            await update.message.reply_audio(
                audio=open(file_path, 'rb'),
                caption="✅ **සාර්ථකව ඩවුන්ලෝඩ් කරන ලදී!**\n\n@YourBotUsername",
                parse_mode='Markdown'
            )
            
            # වැඩේ ඉවර වුණාම සර්වර් එකේ තියෙන file එක මකා දැමීම
            os.remove(file_path)
            await status_msg.delete()

        except Exception as e:
            await status_msg.edit_text(f"❌ **දෝෂයක් සිදු විය:** \n`{str(e)}`", parse_mode='Markdown')
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        await update.message.reply_text("❌ කරුණාකර වලංගු YouTube ලින්ක් එකක් එවන්න.")

# --- Main Bot Execution ---
if __name__ == '__main__':
    print("🚀 Bot is starting on Cloud...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_links))

    app.run_polling()
