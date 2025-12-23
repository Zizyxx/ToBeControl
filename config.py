import os
import logging
from dotenv import load_dotenv

# Load file .env
load_dotenv()

# Ambil variabel environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
uri = os.getenv("uri")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validasi Token
if not TELEGRAM_TOKEN:
    raise SystemExit("❌ ENV ERROR: TELEGRAM_TOKEN belum diset di file .env")
if not uri:
    raise SystemExit("❌ ENV ERROR: uri belum diset di file .env")

# Setup Logging agar bisa dipanggil di file lain
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("tbc_bot")