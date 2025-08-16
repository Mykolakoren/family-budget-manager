import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from handlers.budget_handlers import setup_budget_handlers
from handlers.transaction_handlers import setup_transaction_handlers
from handlers.analytics_handlers import setup_analytics_handlers

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\n"
        f"Welcome to Family Budget Manager Bot! 🏦\n\n"
        f"Available commands:\n"
        f"/budgets - Manage your budgets\n"
        f"/add - Add a transaction\n"
        f"/balance - Check balance\n"
        f"/analytics - View analytics\n"
        f"/help - Show this help message\n\n"
        f"You can also just type your transaction naturally, like:\n"
        f"'Bought groceries for 50 GEL at Carrefour'"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command handler"""
    help_text = """
🏦 *Family Budget Manager Bot*

*Commands:*
/start - Start the bot
/budgets - Manage your budgets
/add - Add a transaction manually
/balance - Check current balance
/analytics - View spending analytics
/export - Export your data
/settings - Bot settings

*Smart Input:*
You can add transactions by simply typing them naturally:
• "Lunch 25 GEL"
• "Salary 2000 USD"
• "Coffee at Starbucks 8.50 GEL"
• "Transfer 100 USD to savings"

*Supported Currencies:*
GEL, USD, EUR, UAH, USDT
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_smart_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle natural language transaction input"""
    text = update.message.text
    
    # TODO: Implement LLM-based transaction parsing
    await update.message.reply_text(
        f"🤖 Smart input received: '{text}'\n\n"
        f"This will be processed using AI to extract transaction details.\n"
        f"(Feature coming soon!)"
    )

def main() -> None:
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    # Create the Application
    application = Application.builder().token(token).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Setup feature handlers
    setup_budget_handlers(application)
    setup_transaction_handlers(application)
    setup_analytics_handlers(application)
    
    # Handle all text messages as smart input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_smart_input))

    # Run the bot
    logger.info("Starting Family Budget Manager Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()