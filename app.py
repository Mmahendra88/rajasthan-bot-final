from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, MAX_MESSAGE_LENGTH
from scraper import WebsiteScraper
from gemini_handler import GeminiHandler
import asyncio

class TourismBot:
    def __init__(self):
        self.scraper = WebsiteScraper()
        self.gemini = GeminiHandler()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
        Namaste! 🙏 Welcome to Rajasthan Tourism Bot!

        I can help you with information about:
        • Jaipur tourism (jaipurthrumylens.com)
        • Rajasthan Tourism Development (rtdc.tourism.rajasthan.gov.in)
        • Rajasthan tour packages (rajasthantourdriver.com)

        Just ask me any question about Rajasthan tourism!
        """
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(help_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        user_message = update.message.text
        
        # Show typing action
        await update.message.chat.send_action(action="typing")
        
        try:
            # Step 1: Scrape data from websites
            await update.message.reply_text("🔍 Fetching latest information from tourism websites...")
            scraped_data = await asyncio.get_event_loop().run_in_executor(
                None, self.scraper.get_combined_data
            )
            
            # Step 2: Generate response using Gemini
            await update.message.reply_text("🤔 Analyzing information and preparing answer...")
            response = self.gemini.generate_response(user_message, scraped_data)
            
            # Step 3: Send response (handle long messages)
            if len(response) > MAX_MESSAGE_LENGTH:
                # Split long messages
                for i in range(0, len(response), MAX_MESSAGE_LENGTH):
                    await update.message.reply_text(response[i:i+MAX_MESSAGE_LENGTH])
            else:
                await update.message.reply_text(response)
                
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            await update.message.reply_text(error_message)
    
    def run(self):
        """Start the bot"""
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start bot
        print("🤖 Bot is running...")
        application.run_polling()

if __name__ == "__main__":
    bot = TourismBot()
    bot.run()
