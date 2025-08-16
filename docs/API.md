# API Documentation

## Overview

Family Budget Manager API provides endpoints for managing personal and family budgets with multi-platform support.

### Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://your-domain.com/api/v1`

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Endpoints

### Authentication

#### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "telegram_id": "123456789",
  "preferred_language": "en",
  "preferred_currency": "USD"
}
```

#### POST /auth/login
Login with email and password.

#### POST /auth/telegram-login
Login with Telegram ID.

### Users

#### GET /users/me
Get current user profile.

#### PATCH /users/me
Update current user profile.

### Accounts

#### GET /accounts/
Get user's accounts.

#### POST /accounts/
Create a new account.

**Request Body:**
```json
{
  "name": "BOG Card",
  "account_type": "bank_card",
  "currency": "GEL",
  "initial_balance": 1000.00,
  "bank_name": "Bank of Georgia"
}
```

### Transactions

#### GET /transactions/
Get user's transactions with optional filtering.

#### POST /transactions/
Create a new transaction.

**Request Body:**
```json
{
  "amount": 50.00,
  "description": "Lunch at restaurant",
  "transaction_type": "expense",
  "transaction_date": "2023-12-01T12:00:00Z",
  "account_id": 1,
  "category_id": 1,
  "original_text": "Spent 50 GEL on food"
}
```

#### POST /transactions/parse
Parse natural language transaction text.

### Categories

#### GET /categories/
Get available categories.

#### POST /categories/
Create a custom category.

### Analytics

#### GET /analytics/dashboard
Get dashboard statistics.

#### GET /analytics/expenses-by-category
Get expenses grouped by category.

#### GET /analytics/income-vs-expenses
Get income vs expenses data.

## Error Handling

The API returns standard HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses include details:

```json
{
  "detail": "Error description",
  "code": "ERROR_CODE"
}
```

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

## SDKs and Examples

### Python Example

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/v1/auth/login', {
    'username': 'user@example.com',
    'password': 'password123'
})
token = response.json()['access_token']

# Create transaction
headers = {'Authorization': f'Bearer {token}'}
transaction = {
    'amount': 25.50,
    'description': 'Coffee',
    'transaction_type': 'expense',
    'account_id': 1,
    'category_id': 1
}
response = requests.post(
    'http://localhost:8000/api/v1/transactions/',
    json=transaction,
    headers=headers
)
```

### JavaScript Example

```javascript
// Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// Create transaction
const transaction = {
  amount: 25.50,
  description: 'Coffee',
  transaction_type: 'expense',
  account_id: 1,
  category_id: 1
};
const response = await fetch('/api/v1/transactions/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify(transaction)
});
```