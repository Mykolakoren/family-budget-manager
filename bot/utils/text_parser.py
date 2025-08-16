import re
from typing import Dict, Optional, Any
from datetime import datetime
import openai
from decouple import config


class TransactionParser:
    """Parse natural language transaction text."""
    
    def __init__(self):
        self.openai_api_key = config('OPENAI_API_KEY', default=None)
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Define patterns for different languages
        self.patterns = {
            'amount': [
                r'(\d+(?:\.\d+)?)\s*(лари|лар|gel|dollar|dollars|usd|euro|eur|грн|uah|usdt)',
                r'(\d+(?:\.\d+)?)',  # Fallback for just numbers
            ],
            'transaction_type': {
                'expense': [
                    'потратил', 'трата', 'купил', 'оплатил', 'spent', 'paid', 'bought',
                    'expense', 'расход', 'minus', 'withdraw'
                ],
                'income': [
                    'получил', 'зарплата', 'доход', 'earned', 'salary', 'income',
                    'received', 'bonus', 'profit', 'freelance'
                ]
            },
            'categories': {
                'food': ['еда', 'питание', 'ресторан', 'кафе', 'food', 'restaurant', 'cafe', 'lunch', 'dinner'],
                'transport': ['транспорт', 'метро', 'автобус', 'такси', 'transport', 'metro', 'bus', 'taxi', 'uber'],
                'entertainment': ['развлечения', 'кино', 'театр', 'entertainment', 'movie', 'cinema'],
                'health': ['здоровье', 'аптека', 'врач', 'health', 'pharmacy', 'doctor', 'medical'],
                'clothes': ['одежда', 'обувь', 'clothes', 'shoes', 'fashion'],
                'rent': ['аренда', 'квартира', 'rent', 'apartment', 'house'],
                'salary': ['зарплата', 'salary', 'wage', 'income'],
                'other': ['прочее', 'другое', 'other', 'misc']
            },
            'accounts': {
                'bog': ['bog', 'bank of georgia', 'бог'],
                'tbc': ['tbc', 'тбк', 'tbilisi business center'],
                'cash': ['наличные', 'cash', 'наличка'],
                'paypal': ['paypal', 'пейпал'],
                'crypto': ['crypto', 'криптотa', 'bitcoin', 'btc']
            }
        }
    
    async def parse_transaction_text(self, text: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Parse transaction text and extract structured data."""
        text_lower = text.lower()
        
        # Try LLM parsing first if available
        if self.openai_api_key:
            llm_result = await self._parse_with_llm(text)
            if llm_result and llm_result.get('confidence', 0) > 0.7:
                return llm_result
        
        # Fallback to pattern-based parsing
        return await self._parse_with_patterns(text_lower)
    
    async def _parse_with_patterns(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse using regex patterns."""
        result = {
            'amount': None,
            'currency': 'USD',
            'transaction_type': 'expense',
            'category_name': 'other',
            'account_name': 'cash',
            'description': text,
            'confidence': 0.5
        }
        
        # Extract amount
        for pattern in self.patterns['amount']:
            match = re.search(pattern, text)
            if match:
                result['amount'] = float(match.group(1))
                if len(match.groups()) > 1:
                    currency_text = match.group(2).lower()
                    if currency_text in ['лари', 'лар', 'gel']:
                        result['currency'] = 'GEL'
                    elif currency_text in ['dollar', 'dollars', 'usd']:
                        result['currency'] = 'USD'
                    elif currency_text in ['euro', 'eur']:
                        result['currency'] = 'EUR'
                    elif currency_text in ['грн', 'uah']:
                        result['currency'] = 'UAH'
                    elif currency_text in ['usdt']:
                        result['currency'] = 'USDT'
                break
        
        # Determine transaction type
        for transaction_type, keywords in self.patterns['transaction_type'].items():
            if any(keyword in text for keyword in keywords):
                result['transaction_type'] = transaction_type
                break
        
        # Extract category
        for category, keywords in self.patterns['categories'].items():
            if any(keyword in text for keyword in keywords):
                result['category_name'] = category
                result['confidence'] += 0.2
                break
        
        # Extract account
        for account, keywords in self.patterns['accounts'].items():
            if any(keyword in text for keyword in keywords):
                result['account_name'] = account
                result['confidence'] += 0.2
                break
        
        if result['amount'] is None:
            return None
        
        return result
    
    async def _parse_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse using OpenAI LLM."""
        try:
            prompt = f"""
Parse this transaction text and extract structured data:
"{text}"

Return a JSON object with these fields:
- amount: number (positive value)
- currency: one of [USD, EUR, GEL, UAH, USDT]
- transaction_type: one of [income, expense]
- category_name: one of [food, transport, entertainment, health, clothes, rent, salary, other]
- account_name: one of [bog, tbc, cash, paypal, crypto, other]
- description: brief description
- confidence: float between 0 and 1

Only return valid JSON, no additional text.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"LLM parsing error: {e}")
            return None