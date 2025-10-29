#!/usr/bin/env python3
"""
Interactive session generator for Moon-Userbot
This will work better for interactive input
"""

import os
import sys
from pyrogram import Client

def main():
    print("🌕 Moon-Userbot - Interactive Session Generator")
    print("=" * 55)
    print()
    
    # Your API credentials
    api_id = 22595574
    api_hash = "6f8f406b4cc917a55c639f78be182c8d"
    
    print(f"Using API_ID: {api_id}")
    print(f"Using API_HASH: {api_hash}")
    print()
    print("📱 Ready to generate your session!")
    print("⚠️  This will ask for your phone number and verification code.")
    print()
    
    try:
        # Create a client instance
        app = Client("my_account", api_id, api_hash)
        
        print("🔑 Starting session generation...")
        print("📱 Please enter your phone number when prompted.")
        print()
        
        # Start the client to generate session
        app.start()
        
        print("✅ Session generated successfully!")
        print("📁 Session file created: my_account.session")
        print()
        print("📋 Next steps:")
        print("1. The session file is ready")
        print("2. Add the session string to your Vercel environment variables")
        print("3. Your bot will be fully operational!")
        
        # Stop the client
        app.stop()
        
    except KeyboardInterrupt:
        print("\n❌ Session generation cancelled by user")
    except Exception as e:
        print(f"❌ Error generating session: {e}")
        print()
        print("💡 This might be due to the interactive nature of the process.")
        print("   Try running it locally on your computer instead.")

if __name__ == "__main__":
    main()