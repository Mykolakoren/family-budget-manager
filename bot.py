response = f"""
🏠 **Семейная группа:** {family_data['name']}
🆔 **ID группы:** `{family_data['id']}`

👥 **Участники ({len(family_data['members'])}):**
{members_info}

📊 **Общая статистика:**
💸 Транзакций: {family_stats['total_transactions']}
💰 Общий баланс: {family_stats['total_balance']:.2f} лари
📈 Доходы: {family_stats['total_income']:.2f} лари
📉 Расходы: {family_stats['total_expenses']:.2f} лари

**Команды:**
• `/family_invite` - пригласить члена семьи
• `/family_stats` - детальная статистика
• `/family_leave` - покинуть группу
            """

await update.message.reply_text(response, parse_mode='Markdown')
else:
keyboard = [
    [
        InlineKeyboardButton("🏠 Создать семью", callback_data="create_family"),
        InlineKeyboardButton("👥 Присоединиться", callback_data="join_family")
    ]
]
reply_markup = InlineKeyboardMarkup(keyboard)

await update.message.reply_text(
    "🏠 **Семейный бюджет**\n\n"
    "Создайте семейную группу для ведения общего бюджета!\n\n"
    "**Преимущества:**\n"
    "• 👥 Общие транзакции для всей семьи\n"
    "• 📊 Совместная статистика и анализ\n"
    "• 🤖 ИИ обучается на данных всей семьи\n"
    "• 📈 Отчеты по дням, неделям, месяцам\n\n"
    "Выберите действие:",
    reply_markup=reply_markup,
    parse_mode='Markdown'
)


async def family_invite_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users_data = self.db.load_data()
    family_data = self.family_manager.get_family_data(user_id, users_data)

    if not family_data:
        await update.message.reply_text("❌ Вы не состоите в семейной группе. Используйте /family")
        return

    if family_data['created_by'] != user_id:
        await update.message.reply_text("❌ Только админ группы может приглашать участников")
        return

    bot_username = context.bot.username or "YourBotName"
    invite_text = f"""
🏠 **Приглашение в семейную группу**

**Название:** {family_data['name']}
**ID группы:** `{family_data['id']}`

📋 **Инструкция для присоединения:**
1. Запустите бота @{bot_username}
2. Отправьте команду `/family`
3. Нажмите "👥 Присоединиться"
4. Введите ID группы: `{family_data['id']}`

✅ После присоединения вы будете видеть все семейные транзакции!
        """

    await update.message.reply_text(invite_text, parse_mode='Markdown')


async def family_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    stats = self.family_manager.get_detailed_family_stats(user_id)

    if not stats:
        await update.message.reply_text("❌ Вы не состоите в семейной группе или нет транзакций. Используйте /family")
        return

    response = f"""
🏠 **Детальная семейная статистика**

📅 **За неделю:**
💸 Расходы: {stats['week']['expenses']:.2f} лари
💰 Доходы: {stats['week']['income']:.2f} лари
💎 Баланс: {stats['week']['balance']:+.2f} лари

📅 **За месяц:**
💸 Расходы: {stats['month']['expenses']:.2f} лари
💰 Доходы: {stats['month']['income']:.2f} лари
💎 Баланс: {stats['month']['balance']:+.2f} лари

👥 **По участникам (месяц):**
"""

    for member, member_stats in stats['by_member'].items():
        response += f"• {member}: {member_stats['count']} транзакций, {member_stats['expenses']:.0f} лари расходов\n"

    if stats['top_categories']:
        response += f"\n🔥 **Топ категории (месяц):**\n"
        for category, amount in stats['top_categories']:
            response += f"• {category}: {amount:.2f} лари\n"

    response += f"\n🤖 Команда /analyze для ИИ анализа семейных трат"

    await update.message.reply_text(response, parse_mode='Markdown')


async def family_leave_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users_data = self.db.load_data()
    family_data = self.family_manager.get_family_data(user_id, users_data)

    if not family_data:
        await update.message.reply_text("❌ Вы не состоите в семейной группе")
        return

    keyboard = [
        [
            InlineKeyboardButton("✅ Да, покинуть", callback_data="confirm_leave_family"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_leave_family")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"⚠️ **Подтверждение**\n\n"
        f"Вы действительно хотите покинуть группу **{family_data['name']}**?\n\n"
        f"После выхода вы не будете видеть семейные транзакции.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    transactions = self.family_manager.get_family_transactions(user_id)

    if not transactions:
        users_data = self.db.load_data()
        family_data = self.family_manager.get_family_data(user_id, users_data)
        if family_data:
            await update.message.reply_text("📊 Пока нет семейных транзакций. Добавьте первую!")
        else:
            await update.message.reply_text(
                "📊 Пока нет транзакций.\n\n"
                "💡 **Совет:** Используйте /family для создания семейной группы!"
            )
        return

    balances = {}
    for trans in transactions:
        account = trans.get('account', 'Неизвестно')
        amount = trans.get('amount', 0)
        currency = trans.get('currency', 'GEL')

        key = f"{account} ({currency})"
        if key not in balances:
            balances[key] = 0
        balances[key] += amount

    users_data = self.db.load_data()
    family_data = self.family_manager.get_family_data(user_id, users_data)
    if family_data:
        balance_text = f"🏠 **{family_data['name']}**\n\n💰 **Баланс счетов:**\n\n"
    else:
        balance_text = "💰 **Баланс счетов:**\n\n"

    for account, balance in balances.items():
        emoji = "💳" if "Card" in account else "💵"
        balance_text += f"{emoji} {account}: {balance:,.2f}\n"

    total_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
    total_expense = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)

    balance_text += f"\n📈 Доходы: {total_income:,.2f}\n"
    balance_text += f"📉 Расходы: {total_expense:,.2f}\n"
    balance_text += f"💎 Баланс: {total_income - total_expense:,.2f}\n\n"

    if family_data:
        balance_text += f"👥 Участников в семье: {len(family_data['members'])}\n"
        balance_text += f"📊 Команда /family_stats для детальной статистики"
    else:
        balance_text += f"💡 Команда /family для создания семейной группы"

    await update.message.reply_text(balance_text, parse_mode='Markdown')


async def smart_analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    transactions = self.family_manager.get_family_transactions(user_id)

    if len(transactions) < 5:
        users_data = self.db.load_data()
        family_data = self.family_manager.get_family_data(user_id, users_data)
        family_hint = "\n• Создайте семейную группу через /family" if not family_data else ""

        await update.message.reply_text(
            "🤖 **Для ИИ анализа нужно минимум 5 транзакций.**\n\n"
            "Добавьте еще несколько:\n"
            "• \"Потратил 50 лари на еду\"\n"
            "• Пришлите файл выписки\n"
            "• /balance для просмотра текущих данных" + family_hint
        )
        return

    await update.message.reply_text("🤖 **ИИ анализирует данные...**\nДай мне секундочку! 🧠")

    analysis = await self.ai_analyzer.analyze_spending_patterns(transactions)

    user_data = self.get_user_data(user_id)
    learning_stats = user_data['ai_learning']

    users_data = self.db.load_data()
    family_data = self.family_manager.get_family_data(user_id, users_data)
    family_prefix = f"🏠 **{family_data['name']}** - " if family_data else ""

    mood_emoji = {
        'positive': '😊',
        'neutral': '😐',
        'concern': '😟'
    }

    emoji = mood_emoji.get(analysis['mood'], '🤖')

    response = f"{emoji} **{family_prefix}Персональный ИИ анализ:**\n\n"
    response += f"📊 {analysis['analysis']}\n\n"
    response += f"🔥 **Топ категория:** {analysis['top_category']}\n\n"
    response += "💡 **ИИ рекомендации:**\n"

    for i, advice in enumerate(analysis['advice'], 1):
        response += f"{i}. {advice}\n"

    response += f"\n🧠 **Обучение ИИ:**\n"
    response += f"• Изучено {len(learning_stats['category_preferences'])} слов\n"
    response += f"• Запомнено {len(learning_stats['merchant_categories'])} мест\n"
    response += f"• Общий опыт: {learning_stats['learning_score']} примеров\n\n"

    if family_data:
        response += f"👥 **Семейная группа:** {len(family_data['members'])} участников\n"
        response += f"📊 /family_stats для детальной семейной статистики\n\n"

    response += f"🎯 **Точность ИИ растет с каждой транзакцией!**"

    await update.message.reply_text(response, parse_mode='Markdown')


async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user_data = self.get_user_data(user_id)

    if user_data.get('waiting_for_family_id'):
        family_id = text.strip()

        users_data = self.db.load_data()
        users_data[str(user_id)]['family_id'] = family_id
        users_data[str(user_id)]['family_role'] = 'member'
        self.users_data = users_data

        if self.family_manager.join_family_group(user_id, family_id):
            users_data = self.db.load_data()
            family_data = self.family_manager.get_family_data(user_id, users_data)
            await update.message.reply_text(
                f"🏠 **Добро пожаловать в семью!**\n\n"
                f"**Группа:** {family_data['name']}\n"
                f"👥 **Участников:** {len(family_data['members'])}\n\n"
                f"✅ Теперь вы видите все семейные транзакции!\n"
                f"📊 Используйте /balance для просмотра общего баланса"
            )
        else:
            await update.message.reply_text(
                f"❌ **Группа не найдена**\n\n"
                f"Проверьте правильность ID: `{family_id}`\n"
                f"Попробуйте еще раз или обратитесь к админу группы"
            )

        del user_data['waiting_for_family_id']
        self.save_data()
        return

    text_lower = text.lower()
    if any(word in text_lower for word in ['потратил', 'купил', 'заплатил']):
        await self.ai_parse_expense(update, context)
    elif any(word in text_lower for word in ['получил', 'зарплата', 'доход']):
        await self.ai_parse_income(update, context)
    elif any(word in text_lower for word in ['сколько', 'баланс', 'отчет', 'покажи', 'топ']):
        await self.handle_question(update, context)
    else:
        await update.message.reply_text(
            "🤔 Попробуй:\n"
            "• \"Потратил 50 лари в Carrefour\" - ИИ запомнит!\n"
            "• \"Получил зарплату 1000 долларов\"\n"
            "• Пришли файл выписки 📎\n"
            "• /family для настройки семейного бюджета 🏠\n"
            "• /analyze для ИИ анализа 🤖"
        )


async def ai_parse_expense(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user_data = self.get_user_data(user_id)

    personal_suggestion = self.get_learned_suggestion(user_id, text)

    if personal_suggestion and personal_suggestion['confidence'] > 0.8:
        parsed = await self.simple_parse_transaction(text)
        if parsed:
            parsed.update(personal_suggestion)
            parsed['source'] = 'personal_ai'
    else:
        parsed = await self.ai_parse_transaction(text, user_data)
        if parsed:
            parsed['source'] = 'openai'

    if not parsed:
        await update.message.reply_text("🤔 Не смог распознать транзакцию")
        return

    current_transactions = self.family_manager.get_family_transactions(user_id)
    transaction = {
        'id': len(current_transactions) + 1,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        **parsed
    }

    if self.add_transaction(user_id, transaction, user_data.get('name')):
        source_text = "Персональный ИИ" if parsed.get('source') == 'personal_ai' else "ИИ"
        reasoning = f" ({parsed.get('reasoning', '')})" if 'reasoning' in parsed else ""

        users_data = self.db.load_data()
        family_data = self.family_manager.get_family_data(user_id, users_data)
        family_info = f" в группу **{family_data['name']}**" if family_data else ""

        await update.message.reply_text(
            f"✅ **{source_text} добавил:**{reasoning}\n\n"
            f"💸 {parsed['amount']:+.2f} {parsed['currency']}\n"
            f"🏷️ {parsed['category']}\n"
            f"💳 {parsed['account']}\n\n"
            f"🧠 Уверенность: {parsed['confidence'] * 100:.0f}%\n"
            f"💾 Сохранено{family_info}"
        )
    else:
        await update.message.reply_text("❌ Ошибка сохранения в базу данных")


async def simple_parse_transaction(self, text: str) -> Optional[Dict]:
    amount_match = re.search(r'(\d+(?:\.\d+)?)', text)
    if not amount_match:
        return None

    amount = float(amount_match.group(1))
    is_expense = any(word in text.lower() for word in ['потратил', 'купил', 'заплатил'])

    return {
        'amount': -amount if is_expense else amount,
        'currency': 'GEL',
        'category': 'Прочее',
        'account': 'Наличные',
        'description': text,
        'type': 'expense' if is_expense else 'income',
        'confidence': 0.5
    }


async def ai_parse_transaction(self, text: str, user_data: dict) -> Optional[Dict]:
    if not self.ai_analyzer.enabled:
        return await self.simple_parse_transaction(text)

    try:
        amount_match = re.search(r'(\d+(?:\.\d+)?)', text)
        amount = float(amount_match.group(1)) if amount_match else None

        if not amount:
            return None

        is_expense = any(word in text.lower() for word in ['потратил', 'купил', 'заплатил', 'потрачено'])
        if not is_expense:
            is_expense = not any(word in text.lower() for word in ['получил', 'зарплата', 'доход', 'заработал'])

        amount = -amount if is_expense else amount

        categorization = await self.ai_analyzer.smart_categorize(
            description=text,
            amount=amount,
            user_history=user_data.get('transactions', []),
            user_preferences=user_data.get('ai_learning', {})
        )

        currency = 'GEL'
        if any(word in text.lower() for word in ['доллар', 'usd', 'import logging
        from datetime import datetime, timedelta
        import json
        import re
        import io
        import os
        import csv
        import uuid
        from typing import Dict, List, Optional
        from collections import defaultdict, Counter


try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

    print("✅ Telegram библиотека найдена")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Выполни: python3 -m pip install python-telegram-bot==20.6")
    exit(1)

try:
    import pandas as pd
    import PyPDF2

    print("✅ Библиотеки для файлов найдены")
except ImportError as e:
    print(f"⚠️ Библиотеки для файлов не найдены: {e}")

try:
    from openai import OpenAI

    print("✅ OpenAI библиотека найдена")
except ImportError as e:
    print(f"⚠️ OpenAI не найдена: {e}")

try:
    from config import TELEGRAM_TOKEN, DEFAULT_CATEGORIES, DEFAULT_ACCOUNTS, OPENAI_API_KEY

    print("✅ Конфигурация загружена")
except ImportError:
    print("❌ Файл config.py не найден")
    exit(1)

if not TELEGRAM_TOKEN:
    print("❌ Ошибка: Не настроен TELEGRAM_TOKEN в config.py")
    exit(1)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class AIAnalyzer:
    def __init__(self, api_key):
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.enabled = True
                print("✅ OpenAI API подключен")
            except Exception as e:
                self.client = None
                self.enabled = False
                print(f"❌ Ошибка подключения OpenAI: {e}")
        else:
            self.client = None
            self.enabled = False
            print("⚠️ OpenAI API не настроен")

    async def smart_categorize(self, description, amount, user_history=None, user_preferences=None):
        if not self.enabled:
            return self.fallback_categorize(description, amount < 0)

        try:
            if user_preferences:
                personal_match = self.check_personal_preferences(description, user_preferences)
                if personal_match and personal_match['confidence'] > 0.8:
                    return personal_match

            history_context = ""
            if user_history:
                similar_transactions = self.find_similar_transactions(description, user_history)
                if similar_transactions:
                    history_context = f"\nИстория похожих трат пользователя:\n"
                    for trans in similar_transactions[:3]:
                        history_context += f"- '{trans['description']}' → {trans['category']}\n"

            prompt = f"""
Проанализируй транзакцию и определи категорию.

Транзакция: "{description}"
Сумма: {amount} лари
Тип: {'расход' if amount < 0 else 'доход'}

{history_context}

Доступные категории расходов:
- Еда (продукты, рестораны, кафе, доставка)
- Транспорт (такси, бензин, общественный транспорт, парковка)
- Развлечения (кино, театр, игры, хобби, спорт)
- Здоровье (аптека, врачи, медицина, спорт зал)
- Одежда (одежда, обувь, аксессуары)
- Техника (электроника, софт, гаджеты)
- Прочее

Доступные категории доходов:
- Зарплата, Фриланс, Бизнес, Инвестиции, Подарки, Возврат, Кешбэк, Прочее

Ответь в JSON формате:
{{
    "category": "название_категории",
    "confidence": 0.95,
    "reasoning": "краткое объяснение выбора"
}}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.1
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"AI categorization error: {e}")
            return self.fallback_categorize(description, amount < 0)

    def check_personal_preferences(self, description, user_preferences):
        description_lower = description.lower()
        category_scores = {}

        for merchant, category in user_preferences.get('merchant_categories', {}).items():
            if merchant in description_lower:
                return {
                    'category': category,
                    'confidence': 0.95,
                    'reasoning': f'Ты всегда относишь {merchant} к категории {category}'
                }

        words = description_lower.split()
        for word in words:
            if word in user_preferences.get('category_preferences', {}):
                for category, count in user_preferences['category_preferences'][word].items():
                    category_scores[category] = category_scores.get(category, 0) + count

        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            confidence = min(0.9, best_category[1] / 5)
            if confidence > 0.7:
                return {
                    'category': best_category[0],
                    'confidence': confidence,
                    'reasoning': f'На основе твоей истории ({best_category[1]} совпадений)'
                }

        return None

    def find_similar_transactions(self, description, history):
        description_lower = description.lower()
        similar = []

        for trans in history[-50:]:
            trans_desc = trans.get('description', '').lower()
            desc_words = set(description_lower.split())
            trans_words = set(trans_desc.split())
            common_words = desc_words.intersection(trans_words)

            if len(common_words) >= 1:
                similarity = len(common_words) / max(len(desc_words), len(trans_words))
                if similarity > 0.3:
                    similar.append({
                        'description': trans.get('description', ''),
                        'category': trans.get('category', ''),
                        'similarity': similarity
                    })

        similar.sort(key=lambda x: x['similarity'], reverse=True)
        return similar

    def fallback_categorize(self, description, is_expense=True):
        desc_lower = description.lower()

        if not is_expense:
            if any(word in desc_lower for word in ['salary', 'зарплата', 'заработок']):
                return {'category': 'Зарплата', 'confidence': 0.8, 'reasoning': 'Ключевые слова'}
            return {'category': 'Прочее', 'confidence': 0.5, 'reasoning': 'По умолчанию'}

        categories = {
            'Еда': ['carrefour', 'spar', 'restaurant', 'cafe', 'кафе', 'ресторан', 'еда', 'продукт', 'agrohub'],
            'Транспорт': ['taxi', 'bolt', 'uber', 'gpc', 'такси', 'бензин', 'метро', 'автобус'],
            'Развлечения': ['cinema', 'theatre', 'game', 'кино', 'театр', 'развлечения', 'игра'],
            'Здоровье': ['pharmacy', 'hospital', 'doctor', 'аптека', 'больница', 'врач'],
            'Одежда': ['clothing', 'clothes', 'одежда', 'обувь'],
            'Техника': ['cellfie', 'mobile', 'internet', 'интернет', 'техника']
        }

        for category, keywords in categories.items():
            if any(keyword in desc_lower for keyword in keywords):
                return {'category': category, 'confidence': 0.7, 'reasoning': 'Ключевые слова'}

        return {'category': 'Прочее', 'confidence': 0.5, 'reasoning': 'Не определено'}

    async def analyze_spending_patterns(self, transactions):
        if not self.enabled or len(transactions) < 10:
            return self.simple_analysis(transactions)

        try:
            expenses = [t for t in transactions if t['amount'] < 0]
            by_category = defaultdict(list)
            for trans in expenses[-30:]:
                by_category[trans['category']].append(abs(trans['amount']))

            stats = {}
            for category, amounts in by_category.items():
                stats[category] = {
                    'total': sum(amounts),
                    'count': len(amounts),
                    'avg': sum(amounts) / len(amounts)
                }

            prompt = f"""
Проанализируй траты пользователя и дай персональные советы.

Статистика трат за последний период:
{json.dumps(stats, indent=2, ensure_ascii=False)}

Общая сумма расходов: {sum(abs(t['amount']) for t in expenses[-30:])} лари
Количество транзакций: {len(expenses[-30:])}

Дай краткий анализ (2-3 предложения) и 2-3 конкретных совета по оптимизации бюджета.
Будь дружелюбным и конструктивным.

Ответь в JSON формате:
{{
    "analysis": "краткий анализ трат",
    "top_category": "категория с наибольшими тратами",
    "advice": [
        "первый совет",
        "второй совет",
        "третий совет"
    ],
    "mood": "positive/neutral/concern"
}}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"AI analysis error: {e}")
            return self.simple_analysis(transactions)

    def simple_analysis(self, transactions):
        expenses = [t for t in transactions if t['amount'] < 0]

        if not expenses:
            return {
                "analysis": "Пока недостаточно данных для анализа",
                "top_category": "Нет данных",
                "advice": ["Добавьте больше транзакций для анализа"],
                "mood": "neutral"
            }

        by_category = defaultdict(float)
        for trans in expenses[-30:]:
            by_category[trans['category']] += abs(trans['amount'])

        top_category = max(by_category.items(), key=lambda x: x[1])[0] if by_category else "Прочее"
        total = sum(by_category.values())

        return {
            "analysis": f"За последний период потрачено {total:.2f} лари. Больше всего уходит на категорию '{top_category}'.",
            "top_category": top_category,
            "advice": [
                "Отслеживайте крупные траты",
                "Установите лимиты по категориям",
                "Анализируйте паттерны еженедельно"
            ],
            "mood": "neutral"
        }


class DatabaseManager:
    def __init__(self, data_file="budget_data.json"):
        self.data_file = data_file
        self.backup_file = f"{data_file}.backup"

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ База данных загружена из {self.data_file}")
                return data
            else:
                print(f"📝 Создается новая база данных: {self.data_file}")
                return {}
        except Exception as e:
            print(f"❌ Ошибка загрузки БД: {e}")
            return {}

    def save_data(self, data):
        try:
            if os.path.exists(self.data_file):
                import shutil
                shutil.copy2(self.data_file, self.backup_file)

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            file_size = os.path.getsize(self.data_file)
            print(f"💾 БД сохранена: {file_size} байт")
            return True

        except Exception as e:
            print(f"❌ Ошибка сохранения БД: {e}")
            return False

    def export_user_data(self, user_data, format='csv'):
        if format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Дата', 'Сумма', 'Валюта', 'Категория', 'Счет', 'Описание', 'Тип'])

            for transaction in user_data.get('transactions', []):
                writer.writerow([
                    transaction.get('date', ''),
                    transaction.get('amount', 0),
                    transaction.get('currency', 'GEL'),
                    transaction.get('category', ''),
                    transaction.get('account', ''),
                    transaction.get('description', ''),
                    transaction.get('type', '')
                ])

            return output.getvalue().encode('utf-8')

        elif format == 'json':
            return json.dumps(user_data, ensure_ascii=False, indent=2).encode('utf-8')


class FamilyManager:
    def __init__(self, database_manager):
        self.db = database_manager

    def create_family_group(self, creator_user_id, family_name="Семейный бюджет"):
        family_id = str(uuid.uuid4())[:8]

        family_data = {
            'id': family_id,
            'name': family_name,
            'created_by': creator_user_id,
            'created_at': datetime.now().isoformat(),
            'members': [creator_user_id],
            'transactions': [],
            'settings': {
                'default_currency': 'GEL',
                'shared_categories': True,
                'notification_enabled': True
            }
        }

        users_data = self.db.load_data()
        if 'families' not in users_data:
            users_data['families'] = {}

        users_data['families'][family_id] = family_data
        self.db.save_data(users_data)
        return family_id

    def join_family_group(self, user_id, family_id):
        users_data = self.db.load_data()

        if 'families' not in users_data or family_id not in users_data['families']:
            return False

        family_data = users_data['families'][family_id]

        if user_id not in family_data['members']:
            family_data['members'].append(user_id)
            self.db.save_data(users_data)
            return True

        return False

    def get_family_data(self, user_id, users_data=None):
        if users_data is None:
            users_data = self.db.load_data()

        user_id_str = str(user_id)
        if user_id_str not in users_data:
            return None

        family_id = users_data[user_id_str].get('family_id')

        if not family_id or 'families' not in users_data:
            return None

        return users_data['families'].get(family_id)

    def get_family_transactions(self, user_id):
        users_data = self.db.load_data()
        family_data = self.get_family_data(user_id, users_data)

        if not family_data:
            user_id_str = str(user_id)
            if user_id_str in users_data:
                return users_data[user_id_str].get('transactions', [])
            return []

        return family_data.get('transactions', [])

    def add_family_transaction(self, user_id, transaction, user_name):
        users_data = self.db.load_data()
        family_data = self.get_family_data(user_id, users_data)

        if not family_data:
            return False

        transaction['added_by'] = user_id
        transaction['added_by_name'] = user_name

        family_data['transactions'].append(transaction)

        if self.db.save_data(users_data):
            print(f"💾 Семейная транзакция сохранена от пользователя {user_id}")
            return True
        return False

    def get_family_statistics(self, user_id):
        transactions = self.get_family_transactions(user_id)

        total_transactions = len(transactions)
        total_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
        total_expenses = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
        total_balance = total_income - total_expenses

        return {
            'total_transactions': total_transactions,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_balance': total_balance
        }

    def get_detailed_family_stats(self, user_id):
        users_data = self.db.load_data()
        family_data = self.get_family_data(user_id, users_data)
        if not family_data:
            return None

        transactions = family_data.get('transactions', [])

        if not transactions:
            return None

        today = datetime.now()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        week_transactions = []
        month_transactions = []

        for trans in transactions:
            try:
                trans_date = datetime.strptime(trans['date'][:10], '%Y-%m-%d')
                if trans_date >= week_ago:
                    week_transactions.append(trans)
                if trans_date >= month_ago:
                    month_transactions.append(trans)
            except:
                continue

        week_expenses = sum(abs(t['amount']) for t in week_transactions if t['amount'] < 0)
        month_expenses = sum(abs(t['amount']) for t in month_transactions if t['amount'] < 0)

        week_income = sum(t['amount'] for t in week_transactions if t['amount'] > 0)
        month_income = sum(t['amount'] for t in month_transactions if t['amount'] > 0)

        by_member = defaultdict(lambda: {'expenses': 0, 'income': 0, 'count': 0})
        for trans in month_transactions:
            member_name = trans.get('added_by_name', 'Неизвестно')
            by_member[member_name]['count'] += 1
            if trans['amount'] < 0:
                by_member[member_name]['expenses'] += abs(trans['amount'])
            else:
                by_member[member_name]['income'] += trans['amount']

        by_category = defaultdict(float)
        for trans in month_transactions:
            if trans['amount'] < 0:
                by_category[trans['category']] += abs(trans['amount'])

        top_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'family_data': family_data,
            'week': {
                'expenses': week_expenses,
                'income': week_income,
                'balance': week_income - week_expenses
            },
            'month': {
                'expenses': month_expenses,
                'income': month_income,
                'balance': month_income - month_expenses
            },
            'by_member': dict(by_member),
            'top_categories': top_categories
        }

    def leave_family(self, user_id):
        users_data = self.db.load_data()
        family_data = self.get_family_data(user_id, users_data)
        if not family_data:
            return False

        family_id = family_data['id']

        if user_id in family_data['members']:
            family_data['members'].remove(user_id)

        user_id_str = str(user_id)
        if user_id_str in users_data:
            user_data = users_data[user_id_str]
            if 'family_id' in user_data:
                del user_data['family_id']
            if 'family_role' in user_data:
                del user_data['family_role']

        if not family_data['members']:
            del users_data['families'][family_id]

        self.db.save_data(users_data)
        return True


class BudgetBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.users_data = self.db.load_data()

        self.categories = DEFAULT_CATEGORIES
        self.accounts = DEFAULT_ACCOUNTS

        self.ai_analyzer = AIAnalyzer(OPENAI_API_KEY)
        self.family_manager = FamilyManager(self.db)

        print(f"📊 Бот инициализирован с {len(self.users_data)} пользователей")

    def get_user_data(self, user_id):
        user_id_str = str(user_id)

        if user_id_str not in self.users_data:
            self.users_data[user_id_str] = {
                'transactions': [],
                'active_budget': 'Семейный',
                'ai_learning': {
                    'category_preferences': {},
                    'merchant_categories': {},
                    'total_interactions': 0,
                    'learning_score': 0
                },
                'settings': {
                    'default_currency': 'GEL',
                    'auto_save': True,
                    'ai_enabled': True
                },
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat()
            }
            self.save_data()

        self.users_data[user_id_str]['last_activity'] = datetime.now().isoformat()
        return self.users_data[user_id_str]

    def save_data(self):
        return self.db.save_data(self.users_data)

    def add_transaction(self, user_id, transaction, user_name=None):
        users_data = self.db.load_data()
        family_data = self.family_manager.get_family_data(user_id, users_data)

        if family_data:
            if not user_name:
                user_name = users_data[str(user_id)].get('name', f'Пользователь {str(user_id)[-4:]}')
            return self.family_manager.add_family_transaction(user_id, transaction, user_name)
        else:
            user_data = self.get_user_data(user_id)
            user_data['transactions'].append(transaction)

            self.learn_from_transaction(user_id, transaction)

            if self.save_data():
                print(f"💾 Личная транзакция сохранена для пользователя {user_id}")
                return True
            return False

    def learn_from_transaction(self, user_id, transaction):
        user_data = self.get_user_data(user_id)
        ai_learning = user_data['ai_learning']

        description = transaction.get('description', '').lower()
        category = transaction.get('category', '')

        if not description or not category:
            return

        keywords = [word for word in description.split() if len(word) > 2]

        for keyword in keywords:
            if keyword not in ai_learning['category_preferences']:
                ai_learning['category_preferences'][keyword] = {}

            if category not in ai_learning['category_preferences'][keyword]:
                ai_learning['category_preferences'][keyword][category] = 0

            ai_learning['category_preferences'][keyword][category] += 1

        merchants = ['carrefour', 'spar', 'agrohub', 'big chefs', 'bolt', 'tbc', 'bog',
                     'gpc', 'grand mall', 'cellfie', 'merkuri', 'dona']

        for merchant in merchants:
            if merchant in description:
                ai_learning['merchant_categories'][merchant] = category
                break

        ai_learning['learning_score'] += 1
        print(f"🧠 ИИ изучил: {description[:30]}... → {category}")

    def get_learned_suggestion(self, user_id, description):
        user_data = self.get_user_data(user_id)
        ai_learning = user_data['ai_learning']

        description_lower = description.lower()
        category_scores = {}

        for merchant, category in ai_learning['merchant_categories'].items():
            if merchant in description_lower:
                return {
                    'category': category,
                    'confidence': 0.95,
                    'reasoning': f'Ты всегда относишь {merchant.title()} к категории {category}'
                }

        words = description_lower.split()
        for word in words:
            if word in ai_learning['category_preferences']:
                for category, count in ai_learning['category_preferences'][word].items():
                    category_scores[category] = category_scores.get(category, 0) + count

        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            confidence = min(0.9, best_category[1] / 5)

            if confidence > 0.6:
                return {
                    'category': best_category[0],
                    'confidence': confidence,
                    'reasoning': f'На основе твоего обучения ({best_category[1]} примеров)'
                }

        return None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_data = self.get_user_data(user.id)
        user_data['name'] = user.first_name

        transactions = self.family_manager.get_family_transactions(user.id)
        total_transactions = len(transactions)
        learning_score = user_data['ai_learning']['learning_score']

        users_data = self.db.load_data()
        family_data = self.family_manager.get_family_data(user.id, users_data)
        family_info = f"\n🏠 **Семья:** {family_data['name']}" if family_data else "\n💡 **Совет:** Создайте семейную группу через /family"

        welcome_text = f"""
👋 Привет, {user.first_name}!

Я умный помощник для семейного бюджета с персональным обучением!{family_info}

🔥 **Твоя статистика:**
📊 Транзакций: {total_transactions}
🧠 ИИ обучение: {learning_score} примеров

🤖 **ИИ возможности:**
• Умная категоризация с обучением
• Персональные советы и анализ
• Запоминание твоих предпочтений
• Обработка банковских выписок

**Команды:**
/family - 🏠 семейный бюджет
/analyze - 🧠 ИИ анализ трат
/stats - 📊 статистика обучения
/export - 📤 экспорт данных
/balance - 💰 баланс счетов

**Попробуй:**
• "Потратил 50 лари на еду в Carrefour"
• Пришли файл выписки 📎
        """

        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    async def family_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name

        user_data = self.get_user_data(user_id)
        user_data['name'] = user_name

        users_data = self.db.load_data()
        family_data = self.family_manager.get_family_data(user_id, users_data)

        if family_data:
            members_info = ""
            for member_id in family_data['members']:
                member_name = users_data.get(str(member_id), {}).get('name', f'Пользователь {str(member_id)[-4:]}')
                role = "👑 Админ" if member_id == family_data['created_by'] else "👤 Участник"
                members_info += f"• {member_name} - {role}\n"

            family_stats = self.family_manager.get_family_statistics(user_id)

            response = f"""]):
                currency = 'USD'
            elif any(word in text.lower() for word in ['евро', 'eur', '€']):
                currency = 'EUR'

            account = 'Наличные'
            if 'bog' in text.lower():
                account = 'BOG Card'
            elif 'tbc' in text.lower():
                account = 'TBC Card'
            elif 'карт' in text.lower():
                account = 'Банковская карта'

            return {
            'amount': amount,
                'currency': currency,
                'category': categorization['category'],
                'account': account,
                'description': text,
                'type': 'expense' if amount < 0 else 'income',
                'confidence': categorization['confidence'],
                'reasoning': categorization.get('reasoning', '')
            }

        except Exception as e:
            logger.error(f"AI parsing error: {e}")
            return await self.simple_parse_transaction(text)

    async def ai_parse_income(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        user_id = update.effective_user.id
        user_data = self.get_user_data(user_id)

        parsed = await self.ai_parse_transaction(text, user_data)

        if not parsed:
            await update.message.reply_text("🤔 Не смог распознать доход")
            return

        parsed['amount'] = abs(parsed['amount'])
        parsed['type'] = 'income'

        current_transactions = self.family_manager.get_family_transactions(user_id)
        transaction = {
            'id': len(current_transactions) + 1,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            **parsed
        }

        if self.add_transaction(user_id, transaction, user_data.get('name')):
            reasoning = f" ({parsed.get('reasoning', '')})" if 'reasoning' in parsed else ""

            users_data = self.db.load_data()
            family_data = self.family_manager.get_family_data(user_id, users_data)
            family_info = f" в группу **{family_data['name']}**" if family_data else ""

            await update.message.reply_text(
                f"✅ **ИИ добавил доход:**{reasoning}\n\n"
                f"💰 +{parsed['amount']:.2f} {parsed['currency']}\n"
                f"🏷️ {parsed['category']}\n"
                f"💳 {parsed['account']}\n\n"
                f"💾 Сохранено{family_info}"
            )
        else:
            await update.message.reply_text("❌ Ошибка сохранения в базу данных")

    async def handle_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.lower()
        user_id = update.effective_user.id
        transactions = self.family_manager.get_family_transactions(user_id)

        if not transactions:
            await update.message.reply_text(
                "📊 Пока нет данных для анализа.\n"
                "Добавь несколько транзакций и попробуй снова!"
            )
            return

        if any(word in text for word in ['сколько', 'потратил', 'трат']):
            await self.show_spending_summary(update, transactions)
        elif any(word in text for word in ['баланс', 'счет']):
            await self.balance_command(update, context)
        elif any(word in text for word in ['топ', 'больше', 'категор']):
            await self.show_top_categories(update, transactions)
        else:
            await update.message.reply_text(
                "🤔 Попробуй спросить:\n"
                "• Сколько я потратил?\n"
                "• Показать баланс\n"
                "• Топ категории трат\n"
                "• /analyze для полного ИИ анализа"
            )

    async def show_spending_summary(self, update: Update, transactions: List[Dict]):
        expenses = [t for t in transactions if t['amount'] < 0]

        if not expenses:
            await update.message.reply_text("💰 Пока нет расходов!")
            return

        today = datetime.now()
        month_ago = today - timedelta(days=30)

        recent_expenses = []
        for trans in expenses:
            try:
                trans_date = datetime.strptime(trans['date'][:10], '%Y-%m-%d')
                if trans_date >= month_ago:
                    recent_expenses.append(trans)
            except:
                continue

        total_month = sum(abs(t['amount']) for t in recent_expenses)
        total_all = sum(abs(t['amount']) for t in expenses)

        summary = f"💸 **Твои траты:**\n\n"
        summary += f"📅 За месяц: {total_month:,.2f} лари\n"
        summary += f"📊 Всего: {total_all:,.2f} лари\n"
        summary += f"📝 Транзакций: {len(expenses)}\n\n"

        if recent_expenses:
            avg_daily = total_month / 30
            summary += f"📈 В среднем в день: {avg_daily:.2f} лари\n\n"

        summary += "🤖 Команда /analyze для детального ИИ анализа!"

        await update.message.reply_text(summary, parse_mode='Markdown')

    async def show_top_categories(self, update: Update, transactions: List[Dict]):
        expenses = [t for t in transactions if t['amount'] < 0]

        if not expenses:
            await update.message.reply_text("💰 Пока нет расходов!")
            return

        by_category = defaultdict(float)
        for trans in expenses[-30:]:
            by_category[trans['category']] += abs(trans['amount'])

        sorted_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)

        response = "🔥 **Топ категории трат:**\n\n"

        emojis = {
            'Еда': '🍽️',
            'Транспорт': '🚗',
            'Развлечения': '🎬',
            'Здоровье': '💊',
            'Одежда': '👕',
            'Техника': '📱',
            'Прочее': '📦'
        }

        for i, (category, amount) in enumerate(sorted_categories[:5], 1):
            emoji = emojis.get(category, '📦')
            percentage = (amount / sum(by_category.values())) * 100
            response += f"{i}. {emoji} {category}: {amount:.2f} лари ({percentage:.1f}%)\n"

        response += f"\n🤖 /analyze для персональных советов!"

        await update.message.reply_text(response, parse_mode='Markdown')

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        user_name = query.from_user.first_name
        data = query.data

        if data == "create_family":
            user_data = self.get_user_data(user_id)
            user_data['name'] = user_name

            family_id = self.family_manager.create_family_group(user_id, f"Семья {user_name}")

            users_data = self.db.load_data()
            users_data[str(user_id)]['family_id'] = family_id
            users_data[str(user_id)]['family_role'] = 'admin'
            self.users_data = users_data
            self.save_data()

            await query.edit_message_text(
                f"🏠 **Семейная группа создана!**\n\n"
                f"**ID группы:** `{family_id}`\n\n"
                f"📋 **Пригласите членов семьи:**\n"
                f"1. Отправьте им команду /family_invite\n"
                f"2. Или дайте им этот ID: `{family_id}`\n\n"
                f"✅ Теперь все ваши транзакции будут общими!",
                parse_mode='Markdown'
            )
            return

        elif data == "join_family":
            await query.edit_message_text(
                "👥 **Присоединение к семье**\n\n"
                "Введите ID семейной группы, который вам дал админ:\n\n"
                "Пример: `abc12345`",
                parse_mode='Markdown'
            )
            user_data = self.get_user_data(user_id)
            user_data['waiting_for_family_id'] = True
            self.save_data()
            return

        elif data == "confirm_leave_family":
            if self.family_manager.leave_family(user_id):
                await query.edit_message_text(
                    "✅ **Вы покинули семейную группу**\n\n"
                    "Теперь ваши транзакции снова будут личными.\n"
                    "Вы можете создать новую группу или присоединиться к другой через /family"
                )
            else:
                await query.edit_message_text("❌ Ошибка при выходе из группы")
            return

        elif data == "cancel_leave_family":
            await query.edit_message_text(
                "🏠 Вы остались в семейной группе!\n"
                "Используйте /family для управления группой."
            )
            return

        # Стандартные callback-и для транзакций
        user_data = self.get_user_data(user_id)

        if data.startswith('confirm_'):
            transaction_id = int(data.split('_')[1])
            pending = user_data.get('pending_transaction')

            if pending and pending['id'] == transaction_id:
                if self.add_transaction(user_id, pending, user_data.get('name')):
                    await query.edit_message_text(
                        f"✅ **Транзакция добавлена!**\n\n"
                        f"💰 {pending['amount']:+.2f} {pending['currency']}\n"
                        f"🏷️ {pending['category']}\n"
                        f"💾 Сохранено в базу данных"
                    )
                    del user_data['pending_transaction']
                    self.save_data()
                else:
                    await query.edit_message_text("❌ Ошибка сохранения")
            else:
                await query.edit_message_text("❌ Транзакция не найдена")

    async def get_user_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_data = self.get_user_data(update.effective_user.id)
        ai_learning = user_data['ai_learning']

        stats_text = "📊 **Детальная статистика:**\n\n"

        transactions = self.family_manager.get_family_transactions(update.effective_user.id)
        total_transactions = len(transactions)
        stats_text += f"📝 Всего транзакций: {total_transactions}\n"

        if total_transactions > 0:
            expenses = [t for t in transactions if t['amount'] < 0]
            incomes = [t for t in transactions if t['amount'] > 0]

            stats_text += f"💸 Расходов: {len(expenses)}\n"
            stats_text += f"💰 Доходов: {len(incomes)}\n\n"

            stats_text += "🧠 **ИИ обучение:**\n"
            stats_text += f"📚 Изученных слов: {len(ai_learning['category_preferences'])}\n"
            stats_text += f"🏪 Запомненных мест: {len(ai_learning['merchant_categories'])}\n"
            stats_text += f"🎯 Общий опыт: {ai_learning['learning_score']} примеров\n"

            if ai_learning['merchant_categories']:
                stats_text += f"\n🏪 **Запомненные места:**\n"
                for merchant, category in list(ai_learning['merchant_categories'].items())[:5]:
                    stats_text += f"• {merchant.title()} → {category}\n"

            if ai_learning['category_preferences']:
                stats_text += f"\n📚 **Топ изученные слова:**\n"
                word_scores = {}
                for word, categories in ai_learning['category_preferences'].items():
                    word_scores[word] = sum(categories.values())

                top_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)[:5]
                for word, score in top_words:
                    stats_text += f"• \"{word}\" - {score} примеров\n"

            created = datetime.fromisoformat(user_data['created_at'])
            days_ago = (datetime.now() - created).days
            stats_text += f"\n📅 Используешь бота: {days_ago} дней\n"
            stats_text += f"🔄 Данные сохраняются автоматически"

        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def export_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        transactions = self.family_manager.get_family_transactions(user_id)

        if not transactions:
            await update.message.reply_text("📊 Нет данных для экспорта")
            return

        export_data = {'transactions': transactions}
        csv_content = self.db.export_user_data(export_data, format='csv')

        filename = f"budget_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

        users_data = self.db.load_data()
        family_data = self.family_manager.get_family_data(user_id, users_data)
        family_info = f"🏠 Семейная группа: {family_data['name']}\n" if family_data else ""

        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=io.BytesIO(csv_content),
            filename=filename,
            caption=f"📊 **Экспорт данных:**\n"
                   f"{family_info}"
                   f"📝 {len(transactions)} транзакций\n"
                   f"🧠 ИИ обучение: {self.get_user_data(user_id)['ai_learning']['learning_score']} примеров"
        )

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error("Ошибка в боте:", exc_info=context.error)

        if update and hasattr(update, 'effective_message') and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "🤖 Произошла техническая ошибка. Попробуйте еще раз или обратитесь к разработчику."
                )
            except:
                pass


def main():
    print("🚀 Запуск умного бота семейного бюджета...")
    print(f"🤖 Token: {TELEGRAM_TOKEN[:10]}...")
    print(f"🧠 OpenAI API: {'✅ Подключен' if OPENAI_API_KEY else '❌ Не настроен'}")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    bot = BudgetBot()
    print(f"📊 Бот инициализирован с {len(bot.users_data)} пользователей")

    # Регистрируем команды
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("balance", bot.balance_command))
    application.add_handler(CommandHandler("analyze", bot.smart_analysis_command))
    application.add_handler(CommandHandler("stats", bot.get_user_stats))
    application.add_handler(CommandHandler("export", bot.export_data))

    # Семейные команды
    application.add_handler(CommandHandler("family", bot.family_command))
    application.add_handler(CommandHandler("family_invite", bot.family_invite_command))
    application.add_handler(CommandHandler("family_stats", bot.family_stats_command))
    application.add_handler(CommandHandler("family_leave", bot.family_leave_command))

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text_message))
    application.add_handler(CallbackQueryHandler(bot.handle_callback_query))
    application.add_error_handler(bot.error_handler)

    print("✅ Все обработчики зарегистрированы")
    print("🔥 Бот готов к работе!")
    print("-" * 50)
    print("📱 Доступные команды:")
    print("• /start - начать работу")
    print("• /family - настройка семейного бюджета 🏠")
    print("• /balance - баланс счетов")
    print("• /analyze - ИИ анализ трат")
    print("• /family_stats - семейная статистика 👥")
    print("• /stats - статистика обучения")
    print("• /export - экспорт данных")
    print("-" * 50)
    print("🤖 Особенности:")
    print("• Персональное обучение ИИ")
    print("• Семейный общий бюджет 👨‍👩‍👧‍👦")
    print("• Автоматическая категоризация")
    print("• Умные советы и анализ")
    print("-" * 50)
    print("🚀 Бот запущен и ожидает сообщений...")

    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        print("💾 Сохранение данных перед завершением...")
        bot.save_data()
        print("✅ Бот завершил работу")


if __name__ == '__main__':
    main()import logging
from datetime import datetime, timedelta
import json
import re
import io
import os
import csv
import uuid
from typing import Dict, List, Optional
from collections import defaultdict, Counter

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
    print("✅ Telegram библиотека найдена")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Выполни: python3 -m pip install python-telegram-bot==20.6")
    exit(1)

try:
    import pandas as pd
    import PyPDF2
    print("✅ Библиотеки для файлов найдены")
except ImportError as e:
    print(f"⚠️ Библиотеки для файлов не найдены: {e}")

try:
    from openai import OpenAI
    print("✅ OpenAI библиотека найдена")
except ImportError as e:
    print(f"⚠️ OpenAI не найдена: {e}")

try:
    from config import TELEGRAM_TOKEN, DEFAULT_CATEGORIES, DEFAULT_ACCOUNTS, OPENAI_API_KEY
    print("✅ Конфигурация загружена")
except ImportError:
    print("❌ Файл config.py не найден")
    exit(1)

if not TELEGRAM_TOKEN:
    print("❌ Ошибка: Не настроен TELEGRAM_TOKEN в config.py")
    exit(1)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class AIAnalyzer:
    def __init__(self, api_key):
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.enabled = True
                print("✅ OpenAI API подключен")
            except Exception as e:
                self.client = None
                self.enabled = False
                print(f"❌ Ошибка подключения OpenAI: {e}")
        else:
            self.client = None
            self.enabled = False
            print("⚠️ OpenAI API не настроен")

    async def smart_categorize(self, description, amount, user_history=None, user_preferences=None):
        if not self.enabled:
            return self.fallback_categorize(description, amount < 0)

        try:
            if user_preferences:
                personal_match = self.check_personal_preferences(description, user_preferences)
                if personal_match and personal_match['confidence'] > 0.8:
                    return personal_match

            history_context = ""
            if user_history:
                similar_transactions = self.find_similar_transactions(description, user_history)
                if similar_transactions:
                    history_context = f"\nИстория похожих трат пользователя:\n"
                    for trans in similar_transactions[:3]:
                        history_context += f"- '{trans['description']}' → {trans['category']}\n"

            prompt = f"""


Проанализируй
транзакцию
и
определи
категорию.

Транзакция: "{description}"
Сумма: {amount}
лари
Тип: {'расход' if amount < 0 else 'доход'}

{history_context}

Доступные
категории
расходов:
- Еда(продукты, рестораны, кафе, доставка)
- Транспорт(такси, бензин, общественный
транспорт, парковка)
- Развлечения(кино, театр, игры, хобби, спорт)
- Здоровье(аптека, врачи, медицина, спорт
зал)
- Одежда(одежда, обувь, аксессуары)
- Техника(электроника, софт, гаджеты)
- Прочее

Доступные
категории
доходов:
- Зарплата, Фриланс, Бизнес, Инвестиции, Подарки, Возврат, Кешбэк, Прочее

Ответь
в
JSON
формате:
{{
    "category": "название_категории",
    "confidence": 0.95,
    "reasoning": "краткое объяснение выбора"
}}
"""

response = self.client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=150,
    temperature=0.1
)

result = json.loads(response.choices[0].message.content)
return result

except Exception as e:
print(f"AI categorization error: {e}")
return self.fallback_categorize(description, amount < 0)

def check_personal_preferences(self, description, user_preferences):
description_lower = description.lower()
category_scores = {}

for merchant, category in user_preferences.get('merchant_categories', {}).items():
if merchant in description_lower:
    return {
        'category': category,
        'confidence': 0.95,
        'reasoning': f'Ты всегда относишь {merchant} к категории {category}'
    }

words = description_lower.split()
for word in words:
if word in user_preferences.get('category_preferences', {}):
    for category, count in user_preferences['category_preferences'][word].items():
        category_scores[category] = category_scores.get(category, 0) + count

if category_scores:
best_category = max(category_scores.items(), key=lambda x: x[1])
confidence = min(0.9, best_category[1] / 5)
if confidence > 0.7:
    return {
        'category': best_category[0],
        'confidence': confidence,
        'reasoning': f'На основе твоей истории ({best_category[1]} совпадений)'
    }

return None

def find_similar_transactions(self, description, history):
description_lower = description.lower()
similar = []

for trans in history[-50:]:
trans_desc = trans.get('description', '').lower()
desc_words = set(description_lower.split())
trans_words = set(trans_desc.split())
common_words = desc_words.intersection(trans_words)

if len(common_words) >= 1:
    similarity = len(common_words) / max(len(desc_words), len(trans_words))
    if similarity > 0.3:
        similar.append({
            'description': trans.get('description', ''),
            'category': trans.get('category', ''),
            'similarity': similarity
        })

similar.sort(key=lambda x: x['similarity'], reverse=True)
return similar

def fallback_categorize(self, description, is_expense=True):
desc_lower = description.lower()

if not is_expense:
if any(word in desc_lower for word in ['salary', 'зарплата', 'заработок']):
    return {'category': 'Зарплата', 'confidence': 0.8, 'reasoning': 'Ключевые слова'}
return {'category': 'Прочее', 'confidence': 0.5, 'reasoning': 'По умолчанию'}

categories = {
'Еда': ['carrefour', 'spar', 'restaurant', 'cafe', 'кафе', 'ресторан', 'еда', 'продукт', 'agrohub'],
'Транспорт': ['taxi', 'bolt', 'uber', 'gpc', 'такси', 'бензин', 'метро', 'автобус'],
'Развлечения': ['cinema', 'theatre', 'game', 'кино', 'театр', 'развлечения', 'игра'],
'Здоровье': ['pharmacy', 'hospital', 'doctor', 'аптека', 'больница', 'врач'],
'Одежда': ['clothing', 'clothes', 'одежда', 'обувь'],
'Техника': ['cellfie', 'mobile', 'internet', 'интернет', 'техника']
}

for category, keywords in categories.items():
if any(keyword in desc_lower for keyword in keywords):
    return {'category': category, 'confidence': 0.7, 'reasoning': 'Ключевые слова'}

return {'category': 'Прочее', 'confidence': 0.5, 'reasoning': 'Не определено'}

async def analyze_spending_patterns(self, transactions):
if not self.enabled or len(transactions) < 10:
return self.simple_analysis(transactions)

try:
expenses = [t for t in transactions if t['amount'] < 0]
by_category = defaultdict(list)
for trans in expenses[-30:]:
    by_category[trans['category']].append(abs(trans['amount']))

stats = {}
for category, amounts in by_category.items():
    stats[category] = {
        'total': sum(amounts),
        'count': len(amounts),
        'avg': sum(amounts) / len(amounts)
    }

prompt = f"""
Проанализируй
траты
пользователя
и
дай
персональные
советы.

Статистика
трат
за
последний
период:
{json.dumps(stats, indent=2, ensure_ascii=False)}

Общая
сумма
расходов: {sum(abs(t['amount']) for t in expenses[-30:])}
лари
Количество
транзакций: {len(expenses[-30:])}

Дай
краткий
анализ(2 - 3
предложения) и
2 - 3
конкретных
совета
по
оптимизации
бюджета.
Будь
дружелюбным
и
конструктивным.

Ответь
в
JSON
формате:
{{
    "analysis": "краткий анализ трат",
    "top_category": "категория с наибольшими тратами",
    "advice": [
        "первый совет",
        "второй совет",
        "третий совет"
    ],
    "mood": "positive/neutral/concern"
}}
"""

response = self.client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=300,
    temperature=0.3
)

return json.loads(response.choices[0].message.content)

except Exception as e:
print(f"AI analysis error: {e}")
return self.simple_analysis(transactions)

def simple_analysis(self, transactions):
expenses = [t for t in transactions if t['amount'] < 0]

if not expenses:
return {
    "analysis": "Пока недостаточно данных для анализа",
    "top_category": "Нет данных",
    "advice": ["Добавьте больше транзакций для анализа"],
    "mood": "neutral"
}

by_category = defaultdict(float)
for trans in expenses[-30:]:
by_category[trans['category']] += abs(trans['amount'])

top_category = max(by_category.items(), key=lambda x: x[1])[0] if by_category else "Прочее"
total = sum(by_category.values())

return {
"analysis": f"За последний период потрачено {total:.2f} лари. Больше всего уходит на категорию '{top_category}'.",
"top_category": top_category,
"advice": [
    "Отслеживайте крупные траты",
    "Установите лимиты по категориям",
    "Анализируйте паттерны еженедельно"
],
"mood": "neutral"
}


class DatabaseManager:
def __init__(self, data_file="budget_data.json"):
self.data_file = data_file
self.backup_file = f"{data_file}.backup"

def load_data(self):
try:
if os.path.exists(self.data_file):
    with open(self.data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ База данных загружена из {self.data_file}")
    return data
else:
    print(f"📝 Создается новая база данных: {self.data_file}")
    return {}
except Exception as e:
print(f"❌ Ошибка загрузки БД: {e}")
return {}

def save_data(self, data):
try:
if os.path.exists(self.data_file):
    import shutil
    shutil.copy2(self.data_file, self.backup_file)

with open(self.data_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

file_size = os.path.getsize(self.data_file)
print(f"💾 БД сохранена: {file_size} байт")
return True

except Exception as e:
print(f"❌ Ошибка сохранения БД: {e}")
return False

def export_user_data(self, user_data, format='csv'):
if format == 'csv':
output = io.StringIO()
writer = csv.writer(output)
writer.writerow(['Дата', 'Сумма', 'Валюта', 'Категория', 'Счет', 'Описание', 'Тип'])

for transaction in user_data.get('transactions', []):
    writer.writerow([
        transaction.get('date', ''),
        transaction.get('amount', 0),
        transaction.get('currency', 'GEL'),
        transaction.get('category', ''),
        transaction.get('account', ''),
        transaction.get('description', ''),
        transaction.get('type', '')
    ])

return output.getvalue().encode('utf-8')

elif format == 'json':
return json.dumps(user_data, ensure_ascii=False, indent=2).encode('utf-8')


class FamilyManager:
def __init__(self, database_manager):
self.db = database_manager

def create_family_group(self, creator_user_id, family_name="Семейный бюджет"):
family_id = str(uuid.uuid4())[:8]

family_data = {
'id': family_id,
'name': family_name,
'created_by': creator_user_id,
'created_at': datetime.now().isoformat(),
'members': [creator_user_id],
'transactions': [],
'settings': {
    'default_currency': 'GEL',
    'shared_categories': True,
    'notification_enabled': True
}
}

users_data = self.db.load_data()
if 'families' not in users_data:
users_data['families'] = {}

users_data['families'][family_id] = family_data
self.db.save_data(users_data)
return family_id

def join_family_group(self, user_id, family_id):
users_data = self.db.load_data()

if 'families' not in users_data or family_id not in users_data['families']:
return False

family_data = users_data['families'][family_id]

if user_id not in family_data['members']:
family_data['members'].append(user_id)
self.db.save_data(users_data)
return True

return False

def get_family_data(self, user_id, users_data=None):
if users_data is None:
users_data = self.db.load_data()

user_id_str = str(user_id)
if user_id_str not in users_data:
return None

family_id = users_data[user_id_str].get('family_id')

if not family_id or 'families' not in users_data:
return None

return users_data['families'].get(family_id)

def get_family_transactions(self, user_id):
users_data = self.db.load_data()
family_data = self.get_family_data(user_id, users_data)

if not family_data:
user_id_str = str(user_id)
if user_id_str in users_data:
    return users_data[user_id_str].get('transactions', [])
return []

return family_data.get('transactions', [])

def add_family_transaction(self, user_id, transaction, user_name):
users_data = self.db.load_data()
family_data = self.get_family_data(user_id, users_data)

if not family_data:
return False

transaction['added_by'] = user_id
transaction['added_by_name'] = user_name

family_data['transactions'].append(transaction)

if self.db.save_data(users_data):
print(f"💾 Семейная транзакция сохранена от пользователя {user_id}")
return True
return False

def get_family_statistics(self, user_id):
transactions = self.get_family_transactions(user_id)

total_transactions = len(transactions)
total_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
total_expenses = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
total_balance = total_income - total_expenses

return {
'total_transactions': total_transactions,
'total_income': total_income,
'total_expenses': total_expenses,
'total_balance': total_balance
}

def get_detailed_family_stats(self, user_id):
users_data = self.db.load_data()
family_data = self.get_family_data(user_id, users_data)
if not family_data:
return None

transactions = family_data.get('transactions', [])

if not transactions:
return None

today = datetime.now()
week_ago = today - timedelta(days=7)
month_ago = today - timedelta(days=30)

week_transactions = []
month_transactions = []

for trans in transactions:
try:
    trans_date = datetime.strptime(trans['date'][:10], '%Y-%m-%d')
    if trans_date >= week_ago:
        week_transactions.append(trans)
    if trans_date >= month_ago:
        month_transactions.append(trans)
except:
    continue

week_expenses = sum(abs(t['amount']) for t in week_transactions if t['amount'] < 0)
month_expenses = sum(abs(t['amount']) for t in month_transactions if t['amount'] < 0)

week_income = sum(t['amount'] for t in week_transactions if t['amount'] > 0)
month_income = sum(t['amount'] for t in month_transactions if t['amount'] > 0)

by_member = defaultdict(lambda: {'expenses': 0, 'income': 0, 'count': 0})
for trans in month_transactions:
member_name = trans.get('added_by_name', 'Неизвестно')
by_member[member_name]['count'] += 1
if trans['amount'] < 0:
    by_member[member_name]['expenses'] += abs(trans['amount'])
else:
    by_member[member_name]['income'] += trans['amount']

by_category = defaultdict(float)
for trans in month_transactions:
if trans['amount'] < 0:
    by_category[trans['category']] += abs(trans['amount'])

top_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:5]

return {
'family_data': family_data,
'week': {
    'expenses': week_expenses,
    'income': week_income,
    'balance': week_income - week_expenses
},
'month': {
    'expenses': month_expenses,
    'income': month_income,
    'balance': month_income - month_expenses
},
'by_member': dict(by_member),
'top_categories': top_categories
}

def leave_family(self, user_id):
users_data = self.db.load_data()
family_data = self.get_family_data(user_id, users_data)
if not family_data:
return False

family_id = family_data['id']

if user_id in family_data['members']:
family_data['members'].remove(user_id)

user_id_str = str(user_id)
if user_id_str in users_data:
user_data = users_data[user_id_str]
if 'family_id' in user_data:
    del user_data['family_id']
if 'family_role' in user_data:
    del user_data['family_role']

if not family_data['members']:
del users_data['families'][family_id]

self.db.save_data(users_data)
return True


class BudgetBot:
def __init__(self):
self.db = DatabaseManager()
self.users_data = self.db.load_data()

self.categories = DEFAULT_CATEGORIES
self.accounts = DEFAULT_ACCOUNTS

self.ai_analyzer = AIAnalyzer(OPENAI_API_KEY)
self.family_manager = FamilyManager(self.db)

print(f"📊 Бот инициализирован с {len(self.users_data)} пользователей")

def get_user_data(self, user_id):
user_id_str = str(user_id)

if user_id_str not in self.users_data:
self.users_data[user_id_str] = {
    'transactions': [],
    'active_budget': 'Семейный',
    'ai_learning': {
        'category_preferences': {},
        'merchant_categories': {},
        'total_interactions': 0,
        'learning_score': 0
    },
    'settings': {
        'default_currency': 'GEL',
        'auto_save': True,
        'ai_enabled': True
    },
    'created_at': datetime.now().isoformat(),
    'last_activity': datetime.now().isoformat()
}
self.save_data()

self.users_data[user_id_str]['last_activity'] = datetime.now().isoformat()
return self.users_data[user_id_str]

def save_data(self):
return self.db.save_data(self.users_data)

def add_transaction(self, user_id, transaction, user_name=None):
users_data = self.db.load_data()
family_data = self.family_manager.get_family_data(user_id, users_data)

if family_data:
if not user_name:
    user_name = users_data[str(user_id)].get('name', f'Пользователь {str(user_id)[-4:]}')
return self.family_manager.add_family_transaction(user_id, transaction, user_name)
else:
user_data = self.get_user_data(user_id)
user_data['transactions'].append(transaction)

self.learn_from_transaction(user_id, transaction)

if self.save_data():
    print(f"💾 Личная транзакция сохранена для пользователя {user_id}")
    return True
return False

def learn_from_transaction(self, user_id, transaction):
user_data = self.get_user_data(user_id)
ai_learning = user_data['ai_learning']

description = transaction.get('description', '').lower()
category = transaction.get('category', '')

if not description or not category:
return

keywords = [word for word in description.split() if len(word) > 2]

for keyword in keywords:
if keyword not in ai_learning['category_preferences']:
    ai_learning['category_preferences'][keyword] = {}

if category not in ai_learning['category_preferences'][keyword]:
    ai_learning['category_preferences'][keyword][category] = 0

ai_learning['category_preferences'][keyword][category] += 1

merchants = ['carrefour', 'spar', 'agrohub', 'big chefs', 'bolt', 'tbc', 'bog', 
        'gpc', 'grand mall', 'cellfie', 'merkuri', 'dona']

for merchant in merchants:
if merchant in description:
    ai_learning['merchant_categories'][merchant] = category
    break

ai_learning['learning_score'] += 1
print(f"🧠 ИИ изучил: {description[:30]}... → {category}")

def get_learned_suggestion(self, user_id, description):
user_data = self.get_user_data(user_id)
ai_learning = user_data['ai_learning']

description_lower = description.lower()
category_scores = {}

for merchant, category in ai_learning['merchant_categories'].items():
if merchant in description_lower:
    return {
        'category': category,
        'confidence': 0.95,
        'reasoning': f'Ты всегда относишь {merchant.title()} к категории {category}'
    }

words = description_lower.split()
for word in words:
if word in ai_learning['category_preferences']:
    for category, count in ai_learning['category_preferences'][word].items():
        category_scores[category] = category_scores.get(category, 0) + count

if category_scores:
best_category = max(category_scores.items(), key=lambda x: x[1])
confidence = min(0.9, best_category[1] / 5)

if confidence > 0.6:
    return {
        'category': best_category[0],
        'confidence': confidence,
        'reasoning': f'На основе твоего обучения ({best_category[1]} примеров)'
    }

return None

async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
user_data = self.get_user_data(user.id)
user_data['name'] = user.first_name

transactions = self.family_manager.get_family_transactions(user.id)
total_transactions = len(transactions)
learning_score = user_data['ai_learning']['learning_score']

users_data = self.db.load_data()
family_data = self.family_manager.get_family_data(user.id, users_data)
family_info = f"\n🏠 **Семья:** {family_data['name']}" if family_data else "\n💡 **Совет:** Создайте семейную группу через /family"

welcome_text = f"""
👋 Привет, {user.first_name}!

Я
умный
помощник
для
семейного
бюджета
с
персональным
обучением!{family_info}

🔥 ** Твоя
статистика: **
📊 Транзакций: {total_transactions}
🧠 ИИ
обучение: {learning_score}
примеров

🤖 ** ИИ
возможности: **
• Умная
категоризация
с
обучением
• Персональные
советы
и
анализ
• Запоминание
твоих
предпочтений
• Обработка
банковских
выписок

** Команды: **
/ family - 🏠 семейный
бюджет
/ analyze - 🧠 ИИ
анализ
трат
/ stats - 📊 статистика
обучения
/ export - 📤 экспорт
данных
/ balance - 💰 баланс
счетов

** Попробуй: **
• "Потратил 50 лари на еду в Carrefour"
• Пришли
файл
выписки 📎
"""

await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def family_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
user_name = update.effective_user.first_name

user_data = self.get_user_data(user_id)
user_data['name'] = user_name

users_data = self.db.load_data()
family_data = self.family_manager.get_family_data(user_id, users_data)

if family_data:
    members_info = ""
    for member_id in family_data['members']:
        member_name = users_data.get(str(member_id), {}).get('name', f'Пользователь {str(member_id)[-4:]}')
        role = "👑 Админ" if member_id == family_data['created_by'] else "👤 Участник"
        members_info += f"• {member_name} - {role}\n"

    family_stats = self.family_manager.get_family_statistics(user_id)

    response = f"""