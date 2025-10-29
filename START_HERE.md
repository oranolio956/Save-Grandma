# 🌕 Moon-Userbot - Start Here!

## 🚀 Choose Your Setup Method

### Option 1: Ultra Simple (Recommended)
```bash
python3 auto_setup.py
```
**What it does:** Installs everything and starts the bot automatically. Zero user input required!

### Option 2: One Command
```bash
./quick_start.sh
```
**What it does:** Installs dependencies, creates config, and starts the bot.

### Option 3: Guided Setup
```bash
./simple_setup.sh
```
**What it does:** Walks you through each step with helpful prompts.

### Option 4: Original Method
```bash
./install.sh
```
**What it does:** The original comprehensive installer with all options.

---

## 🎯 Quick Start (30 seconds)

1. **Run this command:**
   ```bash
   python3 auto_setup.py
   ```

2. **Get your API credentials** (optional for testing):
   - Go to https://my.telegram.org/
   - Login with your phone number
   - Create an application
   - Copy API_ID and API_HASH

3. **Edit config** (if you got your own API keys):
   ```bash
   nano .env
   ```
   Replace the default values with your real credentials.

4. **Start using:**
   - Send `.help` in any Telegram chat
   - The bot is now running!

---

## 🛠️ What Each Script Does

| Script | Time | User Input | Best For |
|--------|------|------------|----------|
| `auto_setup.py` | 30 sec | None | Quick testing |
| `quick_start.sh` | 1 min | None | Fast setup |
| `simple_setup.sh` | 2-3 min | Minimal | Guided setup |
| `install.sh` | 5+ min | Full | Complete control |

---

## 🎮 How to Use

- **Start bot:** `python3 main.py`
- **Stop bot:** Press `Ctrl+C`
- **Get help:** Send `.help` in Telegram
- **View logs:** Check terminal output

---

## 🔧 Troubleshooting

**Permission denied?**
```bash
chmod +x *.sh
```

**Python not found?**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

**Dependencies error?**
```bash
pip3 install --user -r requirements.txt
```

---

## 🎉 That's It!

The bot is now running and ready to use. Send `.help` in Telegram to see all available commands.

**Need help?** Check the [full documentation](README.md) or join the [support chat](https://t.me/moonub_chat).