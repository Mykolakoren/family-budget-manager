from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

async def budgets_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /budgets command"""
    keyboard = [
        [InlineKeyboardButton("📊 Family Budget", callback_data='budget_family')],
        [InlineKeyboardButton("📦 Unbox Budget", callback_data='budget_unbox')],
        [InlineKeyboardButton("🎓 Neoschool Budget", callback_data='budget_neoschool')],
        [InlineKeyboardButton("➕ Create New Budget", callback_data='budget_create')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💰 *Your Budgets*\n\nChoose a budget to manage:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def budget_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle budget selection callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'budget_create':
        await query.edit_message_text(
            "➕ *Create New Budget*\n\n"
            "Budget creation feature coming soon!\n"
            "Use /start to return to main menu.",
            parse_mode='Markdown'
        )
    else:
        budget_type = query.data.replace('budget_', '').title()
        await query.edit_message_text(
            f"📊 *{budget_type} Budget*\n\n"
            f"Balance: 0.00 GEL\n"
            f"This month: +0.00 GEL\n\n"
            f"Budget management coming soon!\n"
            f"Use /start to return to main menu.",
            parse_mode='Markdown'
        )

def setup_budget_handlers(application):
    """Setup budget-related handlers"""
    application.add_handler(CommandHandler("budgets", budgets_command))
    application.add_handler(CallbackQueryHandler(budget_callback, pattern="^budget_"))