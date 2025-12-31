#!/bin/bash

echo "🌾 Setting up FarmConnect AI..."

# Create directories
mkdir -p backend frontend data audio models temp

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
pip install -r requirements.txt
cd ..

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from backend.models import init_db; init_db()"

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend:  cd backend && uvicorn main:app --reload"
echo "2. Frontend: cd frontend && streamlit run app.py"
