# 🚀 Replit One-Click Session Generator

## 🌐 **Step 1: Go to Replit**
- Go to: https://replit.com
- Click "Create Repl"
- Choose "Python" as the language
- Name it "Moon-Userbot-Session"

## 🔧 **Step 2: Install Pyrogram**
In the Replit console, run:
```bash
pip install pyrogram
```

## 📝 **Step 3: Copy and Paste This Code**

Replace all the code in `main.py` with this:

```python
# 🌕 Moon-Userbot - Replit One-Click Session Generator
# Just run this and follow the prompts!

from pyrogram import Client
import asyncio

async def generate_session():
    # Your API credentials (already configured)
    api_id = 22595574
    api_hash = "6f8f406b4cc917a55c639f78be182c8d"
    
    print("🌕 Moon-Userbot - Replit One-Click Session Generator")
    print("=" * 60)
    print("✅ API credentials already configured!")
    print("✅ Pyrogram installed!")
    print("✅ Everything is ready!")
    print()
    print("📱 Just enter your phone number and verification code when asked.")
    print("🔑 I'll generate your session string automatically!")
    print()
    
    # Get phone number
    phone = input("📱 Enter your phone number (with country code, e.g., +1234567890): ")
    
    # Create client
    app = Client("my_account", api_id, api_hash)
    
    try:
        print("🔄 Starting session generation...")
        print("📱 Check your Telegram for verification code...")
        
        # Start the client (this will ask for verification code)
        await app.start()
        
        # Get the session string
        session_string = app.export_session_string()
        
        print("\n" + "🎉" * 20)
        print("✅ SUCCESS! Your session string is ready!")
        print("🎉" * 20)
        print()
        print("🔑 Your session string:")
        print("-" * 60)
        print(session_string)
        print("-" * 60)
        print()
        print("📋 What to do next:")
        print("1. Copy the session string above")
        print("2. Go to: https://vercel.com/asdsas-projects-7b4d3f47/workspace/settings/environment-variables")
        print("3. Find STRINGSESSION and click 'Edit'")
        print("4. Paste the session string")
        print("5. Click 'Save'")
        print()
        print("🎉 Your Moon-Userbot will be ready!")
        
        # Save session to file
        with open("session.txt", "w") as f:
            f.write(session_string)
        print("💾 Session also saved to 'session.txt' file!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you enter the correct verification code")
        print("🔄 Try running the code again")
    
    finally:
        await app.stop()

# Run the session generator
asyncio.run(generate_session())
```

## ▶️ **Step 4: Run the Code**
- Click the "Run" button in Replit
- Enter your phone number when prompted
- Enter the verification code from Telegram
- Copy the session string that appears

## 📋 **Step 5: Add to Vercel**
1. Go to: https://vercel.com/asdsas-projects-7b4d3f47/workspace/settings/environment-variables
2. Find `STRINGSESSION` and click "Edit"
3. Paste your session string
4. Save

## 🎉 **That's It!**

Your Moon-Userbot will be fully operational in the cloud! 🚀

---

## 💡 **Replit Advantages:**
- ✅ No installation needed
- ✅ Runs in your browser
- ✅ Saves session to file automatically
- ✅ Easy to use interface
- ✅ Free to use