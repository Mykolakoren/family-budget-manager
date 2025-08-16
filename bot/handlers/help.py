from telegram import Update
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information."""
    user = update.effective_user
    
    help_text = """
🤖 *Family Budget Manager Bot Help*

*Available Commands:*
/start - Start using the bot
/help - Show this help message
/balance - Show account balances  
/accounts - Manage your accounts
/add - Add transaction manually
/report - Generate expense reports
/analytics - View spending analytics

*Natural Language Transaction Examples:*
• `Потратил 50 лари на еду с карты BOG`
• `Зарплата 3000 USD наличные`
• `Bought coffee for 5 GEL from TBC`
• `Freelance payment 500 EUR PayPal`

*Manual Transaction Format:*
`/add <amount> <category> <account> [description]`

*Examples:*
• `/add 50 food bog Lunch at restaurant`
• `/add 3000 salary cash Monthly salary`
• `/add -25 transport tbc Metro ticket`

*Supported Currencies:*
🔸 GEL (Georgian Lari)
🔸 USD (US Dollar)  
🔸 EUR (Euro)
🔸 UAH (Ukrainian Hryvnia)
🔸 USDT (Tether)

*Categories:*
💰 **Income:** salary, freelance, investment, bonus
💸 **Expenses:** food, transport, entertainment, health, clothes, rent, pets, tech

*Account Types:*
🏦 bog, tbc (banks)
💵 cash (cash money)
💳 paypal (PayPal)
🪙 crypto (cryptocurrency wallets)

*Tips:*
• Use natural language for quick entry
• Bot understands multiple languages
• Set your preferred currency in settings
• View reports to track spending patterns

Need more help? Contact support or visit our documentation.
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')