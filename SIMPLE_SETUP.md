# 🌕 Moon-Userbot - Ultra Simple Setup

## 🚀 One-Command Setup (Easiest)

Just run this single command:

```bash
./quick_start.sh
```

That's it! The bot will install everything and start running.

## 📋 What You Need

1. **Python 3.11+** (usually pre-installed on Linux)
2. **Your Telegram API credentials** (optional for testing)

## 🔑 Get Your API Credentials (Optional)

1. Go to https://my.telegram.org/
2. Login with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy your `API_ID` and `API_HASH`

## ⚙️ Configure (Optional)

After running `./quick_start.sh`, edit the `.env` file:

```bash
nano .env
```

Replace the default values with your real API credentials:

```
API_ID=your_real_api_id
API_HASH=your_real_api_hash
```

## 🎮 How to Use

- **Start**: `python3 main.py`
- **Stop**: Press `Ctrl+C`
- **Help**: Send `.help` in any Telegram chat

## 🔧 Manual Setup (If Needed)

If the quick start doesn't work, run:

```bash
./simple_setup.sh
```

This will guide you through the setup step by step.

## ❓ Troubleshooting

- **Permission denied**: Run `chmod +x *.sh`
- **Python not found**: Install Python 3.11+
- **Dependencies error**: Try `pip3 install --user -r requirements.txt`

## 🎯 That's It!

The bot is now running and ready to use. Send `.help` in Telegram to see all available commands.

---

**Note**: The default API keys are for testing only. Get your own from https://my.telegram.org/ for better security.