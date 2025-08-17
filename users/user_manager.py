# -*- coding: utf-8 -*-
"""
Менеджер пользователей для бота семейного бюджета
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class UserManager:
    """Менеджер для работы с пользователями"""

    def __init__(self, database_manager, ai_analyzer):
        self.db = database_manager
        self.ai = ai_analyzer

    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Получить данные пользователя"""
        data = self.db.load_data()
        user_id_str = str(user_id)

        if 'users' not in data:
            data['users'] = {}

        if user_id_str not in data['users']:
            # Создаем нового пользователя
            data['users'][user_id_str] = self._create_new_user()
            self.db.save_data(data)

        # Обновляем время последней активности
        data['users'][user_id_str]['last_activity'] = datetime.now().isoformat()
        return data['users'][user_id_str]

    def _create_new_user(self) -> Dict[str, Any]:
        """Создать данные нового пользователя"""
        return {
            'transactions': [],
            'ai_learning': {
                'category_preferences': {},
                'merchant_categories': {},
                'total_interactions': 0,
                'learning_score': 0
            },
            'settings': {
                'default_currency': 'GEL',
                'auto_save': True,
                'ai_enabled': True,
                'notifications': True
            },
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'family_id': None,
            'family_role': None
        }

    def update_user_data(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """Обновить данные пользователя"""
        data = self.db.load_data()
        if 'users' not in data:
            data['users'] = {}

        data['users'][str(user_id)] = user_data
        return self.db.save_data(data)

    def add_transaction(self, user_id: int, transaction: Dict[str, Any]) -> bool:
        """Добавить транзакцию пользователю"""
        user_data = self.get_user_data(user_id)

        # Добавляем транзакцию
        user_data['transactions'].append(transaction)

        # Обучаем ИИ
        self.learn_from_transaction(user_id, transaction)

        # Сохраняем данные
        if self.update_user_data(user_id, user_data):
            logger.info(f"Транзакция добавлена для пользователя {user_id}")
            return True
        return False

    def learn_from_transaction(self, user_id: int, transaction: Dict[str, Any]) -> None:
        """Обучение ИИ на основе транзакции"""
        user_data = self.get_user_data(user_id)
        ai_learning = user_data['ai_learning']

        description = transaction.get('description', '').lower()
        category = transaction.get('category', '')

        if not description or not category:
            return

        # Обучаем на ключевых словах
        keywords = [word for word in description.split() if len(word) > 2]

        for keyword in keywords:
            if keyword not in ai_learning['category_preferences']:
                ai_learning['category_preferences'][keyword] = {}

            if category not in ai_learning['category_preferences'][keyword]:
                ai_learning['category_preferences'][keyword][category] = 0

            ai_learning['category_preferences'][keyword][category] += 1

        # Запоминаем места (магазины, сервисы)
        merchants = [
            'carrefour', 'spar', 'agrohub', 'big chefs', 'bolt', 'uber',
            'tbc', 'bog', 'liberty', 'gpc', 'grand mall', 'cellfie', 'merkuri'
        ]

        for merchant in merchants:
            if merchant in description:
                ai_learning['merchant_categories'][merchant] = category
                break

        # Увеличиваем счетчик обучения
        ai_learning['learning_score'] += 1
        ai_learning['total_interactions'] += 1

        logger.info(f"ИИ изучил: {description[:30]}... → {category}")

    def get_learned_suggestion(self, user_id: int, description: str) -> Optional[Dict[str, Any]]:
        """Получить предложение на основе обучения"""
        user_data = self.get_user_data(user_id)
        ai_learning = user_data['ai_learning']

        description_lower = description.lower()

        # Проверяем запомненные места
        for merchant, category in ai_learning['merchant_categories'].items():
            if merchant in description_lower:
                return {
                    'category': category,
                    'confidence': 0.95,
                    'reasoning': f'Ты всегда относишь {merchant.title()} к категории {category}',
                    'source': 'personal'
                }

        # Анализируем по словам
        category_scores = {}
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
                    'reasoning': f'На основе твоего обучения ({best_category[1]} примеров)',
                    'source': 'personal'
                }

        return None

    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        user_data = self.get_user_data(user_id)
        transactions = user_data['transactions']
        ai_learning = user_data['ai_learning']

        total_transactions = len(transactions)
        expenses = [t for t in transactions if t['amount'] < 0]
        incomes = [t for t in transactions if t['amount'] > 0]

        created = datetime.fromisoformat(user_data['created_at'])
        days_using = (datetime.now() - created).days

        return {
            'total_transactions': total_transactions,
            'total_expenses': len(expenses),
            'total_incomes': len(incomes),
            'learning_score': ai_learning['learning_score'],
            'known_words': len(ai_learning['category_preferences']),
            'known_merchants': len(ai_learning['merchant_categories']),
            'days_using': days_using,
            'family_member': user_data.get('family_id') is not None
        }

    def get_user_name(self, user_id: int) -> str:
        """Получить имя пользователя"""
        user_data = self.get_user_data(user_id)
        return user_data.get('name', f'Пользователь {str(user_id)[-4:]}')

    def set_user_name(self, user_id: int, name: str) -> bool:
        """Установить имя пользователя"""
        user_data = self.get_user_data(user_id)
        user_data['name'] = name
        return self.update_user_data(user_id, user_data)

    def get_user_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить транзакции пользователя"""
        user_data = self.get_user_data(user_id)
        return user_data['transactions']

    def update_user_settings(self, user_id: int, settings: Dict[str, Any]) -> bool:
        """Обновить настройки пользователя"""
        user_data = self.get_user_data(user_id)
        user_data['settings'].update(settings)
        return self.update_user_data(user_id, user_data)

    def delete_user_data(self, user_id: int) -> bool:
        """Удалить данные пользователя"""
        data = self.db.load_data()
        user_id_str = str(user_id)

        if 'users' in data and user_id_str in data['users']:
            del data['users'][user_id_str]
            return self.db.save_data(data)

        return False