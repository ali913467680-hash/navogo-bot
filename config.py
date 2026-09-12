"""
NavoGo Bot Configuration Module
Loads environment variables and provides centralized configuration
"""

import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# ========================
# Telegram Bot Configuration
# ========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "NavoGoMusicBot")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "❌ TELEGRAM_BOT_TOKEN not found in .env file! "
        "Please set TELEGRAM_BOT_TOKEN in .env"
    )

# ========================
# Music Recognition API Configuration
# ========================

MUSIC_API_KEY = os.getenv("MUSIC_API_KEY", "")
MUSIC_API_TYPE = os.getenv("MUSIC_API_TYPE", "shazam")  # shazam, acoustid, audd, etc.

if not MUSIC_API_KEY:
    raise ValueError(
        "❌ MUSIC_API_KEY not found in .env file! "
        "Please set MUSIC_API_KEY in .env"
    )

# API Endpoints (can be overridden via environment variables)
SHAZAM_API_URL = os.getenv("SHAZAM_API_URL", "https://api.audd.io/")
ACOUSTID_API_URL = os.getenv("ACOUSTID_API_URL", "https://api.acousticbrainz.org/v1/submit")

# ========================
# Bot Configuration
# ========================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "true").lower() == "true"

# Audio file limits
MAX_AUDIO_SIZE_MB = int(os.getenv("MAX_AUDIO_SIZE_MB", "10"))
MAX_AUDIO_SIZE_BYTES = MAX_AUDIO_SIZE_MB * 1024 * 1024

# Supported audio formats
SUPPORTED_AUDIO_FORMATS = ["mp3", "wav", "ogg", "flac", "m4a", "aac"]
SUPPORTED_VOICE_FORMATS = ["ogg"]  # Telegram voice messages are OGG

# ========================
# Temporary Files Configuration
# ========================

TEMP_AUDIO_DIR = os.getenv("TEMP_AUDIO_DIR", "temp_audio")
TEMP_AUDIO_RETENTION_SECONDS = int(os.getenv("TEMP_AUDIO_RETENTION_SECONDS", "3600"))  # 1 hour

# Create temp directory if it doesn't exist
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# ========================
# Admin Configuration (for future admin features)
# ========================

ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]

# ========================
# Database Configuration (for future features)
# ========================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///navogo.db")

# ========================
# Feature Flags
# ========================

ENABLE_HISTORY = os.getenv("ENABLE_HISTORY", "false").lower() == "true"
ENABLE_FAVORITES = os.getenv("ENABLE_FAVORITES", "false").lower() == "true"
ENABLE_STATS = os.getenv("ENABLE_STATS", "false").lower() == "true"

# ========================
# Logging Configuration
# ========================

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": LOG_LEVEL,
            "formatter": "detailed",
            "filename": "logs/navogo.log",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "telegram": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# ========================
# Languages Configuration
# ========================

SUPPORTED_LANGUAGES = {
    "uz": "🇺🇿 O'zbek",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

DEFAULT_LANGUAGE = "uz"

# ========================
# Messages Templates (will be moved to utils/messages.py)
# ========================

MESSAGES = {
    "uz": {
        "welcome": "🎵 Salom! NavoGo botiga xush kelibsiz!\n\nAudio yoki voice xabarni yuboring va men qo'shiqni aniqlayaman.",
        "help": "📖 NavoGo yordami:\n\n/start - Botni boshlash\n/help - Yordam\n/about - NavoGo haqida\n/language - Tilni tanlash",
        "about": "🎵 NavoGo — Telegram ichida musiqani aniqlash boti.\n\nBot qo'shiqni audio yoki voice orqali aniqlab beradi.",
        "recognizing": "🔎 Musiqa aniqlanmoqda...",
        "found": "🎵 Qo'shiq topildi!\n\n🎤 Ijrochi: {artist}\n🎶 Qo'shiq: {title}\n💿 Albom: {album}\n⏱ Davomiyligi: {duration}",
        "not_found": "😔 Kechirasiz, bu qo'shiqni aniqlay olmadim. Boshqa audio yuborib ko'ring.",
        "error": "⚠️ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.",
        "file_too_large": "📦 Fayl juda katta! Maksimal {size}MB yuklay olaman.",
        "unsupported_format": "❌ Bu fayl formati qo'llanmaydi. MP3, WAV, OGG formatlarini yuboring.",
        "api_error": "🔌 API xizmatida muammo. Iltimos, birazdan qayta urinib ko'ring.",
    },
    "ru": {
        "welcome": "🎵 Привет! Добро пожаловать в NavoGo бот!\n\nОтправьте аудиофайл или голосовое сообщение, и я определю песню.",
        "help": "📖 Справка NavoGo:\n\n/start - Запустить бота\n/help - Справка\n/about - О NavoGo\n/language - Выбрать язык",
        "about": "🎵 NavoGo — бот для распознавания музыки в Telegram.\n\nБот определяет песню по аудио или голосовому сообщению.",
        "recognizing": "🔎 Определяю музыку...",
        "found": "🎵 Песня найдена!\n\n🎤 Исполнитель: {artist}\n🎶 Название: {title}\n💿 Альбом: {album}\n⏱ Длительность: {duration}",
        "not_found": "😔 Извините, не смог определить эту песню. Попробуйте другой аудиофайл.",
        "error": "⚠️ Произошла ошибка. Пожалуйста, попробуйте снова.",
        "file_too_large": "📦 Файл слишком большой! Я могу загрузить максимум {size}МБ.",
        "unsupported_format": "❌ Этот формат файла не поддерживается. Отправьте MP3, WAV или OGG.",
        "api_error": "🔌 Проблема с API сервисом. Пожалуйста, попробуйте позже.",
    },
    "en": {
        "welcome": "🎵 Hello! Welcome to NavoGo bot!\n\nSend me an audio file or voice message, and I'll identify the song.",
        "help": "📖 NavoGo Help:\n\n/start - Start bot\n/help - Help\n/about - About NavoGo\n/language - Select language",
        "about": "🎵 NavoGo — A music recognition bot for Telegram.\n\nIdentify songs from audio or voice messages.",
        "recognizing": "🔎 Recognizing music...",
        "found": "🎵 Song found!\n\n🎤 Artist: {artist}\n🎶 Title: {title}\n💿 Album: {album}\n⏱ Duration: {duration}",
        "not_found": "😔 Sorry, I couldn't identify this song. Try sending another audio file.",
        "error": "⚠️ An error occurred. Please try again.",
        "file_too_large": "📦 File is too large! I can upload maximum {size}MB.",
        "unsupported_format": "❌ This file format is not supported. Send MP3, WAV, or OGG.",
        "api_error": "🔌 API service error. Please try again later.",
    },
}

# ========================
# Validation
# ========================

def validate_config():
    """Validate configuration on startup"""
    errors = []

    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is not set")

    if not MUSIC_API_KEY:
        errors.append("MUSIC_API_KEY is not set")

    if MAX_AUDIO_SIZE_MB <= 0:
        errors.append("MAX_AUDIO_SIZE_MB must be greater than 0")

    if MUSIC_API_TYPE not in ["shazam", "acoustid", "audd"]:
        errors.append(f"Unknown MUSIC_API_TYPE: {MUSIC_API_TYPE}")

    if errors:
        for error in errors:
            logging.error(f"❌ Configuration Error: {error}")
        return False

    logging.info("✅ Configuration validated successfully")
    return True


# ========================
# Print Configuration Summary
# ========================

if __name__ == "__main__":
    print("=" * 50)
    print("🎵 NavoGo Configuration Summary")
    print("=" * 50)
    print(f"Bot Token: {'✓' if TELEGRAM_BOT_TOKEN else '✗'}")
    print(f"Bot Username: {BOT_USERNAME}")
    print(f"Music API Type: {MUSIC_API_TYPE}")
    print(f"Music API Key: {'✓' if MUSIC_API_KEY else '✗'}")
    print(f"Max Audio Size: {MAX_AUDIO_SIZE_MB}MB")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Supported Languages: {', '.join(SUPPORTED_LANGUAGES.values())}")
    print(f"Admin IDs: {ADMIN_IDS if ADMIN_IDS else 'None'}")
    print("=" * 50)
