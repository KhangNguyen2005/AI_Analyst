#!/bin/bash
# Quick setup script for AI Analyst

echo "🤖 AI Analyst - Setup Script"
echo "============================"
echo ""

# Check Python version
echo "✓ Checking Python..."
python --version

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  venv already exists"
else
    python -m venv venv
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source venv/bin/activate 2>/dev/null || venv\Scripts\activate 2>/dev/null

# Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install -r requirements.txt --quiet

# Create .env file
echo ""
echo "✓ Setting up configuration..."
if [ -f ".env" ]; then
    echo "  .env already exists"
else
    cp .env.example .env
    echo "  Created .env - please edit with your API keys!"
fi

# Run tests
echo ""
echo "✓ Running system tests..."
python test_setup.py

echo ""
echo "============================"
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run: python app.py"
echo "3. Open: http://localhost:5000"
echo ""
echo "For more info, see QUICKSTART.md"
