#!/bin/bash

# Family Budget Manager Setup Script

echo "🏠 Setting up Family Budget Manager..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Please edit .env file with your configuration"
else
    echo "✅ .env file already exists"
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "🌐 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Install bot dependencies
echo "🤖 Installing bot dependencies..."
cd bot
pip install -r requirements.txt
cd ..

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   docker-compose up -d"
echo ""
echo "📖 Or for development:"
echo "   Backend:  cd backend && uvicorn app.main:app --reload"
echo "   Frontend: cd frontend && npm start"
echo "   Bot:      cd bot && python main.py"
echo ""
echo "🌐 Access points:"
echo "   Web UI:     http://localhost:3000"
echo "   API docs:   http://localhost:8000/docs"
echo "   Database:   localhost:5432"