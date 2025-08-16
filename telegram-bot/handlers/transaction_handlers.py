from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

async def add_transaction_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /add command for manual transaction entry"""
    keyboard = [
        [InlineKeyboardButton("💰 Income", callback_data='trans_income')],
        [InlineKeyboardButton("💸 Expense", callback_data='trans_expense')],
        [InlineKeyboardButton("🔄 Transfer", callback_data='trans_transfer')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💳 *Add Transaction*\n\nSelect transaction type:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /balance command"""
    balance_text = """
💰 *Your Balance*

📊 **Family Budget**: 0.00 GEL
📦 **Unbox Budget**: 0.00 USD  
🎓 **Neoschool Budget**: 0.00 EUR

💱 **Total (GEL equivalent)**: 0.00 GEL

*This Month:*
📈 Income: +0.00 GEL
📉 Expenses: -0.00 GEL
💹 Net: 0.00 GEL
    """
    await update.message.reply_text(balance_text, parse_mode='Markdown')

async def transaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle transaction type selection"""
    query = update.callback_query
    await query.answer()
    
    trans_type = query.data.replace('trans_', '').title()
    
    await query.edit_message_text(
        f"💳 *Add {trans_type}*\n\n"
        f"Please send a message with your transaction details:\n\n"
        f"Examples:\n"
        f"• '50 GEL groceries'\n"
        f"• 'Salary 2000 USD'\n"
        f"• 'Coffee 8.50 GEL at Starbucks'\n\n"
        f"Or use natural language:\n"
        f"'Bought lunch for 25 GEL'",
        parse_mode='Markdown'
    )

def setup_transaction_handlers(application):
    """Setup transaction-related handlers"""
    application.add_handler(CommandHandler("add", add_transaction_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CallbackQueryHandler(transaction_callback, pattern="^trans_"))