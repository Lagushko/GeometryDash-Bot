import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_ID = os.getenv("APP_ID")
    PUBLIC_KEY = os.getenv("PUBLIC_KEY")
    TOKEN_BOT = os.getenv("TOKEN_BOT")

    BOT_URL = os.getenv("BOT_URL")

    OWNER = [int(os.getenv("OWNER"))]