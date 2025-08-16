from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import httpx
from decouple import config

from services.user_service import register_or_get_user
from services.api_client import APIClient

API_BASE_URL = config('API_BASE_URL', default='http://localhost:8000/api/v1')


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Register or get user
    api_client = APIClient()
    user_data = await register_or_get_user(api_client, user)
    
    # Welcome message based on user's language
    if user_data and user_data.get('preferred_language') == 'ru':
        welcome_text = f"""
🏠 *Добро пожаловать в Family Budget Manager!*

Привет, {user.first_name}! Я помогу вам управлять семейным бюджетом.

*Что я умею:*
• 💰 Отслеживать доходы и расходы
• 📊 Создавать отчеты и аналитику
• 💳 Управлять несколькими счетами
• 🏷 Категоризировать транзакции
• 🌍 Работать с разными валютами
• 🤖 Понимать свободный текст

*Примеры команд:*
`Потратил 50 лари на еду с карты BOG`
`Зарплата 3000 USD наличные`
`/добавь 200 лари еда tbc`

Используйте /help для получения полной справки.
        """
    else:
        welcome_text = f"""
🏠 *Welcome to Family Budget Manager!*

Hi, {user.first_name}! I'll help you manage your family budget.

*What I can do:*
• 💰 Track income and expenses
• 📊 Generate reports and analytics
• 💳 Manage multiple accounts
• 🏷 Categorize transactions
• 🌍 Work with different currencies
• 🤖 Understand natural language

*Example commands:*
`Spent 50 GEL on food from BOG card`
`Salary 3000 USD cash`
`/add 200 GEL food tbc`

Use /help for complete help.
        """
    
    # Inline keyboard with quick actions
    keyboard = [
        [
            InlineKeyboardButton("💰 Add Transaction", callback_data="add_transaction"),
            InlineKeyboardButton("📊 Balance", callback_data="show_balance")
        ],
        [
            InlineKeyboardButton("📈 Reports", callback_data="show_reports"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )