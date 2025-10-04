from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import TELEGRAM_BOT_TOKEN, MAX_MESSAGE_LENGTH
from scraper import WebsiteScraper
from gemini_handler import GeminiHandler
import asyncio
import threading

class TourismBot:
    def __init__(self):
        self.scraper = WebsiteScraper()
        self.gemini = GeminiHandler()
        
    def start_command(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        welcome_message = """
        Namaste! 🙏 Welcome to Rajasthan Tourism Bot!

        I can help you with information about:
        • Jaipur tourism (jaipurthrumylens.com)
        • Rajasthan Tourism Development (rtdc.tourism.rajasthan.gov.in)
        • Rajasthan tour packages (rajasthantourdriver.com)

        Just ask me any question about Rajasthan tourism!
        """
        
        update.message.reply_text(welcome_message)
    
    def help_command(self, update: Update, context: CallbackContext):
        """Handle /help command"""
        help_text = """
        🤖 How to use this bot:

        Simply type your question about Rajasthan tourism, such as:
        • "Best places to visit in Jaipur"
        • "Rajasthan tour packages"
        • "Cultural events in Rajasthan"
        • "Travel tips for Rajasthan"

        I'll fetch the latest information from official Rajasthan tourism websites and provide you with an answer!
        """
        update.message.reply_text(help_text)
    
    def handle_message(self, update: Update, context: CallbackContext):
        """Handle incoming messages"""
        user_message = update.message.text
        
        # Show typing action
        update.message.chat.send_action(action="typing")
        
        try:
            # Step 1: Scrape data from websites
            update.message.reply_text("🔍 Fetching latest information from tourism websites...")
            scraped_data = self.scraper.get_combined_data()
            
            # Step 2: Generate response using Gemini
            update.message.reply_text("🤔 Analyzing information and preparing answer...")
            response = self.gemini.generate_response(user_message, scraped_data)
            
            # Step 3: Send response (handle long messages)
            if len(response) > MAX_MESSAGE_LENGTH:
                # Split long messages
                for i in range(0, len(response), MAX_MESSAGE_LENGTH):
                    update.message.reply_text(response[i:i+MAX_MESSAGE_LENGTH])
            else:
                update.message.reply_text(response)
                
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            update.message.reply_text(error_message)
    
    def run(self):
        """Start the bot"""
        updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # Add handlers
        dp.add_handler(CommandHandler("start", self.start_command))
        dp.add_handler(CommandHandler("help", self.help_command))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        
        # Start bot
        print("🤖 Bot is running...")
        updater.start_polling()
        updater.idle()

if __name__ == "__main__":
    bot = TourismBot()
    bot.run()
