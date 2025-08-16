# Shared schemas and models for the Family Budget Manager

from enum import Enum
from typing import Optional
from datetime import datetime


class CurrencyCode(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GEL = "GEL"
    UAH = "UAH"
    USDT = "USDT"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class AccountType(str, Enum):
    CASH = "cash"
    BANK_CARD = "bank_card"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    CRYPTO = "crypto"
    PAYPAL = "paypal"
    OTHER = "other"


class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


# Common validation patterns
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€", 
    "GEL": "₾",
    "UAH": "₴",
    "USDT": "₮"
}

LANGUAGE_CODES = ["en", "ru", "uk", "ka"]

# Default categories mapping
DEFAULT_CATEGORIES = {
    "income": [
        {"name": "Salary", "icon": "💰", "color": "#4CAF50"},
        {"name": "Freelance", "icon": "💻", "color": "#2196F3"},
        {"name": "Investment", "icon": "📈", "color": "#FF9800"},
        {"name": "Bonus", "icon": "🎁", "color": "#9C27B0"},
        {"name": "Other Income", "icon": "💵", "color": "#607D8B"},
    ],
    "expense": [
        {"name": "Food", "icon": "🍽", "color": "#F44336"},
        {"name": "Transport", "icon": "🚗", "color": "#FF5722"},
        {"name": "Entertainment", "icon": "🎬", "color": "#E91E63"},
        {"name": "Health", "icon": "⚕️", "color": "#009688"},
        {"name": "Clothes", "icon": "👔", "color": "#795548"},
        {"name": "Rent", "icon": "🏠", "color": "#3F51B5"},
        {"name": "Pets", "icon": "🐕", "color": "#CDDC39"},
        {"name": "Technology", "icon": "💻", "color": "#00BCD4"},
        {"name": "Children", "icon": "👶", "color": "#FFC107"},
        {"name": "Debts", "icon": "💳", "color": "#9E9E9E"},
        {"name": "Other Expenses", "icon": "💸", "color": "#757575"},
    ]
}