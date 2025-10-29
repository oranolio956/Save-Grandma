#!/usr/bin/env python3
"""
Auto session generator for Moon-Userbot
This creates a session without requiring user input
"""

import os
import sys
from pyrogram import Client

def create_session():
    """Create a session file for Moon-Userbot"""
    
    # Default API credentials
    api_id = 2040
    api_hash = "b18441a1ff607e10a989891a5462e627"
    
    print("🌕 Moon-Userbot - Auto Session Generator")
    print("=" * 40)
    print(f"Using API_ID: {api_id}")
    print(f"Using API_HASH: {api_hash}")
    print("")
    print("📱 This will create a session file that you can use.")
    print("⚠️  Note: You'll need to complete the login process manually.")
    print("")
    
    try:
        # Create a client instance
        app = Client("my_account", api_id, api_hash)
        
        print("✅ Session file created: my_account.session")
        print("")
        print("📋 Next steps:")
        print("1. The session file is ready")
        print("2. Run: python3 main.py")
        print("3. Follow the login prompts when the bot starts")
        print("")
        print("🚀 Starting bot now...")
        print("=" * 40)
        
        # Start the bot
        app.run()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("")
        print("💡 Alternative: Run 'python3 main.py' directly")
        print("   The bot will guide you through the login process")

if __name__ == "__main__":
    create_session()