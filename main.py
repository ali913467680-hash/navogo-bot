"""
NavoGo Bot - Main Module
Telegram Music Recognition Bot
"""

import logging
import logging.config
import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Import configuration
from config import (
    TELEGRAM_BOT_TOKEN,
    BOT_USERNAME,
    LOGGING_CONFIG,
    validate_config,
    MESSAGES,
    DEFAULT_LANGUAGE,
    LOG_LEVEL,
)

# Setup logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)


# ========================
# Command Handlers
# ========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Get user's language (default: Uzbek)
    user_language = context.user_data.get("language", DEFAULT_LANGUAGE)
    
    welcome_message = MESSAGES[user_language]["welcome"]
    
    logger.info(f"👤 User {user.id} started bot")
    
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    user_language = context.user_data.get("language", DEFAULT_LANGUAGE)
    help_message = MESSAGES[user_language]["help"]
    
    logger.info(f"👤 User {update.effective_user.id} requested help")
    
    await update.message.reply_text(help_message)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command"""
    user_language = context.user_data.get("language", DEFAULT_LANGUAGE)
    about_message = MESSAGES[user_language]["about"]
    
    logger.info(f"👤 User {update.effective_user.id} requested about info")
    
    await update.message.reply_text(about_message)


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /language command"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    logger.info(f"👤 User {update.effective_user.id} opened language selector")
    
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🌐 Tilni tanlang / Выберите язык / Select language:", reply_markup=reply_markup)


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection via callback"""
    query = update.callback_query
    await query.answer()
    
    language_map = {
        "lang_uz": "uz",
        "lang_ru": "ru",
        "lang_en": "en",
    }
    
    language_code = language_map.get(query.data, DEFAULT_LANGUAGE)
    context.user_data["language"] = language_code
    
    language_names = {
        "uz": "🇺🇿 O'zbek",
        "ru": "🇷🇺 Русский",
        "en": "🇬🇧 English",
    }
    
    selected_lang = language_names.get(language_code, "Unknown")
    
    logger.info(f"👤 User {update.effective_user.id} selected language: {language_code}")
    
    await query.edit_message_text(text=f"✅ Tanlangan til: {selected_lang}")


# ========================
# Audio and Voice Handlers
# ========================

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle audio file uploads"""
    user = update.effective_user
    user_language = context.user_data.get("language", DEFAULT_LANGUAGE)
    
    logger.info(f"🎵 User {user.id} sent audio file")
    
    # Send "recognizing" message
    recognizing_msg = MESSAGES[user_language]["recognizing"]
    status_message = await update.message.reply_text(recognizing_msg)
    
    try:
        # Get audio file
        audio_file = update.message.audio
        
        # Check file size
        from config import MAX_AUDIO_SIZE_BYTES
        
        if audio_file.file_size > MAX_AUDIO_SIZE_BYTES:
            from config import MAX_AUDIO_SIZE_MB
            error_msg = MESSAGES[user_language]["file_too_large"].format(size=MAX_AUDIO_SIZE_MB)
            await status_message.edit_text(error_msg)
            logger.warning(f"⚠️ User {user.id} sent file that's too large: {audio_file.file_size} bytes")
            return
        
        # Download audio file
        file = await context.bot.get_file(audio_file.file_id)
        
        from config import TEMP_AUDIO_DIR
        import time
        
        # Create unique filename
        timestamp = int(time.time())
        audio_path = os.path.join(TEMP_AUDIO_DIR, f"audio_{user.id}_{timestamp}.mp3")
        
        await file.download_to_drive(audio_path)
        
        logger.info(f"✅ Downloaded audio file: {audio_path}")
        
        # TODO: Call music recognition API
        # For now, send a placeholder response
        
        result = {
            "success": False,
            "title": "Unknown Song",
            "artist": "Unknown Artist",
            "album": "Unknown Album",
            "duration": "0:00",
        }
        
        if result["success"]:
            response = MESSAGES[user_language]["found"].format(
                title=result["title"],
                artist=result["artist"],
                album=result["album"],
                duration=result["duration"],
            )
        else:
            response = MESSAGES[user_language]["not_found"]
        
        await status_message.edit_text(response)
        
        # Clean up temporary file
        try:
            os.remove(audio_path)
            logger.info(f"🗑️ Removed temporary file: {audio_path}")
        except Exception as e:
            logger.error(f"❌ Failed to remove temporary file: {e}")
        
    except Exception as e:
        logger.error(f"❌ Error processing audio: {e}")
        error_msg = MESSAGES[user_language]["error"]
        await status_message.edit_text(error_msg)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice message uploads"""
    user = update.effective_user
    user_language = context.user_data.get("language", DEFAULT_LANGUAGE)
    
    logger.info(f"🎤 User {user.id} sent voice message")
    
    # Send "recognizing" message
    recognizing_msg = MESSAGES[user_language]["recognizing"]
    status_message = await update.message.reply_text(recognizing_msg)
    
    try:
        # Get voice file
        voice_file = update.message.voice
        
        # Check file size
        from config import MAX_AUDIO_SIZE_BYTES
        
        if voice_file.file_size > MAX_AUDIO_SIZE_BYTES:
            from config import MAX_AUDIO_SIZE_MB
            error_msg = MESSAGES[user_language]["file_too_large"].format(size=MAX_AUDIO_SIZE_MB)
            await status_message.edit_text(error_msg)
            logger.warning(f"⚠️ User {user.id} sent voice that's too large: {voice_file.file_size} bytes")
            return
        
        # Download voice file
        file = await context.bot.get_file(voice_file.file_id)
        
        from config import TEMP_AUDIO_DIR
        import time
        
        # Create unique filename
        timestamp = int(time.time())
        voice_path = os.path.join(TEMP_AUDIO_DIR, f"voice_{user.id}_{timestamp}.ogg")
        
        await file.download_to_drive(voice_path)
        
        logger.info(f"✅ Downloaded voice file: {voice_path}")
        
        # TODO: Call music recognition API
        # For now, send a placeholder response
        
        result = {
            "success": False,
            "title": "Unknown Song",
            "artist": "Unknown Artist",
            "album": "Unknown Album",
            "duration": "0:00",
        }
        
        if result["success"]:
            response = MESSAGES[user_language]["found"].format(
                title=result["title"],
                artist=result["artist"],
                album=result["album"],
                duration=result["duration"],
            )
        else:
            response = MESSAGES[user_language]["not_found"]
        
        await status_message.edit_text(response)
        
        # Clean up temporary file
        try:
            os.remove(voice_path)
            logger.info(f"🗑️ Removed temporary voice file: {voice_path}")
        except Exception as e:
            logger.error(f"❌ Failed to remove temporary voice file: {e}")
        
    except Exception as e:
        logger.error(f"❌ Error processing voice: {e}")
        error_msg = MESSAGES[user_language]["error"]
        await status_message.edit_text(error_msg)


# ========================
# Error Handler
# ========================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in bot"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        user_language = context.user_data.get("language", DEFAULT_LANGUAGE)
        error_msg = MESSAGES[user_language]["error"]
        
        try:
            await update.effective_message.reply_text(error_msg)
        except Exception as e:
            logger.error(f"❌ Failed to send error message: {e}")


# ========================
# Main Function
# ========================

async def main() -> None:
    """Start the bot"""
    
    # Validate configuration
    if not validate_config():
        logger.error("❌ Configuration validation failed!")
        sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("🎵 NavoGo Bot Starting...")
    logger.info("=" * 50)
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("language", language))
    
    # Add callback query handler for language selection
    from telegram.ext import CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    
    # Add audio and voice message handlers
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info(f"✅ NavoGo bot (@{BOT_USERNAME}) is running...")
    logger.info("📝 Waiting for messages...")
    
    # Run the bot until the user presses Ctrl-C
    await application.run_polling()


if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 NavoGo bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
