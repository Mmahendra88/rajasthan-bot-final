import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
TELEGRAM_BOT_TOKEN = os.getenv('8316781825:AAGhjwbGi4m-K1blHe9_t8N4XdqwYPUvvXE')
GEMINI_API_KEY = os.getenv('AIzaSyCW7UxMh4vEvvWcrfbZwW0WbxdZxHuBhB0')

# Websites to scrape
WEBSITES = [
    "https://jaipurthrumylens.com",
    "https://rtdc.tourism.rajasthan.gov.in", 
    "https://www.rajasthantourdriver.com"
]

# Bot configuration
MAX_MESSAGE_LENGTH = 4096
