# 🔑 Quick Session Generation Guide

## 🚀 **Easiest Method - Run on Your Computer:**

### Step 1: Download the Script
I've created a simple script for you. Copy this code to a file called `session_gen.py` on your computer:

```python
from pyrogram import Client

# Your API credentials
api_id = 22595574
api_hash = "6f8f406b4cc917a55c639f78be182c8d"

print("🌕 Moon-Userbot - Session Generator")
print("=" * 40)
print(f"API_ID: {api_id}")
print(f"API_HASH: {api_hash}")
print()
print("📱 This will ask for your phone number and verification code.")
print("⚠️  Make sure you have pyrogram installed: pip install pyrogram")
print()

try:
    # Create client and start session generation
    with Client("my_account", api_id, api_hash) as app:
        print("✅ Session generated successfully!")
        print("📁 Session file created: my_account.session")
        print()
        print("📋 Next steps:")
        print("1. Copy the 'my_account.session' file")
        print("2. Go to: https://vercel.com/asdsas-projects-7b4d3f47/workspace/settings/environment-variables")
        print("3. Find STRINGSESSION and click 'Edit'")
        print("4. Upload the session file or copy its contents")
        print("5. Save and your bot will be ready!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("💡 Make sure to install pyrogram first:")
    print("   pip install pyrogram")
```

### Step 2: Install Pyrogram
```bash
pip install pyrogram
```

### Step 3: Run the Script
```bash
python session_gen.py
```

### Step 4: Follow the Prompts
- Enter your phone number (with country code, e.g., +1234567890)
- Enter the verification code from Telegram
- Enter your password (if you have 2FA enabled)

### Step 5: Get Your Session
- The script will create `my_account.session` file
- This contains your session string

---

## 🌐 **Alternative - Online Generators:**

### Option 1: Telegram Bot
1. Go to: https://t.me/SessionStringGeneratorBot
2. Start the bot
3. Send `/start`
4. Follow the instructions

### Option 2: Website Generator
1. Go to: https://session-generator.ml/
2. Enter your API credentials:
   - API_ID: `22595574`
   - API_HASH: `6f8f406b4cc917a55c639f78be182c8d`
3. Login with your phone number
4. Copy the session string

---

## 📋 **After Getting Your Session String:**

1. Go to: https://vercel.com/asdsas-projects-7b4d3f47/workspace/settings/environment-variables
2. Find `STRINGSESSION` in the list
3. Click "Edit"
4. Paste your session string
5. Save

**Your Moon-Userbot will then be fully operational!** 🚀

---

## ❓ **Need Help?**

- **Python not installed?** Download from: https://python.org
- **Pip not working?** Try: `python -m pip install pyrogram`
- **Still having issues?** Try the online generators instead