# Telegram Bot Guide

## Overview

The Family Budget Manager Telegram Bot allows you to manage your budget directly from Telegram using natural language commands and structured commands.

## Getting Started

1. Find your bot on Telegram (ask admin for bot username)
2. Send `/start` to begin
3. Follow the registration process
4. Start adding transactions!

## Commands

### Basic Commands

- `/start` - Start using the bot and register
- `/help` - Show help information
- `/balance` - Show account balances
- `/accounts` - Manage your accounts
- `/report` - Generate monthly report
- `/analytics` - View spending analytics

### Transaction Commands

#### Manual Entry
```
/add <amount> <category> <account> [description]
```

Examples:
```
/add 50 food bog Lunch at restaurant
/add 3000 salary cash Monthly salary payment
/add -25 transport tbc Metro ticket
```

#### Natural Language Input

Just type your transaction naturally:

**English Examples:**
- `Spent 50 GEL on food from BOG card`
- `Salary 3000 USD cash`
- `Bought coffee for 5 EUR`
- `Freelance payment 500 USD PayPal`

**Russian Examples:**
- `Потратил 50 лари на еду с карты BOG`
- `Зарплата 3000 долларов наличными`
- `Купил кофе за 5 лари`
- `Фриланс оплата 500 долларов`

**Georgian Examples:**
- `დავხარჯე 50 ლარი საკვებზე BOG ბარათიდან`
- `ხელფასი 3000 დოლარი ნაღდი`

## Supported Features

### Currencies
- 🇬🇪 GEL (Georgian Lari)
- 🇺🇸 USD (US Dollar)
- 🇪🇺 EUR (Euro)
- 🇺🇦 UAH (Ukrainian Hryvnia)
- 💰 USDT (Tether)

### Categories

**Income Categories:**
- salary - Salary/wages
- freelance - Freelance work
- investment - Investment returns
- bonus - Bonuses
- other - Other income

**Expense Categories:**
- food - Food and dining
- transport - Transportation
- entertainment - Entertainment
- health - Healthcare
- clothes - Clothing
- rent - Rent/housing
- pets - Pet expenses
- tech - Technology
- other - Other expenses

### Account Types
- **bog** - Bank of Georgia
- **tbc** - TBC Bank
- **cash** - Cash money
- **paypal** - PayPal account
- **crypto** - Cryptocurrency wallets

## Advanced Features

### Recurring Transactions
Set up recurring transactions for regular income/expenses:
```
/recurring add 1500 salary cash monthly
/recurring add 500 rent bog monthly
```

### Budget Limits
Set monthly spending limits:
```
/limit food 800
/limit entertainment 200
```

### Analytics
Get detailed analytics:
```
/analytics food - Food spending this month
/analytics month - This month's summary
/analytics year - Year overview
```

### Multi-Language Support

The bot supports multiple languages. Change your language:
```
/language en - English
/language ru - Russian
/language uk - Ukrainian  
/language ka - Georgian
```

## Natural Language Processing

The bot uses AI to understand your natural language input. It can recognize:

- **Amount**: Numbers with or without currency
- **Category**: Food items, transport mentions, etc.
- **Account**: Bank names, "cash", "card"
- **Transaction type**: Spending vs income keywords
- **Description**: Context and details

### Examples of Smart Recognition

Input: `"Coffee 5 lari tbc"`
- Amount: 5
- Currency: GEL
- Category: food (coffee → food)
- Account: tbc
- Type: expense

Input: `"Salary 2500 dollars cash"`
- Amount: 2500  
- Currency: USD
- Category: salary
- Account: cash
- Type: income

## Tips for Better Recognition

1. **Include currency**: "50 GEL" or "25 dollars"
2. **Mention account**: "from BOG card", "cash", "PayPal"
3. **Use clear categories**: "food", "transport", "salary"
4. **Be specific**: "Lunch 25 GEL BOG" vs just "25"

## Troubleshooting

### Bot Not Responding
- Check if bot is online
- Try `/start` command
- Make sure you're registered

### Transaction Not Recognized
- Use manual `/add` command
- Include currency and account
- Check spelling of categories

### Wrong Account/Category
- Edit transaction in web interface
- Use manual commands for precision
- Update your preferred settings

## Privacy and Security

- All data is encrypted in transit
- Bot doesn't store message history
- Only transaction data is saved
- You can delete your data anytime

## Getting Help

- `/help` - In-bot help
- Contact support: @support_username
- Web interface: http://localhost:3000
- Documentation: Check project README

## Pro Tips

1. **Use shortcuts**: Set up common transactions as templates
2. **Regular updates**: Check balances weekly with `/balance`
3. **Monthly reviews**: Use `/report` to track spending
4. **Set limits**: Use budget limits to control spending
5. **Multiple accounts**: Track different wallets and cards