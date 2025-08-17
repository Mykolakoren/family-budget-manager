# -*- coding: utf-8 -*-
"""
ИИ анализатор для бота семейного бюджета
"""

import json
import re
from typing import Dict, List, Optional, Any
from collections import defaultdict
import logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from config import AI_CONFIG

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """ИИ анализатор для обработки транзакций и аналитики"""

    def __init__(self, api_key: Optional[str]):
        self.enabled = False
        self.client = None

        if api_key and OpenAI:
            try:
                self.client = OpenAI(api_key=api_key)
                self.enabled = True
                print("✅ OpenAI API подключен")
            except Exception as e:
                logger.error(f"Ошибка подключения OpenAI: {e}")
                print(f"❌ Ошибка подключения OpenAI: {e}")
        else:
            print("⚠️ OpenAI API не настроен")

    async def smart_categorize(self, description: str, amount: float,
                               user_history: Optional[List[Dict]] = None,
                               user_preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """Умная категоризация транзакции"""

        # Сначала проверяем персональные предпочтения
        if user_preferences:
            personal_match = self._check_personal_preferences(description, user_preferences)
            if personal_match and personal_match['confidence'] > 0.8:
                return personal_match

        # Если ИИ недоступен, используем fallback
        if not self.enabled:
            return self._fallback_categorize(description, amount < 0)

        try:
            # Формируем контекст из истории
            history_context = self._build_history_context(description, user_history)

            # Создаем промпт для ИИ
            prompt = self._build_categorization_prompt(description, amount, history_context)

            # Запрос к ИИ
            response = self.client.chat.completions.create(
                model=AI_CONFIG['model'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=AI_CONFIG['temperature']
            )

            result = json.loads(response.choices[0].message.content)
            result['source'] = 'openai'
            return result

        except Exception as e:
            logger.error(f"Ошибка ИИ категоризации: {e}")
            return self._fallback_categorize(description, amount < 0)

    def _check_personal_preferences(self, description: str, user_preferences: Dict) -> Optional[Dict]:
        """Проверка персональных предпочтений пользователя"""
        description_lower = description.lower()

        # Проверяем запомненные места
        for merchant, category in user_preferences.get('merchant_categories', {}).items():
            if merchant in description_lower:
                return {
                    'category': category,
                    'confidence': 0.95,
                    'reasoning': f'Ты всегда относишь {merchant} к категории {category}',
                    'source': 'personal'
                }

        # Анализируем по словам
        category_scores = {}
        words = description_lower.split()

        for word in words:
            if word in user_preferences.get('category_preferences', {}):
                for category, count in user_preferences['category_preferences'][word].items():
                    category_scores[category] = category_scores.get(category, 0) + count

        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            confidence = min(0.9, best_category[1] / 5)

            if confidence > AI_CONFIG['confidence_threshold']:
                return {
                    'category': best_category[0],
                    'confidence': confidence,
                    'reasoning': f'На основе твоего обучения ({best_category[1]} примеров)',
                    'source': 'personal'
                }

        return None

    def _build_history_context(self, description: str, user_history: Optional[List[Dict]]) -> str:
        """Построение контекста из истории пользователя"""
        if not user_history:
            return ""

        similar_transactions = self._find_similar_transactions(description, user_history)
        if not similar_transactions:
            return ""

        context = "\nИстория похожих трат пользователя:\n"
        for trans in similar_transactions[:3]:
            context += f"- '{trans['description']}' → {trans['category']}\n"

        return context

    def _find_similar_transactions(self, description: str, history: List[Dict]) -> List[Dict]:
        """Поиск похожих транзакций в истории"""
        description_lower = description.lower()
        similar = []

        for trans in history[-50:]:  # Берем последние 50 транзакций
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

        return sorted(similar, key=lambda x: x['similarity'], reverse=True)

    def _build_categorization_prompt(self, description: str, amount: float, history_context: str) -> str:
        """Построение промпта для категоризации"""
        is_expense = amount < 0

        return f"""
Проанализируй транзакцию и определи категорию.

Транзакция: "{description}"
Сумма: {amount} лари
Тип: {'расход' if is_expense else 'доход'}

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

    def _fallback_categorize(self, description: str, is_expense: bool = True) -> Dict[str, Any]:
        """Базовая категоризация без ИИ"""
        desc_lower = description.lower()

        if not is_expense:
            if any(word in desc_lower for word in ['salary', 'зарплата', 'заработок']):
                return {'category': 'Зарплата', 'confidence': 0.8, 'reasoning': 'Ключевые слова', 'source': 'fallback'}
            return {'category': 'Прочее', 'confidence': 0.5, 'reasoning': 'По умолчанию', 'source': 'fallback'}

        # Словарь для определения категорий по ключевым словам
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
                return {'category': category, 'confidence': 0.7, 'reasoning': 'Ключевые слова', 'source': 'fallback'}

        return {'category': 'Прочее', 'confidence': 0.5, 'reasoning': 'Не определено', 'source': 'fallback'}

    async def analyze_spending_patterns(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Анализ паттернов трат"""
        if not self.enabled or len(transactions) < 10:
            return self._simple_analysis(transactions)

        try:
            # Подготавливаем данные для анализа
            expenses = [t for t in transactions if t['amount'] < 0]
            stats = self._calculate_spending_stats(expenses[-30:])  # Последние 30 транзакций

            # Создаем промпт для анализа
            prompt = self._build_analysis_prompt(stats, expenses)

            # Запрос к ИИ
            response = self.client.chat.completions.create(
                model=AI_CONFIG['model'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=AI_CONFIG['max_tokens'],
                temperature=0.3
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Ошибка ИИ анализа: {e}")
            return self._simple_analysis(transactions)

    def _calculate_spending_stats(self, expenses: List[Dict]) -> Dict[str, Any]:
        """Расчет статистики трат"""
        by_category = defaultdict(list)
        for trans in expenses:
            by_category[trans['category']].append(abs(trans['amount']))

        stats = {}
        for category, amounts in by_category.items():
            stats[category] = {
                'total': sum(amounts),
                'count': len(amounts),
                'avg': sum(amounts) / len(amounts) if amounts else 0
            }

        return stats

    def _build_analysis_prompt(self, stats: Dict, expenses: List[Dict]) -> str:
        """Построение промпта для анализа"""
        total_spent = sum(abs(t['amount']) for t in expenses[-30:])

        return f"""
Проанализируй траты пользователя и дай персональные советы.

Статистика трат за последний период:
{json.dumps(stats, indent=2, ensure_ascii=False)}

Общая сумма расходов: {total_spent} лари
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

    def _simple_analysis(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Простой анализ без ИИ"""
        expenses = [t for t in transactions if t['amount'] < 0]

        if not expenses:
            return {
                "analysis": "Пока недостаточно данных для анализа",
                "top_category": "Нет данных",
                "advice": ["Добавьте больше транзакций для анализа"],
                "mood": "neutral"
            }

        # Группируем по категориям
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