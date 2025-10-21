import os
import logging
import sys
from logging.handlers import RotatingFileHandler

# Bot configuration
TOKEN = os.getenv("BOT_TOKEN", "8167063245:AAFr_FRuuN0-wImIS32-A8-Oi9kr-Pb_XII")
PORT = int(os.getenv("PORT", 8081))

# Twitter credentials for authentication
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")

# Auto-restart settings
AUTO_RESTART = True
AUTO_RESTART_DELAY = 10  # seconds
MAX_RESTART_ATTEMPTS = 5

# Download configuration
DOWNLOAD_DIR = "downloads"
MAX_DOWNLOADS = 5  # Maximum concurrent downloads
DOWNLOAD_TIMEOUT = 600  # Timeout in seconds for downloads
MAX_FILE_SIZE = 50 * 1024 * 1024  # Maximum file size (50MB Telegram limit)
CLEANUP_INTERVAL = 3600  # Cleanup interval in seconds (1 hour)
MAX_FILE_AGE = 86400  # Maximum age of files before cleanup (24 hours)

# Rate limiting configuration
MAX_REQUESTS_PER_MINUTE = 10  # Per user
COOLDOWN_PERIOD = 5  # Seconds to wait after hitting rate limit

# Video quality options
VIDEO_QUALITY_OPTIONS = {
    "best": {"format": "bestvideo+bestaudio/best", "description": "Best quality (larger file)"},
    "medium": {"format": "worstvideo[height>=480][ext=mp4]+worstaudio[ext=m4a]/best[height>=480][ext=mp4]/best[height>=480]", "description": "Medium quality (balanced)"},
    "low": {"format": "worstvideo[height>=360][ext=mp4]+worstaudio[ext=m4a]/best[height>=360][ext=mp4]/best[height>=360]", "description": "Low quality (smaller file)"}
}
DEFAULT_QUALITY = "medium"

# Setup logging
def setup_logging():
    os.makedirs("logs", exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("video_downloader_bot")
    logger.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File handler (rotating to avoid filling disk)
    file_handler = RotatingFileHandler("logs/bot.log", maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

LOGGER = setup_logging()
