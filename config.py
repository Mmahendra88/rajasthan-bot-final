import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Websites to scrape
WEBSITES = [
    "https://jaipurthrumylens.com",
    "https://rtdc.tourism.rajasthan.gov.in", 
    "https://www.rajasthantourdriver.com"
]

# Bot configuration
MAX_MESSAGE_LENGTH = 4096
