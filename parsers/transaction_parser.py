# -*- coding: utf-8 -*-
"""
Парсер транзакций для бота семейного бюджета
"""

import re
from typing import Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TransactionParser:
    """Парсер для обработки текстовых описаний транзакций"""

    def __init__(self, ai_analyzer, user_manager):
        self.ai = ai_analyzer
        self.user_manager = user_manager

    async def parse_transaction_text(self, user_id: int, text: str) -> Optional[Dict[str, Any]]:
        """Парсинг текста транзакции"""
        # Получаем данные пользователя для персонализации
        user_data = self.user_manager.get_user_data(user_id)

        # Сначала пробуем персональное предложение
        personal_suggestion = self.user_manager.get_learned_suggestion(user_id, text)

        if personal_suggestion and personal_suggestion['confidence'] > 0.8:
            # Используем персональное предложение
            parsed = self._simple_parse_amount(text)
            if parsed:
                parsed.update(personal_suggestion)
                parsed['source'] = 'personal_ai'
                return parsed

        # Если персонального предложения нет, используем ИИ
        parsed = await self._ai_parse_transaction(text, user_data)
        if parsed:
            parsed['source'] = 'openai'
            return parsed

        # В крайнем случае используем простой парсинг
        return self._simple_parse_transaction(text)

    def _simple_parse_amount(self, text: str) -> Optional[Dict[str, Any]]:
        """Простое извлечение суммы из текста"""
        amount_match = re.search(r'(\d+(?:\.\d+)?)', text)
        if not amount_match:
            return None

        amount = float(amount_match.group(1))
        is_expense = any(word in text.lower() for word in [
            'потратил', 'купил', 'заплатил', 'потрачено', 'израсходовал'
        ])

        return {
            'amount': -amount if is_expense else amount,
            'currency': self._detect_currency(text),
            'account': self._detect_account(text),
            'description': text,
            'type': 'expense' if is_expense else 'income'
        }

    async def _ai_parse_transaction(self, text: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Парсинг с помощью ИИ"""
        if not self.ai.enabled:
            return self._simple_parse_transaction(text)

        try:
            # Извлекаем базовую информацию
            amount_match = re.search(r'(\d+(?:\.\d+)?)', text)
            if not amount_match:
                return None

            amount = float(amount_match.group(1))
            is_expense = self._detect_expense_type(text)
            amount = -amount if is_expense else amount

            # Используем ИИ для категоризации
            categorization = await self.ai.smart_categorize(
                description=text,
                amount=amount,
                user_history=user_data.get('transactions', []),
                user_preferences=user_data.get('ai_learning', {})
            )

            return {
                'amount': amount,
                'currency': self._detect_currency(text),
                'category': categorization['category'],
                'account': self._detect_account(text),
                'description': text,
                'type': 'expense' if is_expense else 'income',
                'confidence': categorization['confidence'],
                'reasoning': categorization.get('reasoning', '')
            }

        except Exception as e:
            logger.error(f"Ошибка ИИ парсинга: {e}")
            return self._simple_parse_transaction(text)

    def _simple_parse_transaction(self, text: str) -> Optional[Dict[str, Any]]:
        """Простой парсинг без ИИ"""
        amount_match = re.search(r'(\d+(?:\.\d+)?)', text)
        if not amount_match:
            return None

        amount = float(amount_match.group(1))
        is_expense = self._detect_expense_type(text)

        return {
            'amount': -amount if is_expense else amount,
            'currency': self._detect_currency(text),
            'category': self._simple_categorize(text, is_expense),
            'account': self._detect_account(text),
            'description': text,
            'type': 'expense' if is_expense else 'income',
            'confidence': 0.5,
            'source': 'simple'
        }

    def _detect_expense_type(self, text: str) -> bool:
        """Определить тип транзакции (расход/доход)"""
        text_lower = text.lower()

        expense_words = [
            'потратил', 'купил', 'заплатил', 'потрачено', 'израсходовал',
            'оплатил', 'приобрел', 'затратил'
        ]

        income_words = [
            'получил', 'зарплата', 'доход', 'заработал', 'поступил',
            'выручка', 'прибыль'
        ]

        # Сначала проверяем явные слова дохода
        if any(word in text_lower for word in income_words):
            return False

        # Затем проверяем слова расхода
        if any(word in text_lower for word in expense_words):
            return True

        # По умолчанию считаем расходом
        return True

    def _detect_currency(self, text: str) -> str:
        """Определить валюту"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['доллар', 'usd', '$']):
            return 'USD'
        elif any(word in text_lower for word in ['евро', 'eur', '€']):
            return 'EUR'
        else:
            return 'GEL'  # По умолчанию

    def _detect_account(self, text: str) -> str:
        """Определить счет"""
        text_lower = text.lower()

        if 'bog' in text_lower:
            return 'BOG Card'
        elif 'tbc' in text_lower:
            return 'TBC Card'
        elif 'liberty' in text_lower:
            return 'Liberty Card'
        elif any(word in text_lower for word in ['карт', 'card']):
            return 'Банковская карта'
        elif any(word in text_lower for word in ['наличные', 'наличка', 'кеш']):
            return 'Наличные'
        else:
            return 'Неизвестно'

    def _simple_categorize(self, text: str, is_expense: bool) -> str:
        """Простая категоризация без ИИ"""
        text_lower = text.lower()

        if not is_expense:
            if any(word in text_lower for word in ['зарплата', 'salary', 'заработок']):
                return 'Зарплата'
            elif any(word in text_lower for word in ['фриланс', 'freelance']):
                return 'Фриланс'
            elif any(word in text_lower for word in ['бизнес', 'business']):
                return 'Бизнес'
            else:
                return 'Прочее'

        # Категории расходов
        categories_map = {
            'Еда': ['carrefour', 'spar', 'restaurant', 'cafe', 'кафе', 'ресторан', 'еда', 'продукт', 'agrohub',
                    'макдональдс', 'kfc'],
            'Транспорт': ['taxi', 'bolt', 'uber', 'gpc', 'такси', 'бензин', 'метро', 'автобус', 'заправка'],
            'Развлечения': ['cinema', 'theatre', 'game', 'кино', 'театр', 'развлечения', 'игра', 'концерт', 'клуб'],
            'Здоровье': ['pharmacy', 'hospital', 'doctor', 'аптека', 'больница', 'врач', 'медицина', 'лекарство'],
            'Одежда': ['clothing', 'clothes', 'одежда', 'обувь', 'магазин одежды', 'бутик'],
            'Техника': ['cellfie', 'mobile', 'internet', 'интернет', 'техника', 'компьютер', 'телефон', 'гаджет']
        }

        for category, keywords in categories_map.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return 'Прочее'

    def create_transaction_dict(self, parsed_data: Dict[str, Any], transaction_id: int = None) -> Dict[str, Any]:
        """Создать словарь транзакции"""
        if transaction_id is None:
            transaction_id = int(datetime.now().timestamp())

        return {
            'id': transaction_id,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'amount': parsed_data['amount'],
            'currency': parsed_data.get('currency', 'GEL'),
            'category': parsed_data.get('category', 'Прочее'),
            'account': parsed_data.get('account', 'Неизвестно'),
            'description': parsed_data['description'],
            'type': parsed_data.get('type', 'expense'),
            'confidence': parsed_data.get('confidence', 0.5),
            'reasoning': parsed_data.get('reasoning', ''),
            'source': parsed_data.get('source', 'manual')
        }