import logging
import asyncio
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from decouple import config

from handlers.start import start_handler
from handlers.transaction import transaction_handler, add_transaction_handler
from handlers.balance import balance_handler, accounts_handler
from handlers.help import help_handler
from handlers.analytics import analytics_handler, report_handler
from services.user_service import register_or_get_user

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
API_BASE_URL = config('API_BASE_URL', default='http://localhost:8000/api/v1')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by Updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


async def post_init(application: Application) -> None:
    """Post initialization hook."""
    # Set bot commands
    commands = [
        BotCommand("start", "Начать работу с ботом / Start using the bot"),
        BotCommand("help", "Показать справку / Show help"),
        BotCommand("balance", "Показать баланс счетов / Show account balances"),
        BotCommand("accounts", "Управление счетами / Manage accounts"),
        BotCommand("add", "Добавить транзакцию / Add transaction"),
        BotCommand("report", "Показать отчет / Show report"),
        BotCommand("analytics", "Аналитика трат / Spending analytics"),
    ]
    
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands set successfully")


def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("balance", balance_handler))
    application.add_handler(CommandHandler("accounts", accounts_handler))
    application.add_handler(CommandHandler("add", add_transaction_handler))
    application.add_handler(CommandHandler("report", report_handler))
    application.add_handler(CommandHandler("analytics", analytics_handler))
    
    # Add message handler for natural language transactions
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, transaction_handler))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting Family Budget Manager Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()