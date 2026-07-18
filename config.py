import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN or not GEMINI_API_KEY:
    print("WARNING: BOT_TOKEN or GEMINI_API_KEY is not set. Please copy .env.example to .env and fill in the values.")
