#!/bin/bash

# 🌕 Moon-Userbot - Ultra Simple Setup Script
# This script makes setting up Moon-Userbot as simple as possible

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌕 Moon-Userbot Ultra Simple Setup${NC}"
echo -e "${YELLOW}=====================================${NC}"
echo ""

# Check if we're in the right directory
if [[ ! -f "main.py" ]] || [[ ! -d "modules" ]]; then
    echo -e "${RED}❌ Error: Please run this script from the Moon-Userbot directory${NC}"
    exit 1
fi

# Check if already installed
if [[ -f ".env" ]] && [[ -f "my_account.session" ]]; then
    echo -e "${GREEN}✅ Moon-Userbot is already installed!${NC}"
    echo -e "${YELLOW}To start: python3 main.py${NC}"
    echo -e "${YELLOW}To stop: Ctrl+C${NC}"
    exit 0
fi

echo -e "${YELLOW}🔧 Installing dependencies...${NC}"

# Install Python dependencies
if command -v python3 &> /dev/null; then
    echo -e "${BLUE}📦 Installing Python packages...${NC}"
    pip3 install -r requirements.txt --user --break-system-packages 2>/dev/null || pip3 install -r requirements.txt --user
else
    echo -e "${RED}❌ Python3 not found. Please install Python 3.11+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed!${NC}"
echo ""

# Create minimal .env file with defaults
echo -e "${YELLOW}⚙️  Creating configuration...${NC}"

cat > .env << EOL
# Moon-Userbot Configuration
# Get your API credentials from: https://my.telegram.org/

# REQUIRED - Get these from https://my.telegram.org/
API_ID=2040
API_HASH=b18441a1ff607e10a989891a5462e627

# Database (using SQLite by default - no setup needed)
DATABASE_TYPE=sqlite3
DATABASE_NAME=db.sqlite3

# PM Limit (how many messages before warning)
PM_LIMIT=3

# Optional API Keys (leave empty if not needed)
APIFLASH_KEY=
RMBG_KEY=
VT_KEY=
GEMINI_KEY=
COHERE_KEY=
SECOND_SESSION=
EOL

echo -e "${GREEN}✅ Configuration created!${NC}"
echo ""

# Generate session string
echo -e "${YELLOW}🔑 Generating session...${NC}"
python3 string_gen.py

echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${YELLOW}=====================================${NC}"
echo ""
echo -e "${BLUE}📋 What's Next:${NC}"
echo -e "1. ${YELLOW}Get your API credentials:${NC} https://my.telegram.org/"
echo -e "2. ${YELLOW}Edit .env file:${NC} Replace API_ID and API_HASH with your own"
echo -e "3. ${YELLOW}Start the bot:${NC} python3 main.py"
echo ""
echo -e "${GREEN}🚀 Quick Start Commands:${NC}"
echo -e "• Start: ${BLUE}python3 main.py${NC}"
echo -e "• Stop:  ${BLUE}Ctrl+C${NC}"
echo -e "• Help:  ${BLUE}Send .help in Telegram${NC}"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo -e "• The default API keys are for testing only"
echo -e "• Get your own keys from https://my.telegram.org/"
echo -e "• Edit .env file with your real credentials"
echo ""
echo -e "${GREEN}✨ Enjoy using Moon-Userbot!${NC}"