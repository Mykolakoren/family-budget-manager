import re
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from typing import Dict, Optional, Tuple

from services.api_client import APIClient
from services.user_service import get_user_token
from utils.text_parser import TransactionParser


async def transaction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle natural language transaction input."""
    user = update.effective_user
    text = update.message.text
    
    try:
        # Get user token
        api_client = APIClient()
        token = await get_user_token(api_client, user.id)
        
        if not token:
            await update.message.reply_text(
                "❌ Please start with /start to register first.",
                parse_mode='Markdown'
            )
            return
        
        # Parse transaction text
        parser = TransactionParser()
        parsed_data = await parser.parse_transaction_text(text, user.id)
        
        if not parsed_data or parsed_data.get('confidence', 0) < 0.5:
            await update.message.reply_text(
                "🤔 I couldn't understand that transaction. Please try:\n"
                "• `Spent 50 GEL on food from BOG card`\n"
                "• `Salary 3000 USD cash`\n"
                "• `/add 200 GEL food tbc`",
                parse_mode='Markdown'
            )
            return
        
        # Create transaction via API
        transaction_data = {
            "amount": parsed_data["amount"],
            "description": parsed_data.get("description", ""),
            "transaction_type": parsed_data["transaction_type"],
            "transaction_date": datetime.now().isoformat(),
            "account_id": parsed_data.get("account_id"),
            "category_id": parsed_data.get("category_id"),
            "original_text": text
        }
        
        api_client.set_auth_token(token)
        response = await api_client.post("/transactions/", json=transaction_data)
        
        if response.status_code == 201:
            transaction = response.json()
            
            # Format success message
            amount_str = f"{transaction['amount']} {parsed_data.get('currency', 'USD')}"
            success_msg = f"""
✅ *Transaction Added Successfully!*

💰 Amount: `{amount_str}`
📝 Description: `{transaction.get('description', 'N/A')}`
🏷 Type: `{transaction['transaction_type'].title()}`
📅 Date: `{transaction['transaction_date'][:10]}`

Use /balance to see your updated balances.
            """
            
            await update.message.reply_text(success_msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "❌ Failed to add transaction. Please try again or use /help for assistance."
            )
            
    except Exception as e:
        await update.message.reply_text(
            "❌ An error occurred while processing your transaction. Please try again."
        )


async def add_transaction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /add command for manual transaction entry."""
    user = update.effective_user
    
    if not context.args:
        help_text = """
💰 *Add Transaction Command*

*Usage:* `/add <amount> <category> <account> [description]`

*Examples:*
• `/add 50 food bog Lunch at restaurant`
• `/add 3000 salary cash Monthly salary`
• `/add -25 transport tbc Metro ticket`

*Supported categories:*
• food, rent, transport, children, health
• entertainment, clothes, pets, debts, tech
• salary, freelance, investment, other

*Account examples:*
• bog, tbc, cash, paypal, crypto
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        return
    
    # Parse command arguments
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "❌ Please provide at least: amount, category, and account.\n"
            "Example: `/add 50 food bog`",
            parse_mode='Markdown'
        )
        return
    
    try:
        amount = float(args[0])
        category = args[1].lower()
        account = args[2].lower()
        description = " ".join(args[3:]) if len(args) > 3 else ""
        
        # Determine transaction type
        transaction_type = "expense" if amount < 0 or category in ["food", "rent", "transport", "entertainment"] else "income"
        if amount < 0:
            amount = abs(amount)
        
        # Get user token and create transaction
        api_client = APIClient()
        token = await get_user_token(api_client, user.id)
        
        if not token:
            await update.message.reply_text("❌ Please start with /start to register first.")
            return
        
        # TODO: Get actual account_id and category_id from API
        # For now, using placeholder values
        transaction_data = {
            "amount": amount,
            "description": description,
            "transaction_type": transaction_type,
            "transaction_date": datetime.now().isoformat(),
            "account_id": 1,  # TODO: Map account name to ID
            "category_id": 1,  # TODO: Map category name to ID
            "original_text": " ".join(["/add"] + args)
        }
        
        api_client.set_auth_token(token)
        response = await api_client.post("/transactions/", json=transaction_data)
        
        if response.status_code == 201:
            await update.message.reply_text(
                f"✅ Added {transaction_type}: {amount} for {category} from {account}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Failed to add transaction.")
            
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid amount. Please enter a valid number.\n"
            "Example: `/add 50 food bog`",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            "❌ An error occurred while adding the transaction."
        )