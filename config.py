import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@memes_for_friends_best")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
MAIN_GROUP_ID = os.getenv("MAIN_GROUP_ID") # ID основной группы для Архивов Шерифа

if not BOT_TOKEN or not GROQ_API_KEY:
    print("WARNING: BOT_TOKEN or GROQ_API_KEY is not set. Please copy .env.example to .env and fill in the values.")
