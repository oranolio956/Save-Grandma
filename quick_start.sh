#!/bin/bash

# 🌕 Moon-Userbot - One Command Setup
# Run this single command to get everything working!

echo "🌕 Moon-Userbot Quick Start"
echo "=========================="
echo ""

# Check if already set up
if [[ -f ".env" ]] && [[ -f "my_account.session" ]]; then
    echo "✅ Already set up! Starting bot..."
    python3 main.py
    exit 0
fi

echo "🔧 Setting up Moon-Userbot..."

# Install dependencies
pip3 install -r requirements.txt --user --break-system-packages 2>/dev/null || pip3 install -r requirements.txt --user

# Create .env with defaults
cat > .env << EOL
API_ID=2040
API_HASH=b18441a1ff607e10a989891a5462e627
DATABASE_TYPE=sqlite3
DATABASE_NAME=db.sqlite3
PM_LIMIT=3
APIFLASH_KEY=
RMBG_KEY=
VT_KEY=
GEMINI_KEY=
COHERE_KEY=
SECOND_SESSION=
EOL

# Generate session
python3 string_gen.py

echo ""
echo "🎉 Setup complete!"
echo "⚠️  Using default API keys - get your own from https://my.telegram.org/"
echo "🚀 Starting bot..."
echo ""

python3 main.py