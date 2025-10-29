#!/usr/bin/env python3
"""
Generate Moon-Userbot session string locally
This script will help you generate a session string without using Replit
"""

import os
import sys
from pyrogram import Client

def generate_session():
    """Generate session string for Moon-Userbot"""
    
    print("🌕 Moon-Userbot - Local Session Generator")
    print("=" * 50)
    print()
    
    # Your API credentials
    api_id = 22595574
    api_hash = "6f8f406b4cc917a55c639f78be182c8d"
    
    print(f"Using API_ID: {api_id}")
    print(f"Using API_HASH: {api_hash}")
    print()
    print("📱 This will create a session file for your Moon-Userbot.")
    print("⚠️  You'll need to complete the login process with your phone number.")
    print()
    
    try:
        # Create a client instance
        app = Client("my_account", api_id, api_hash)
        
        print("🔑 Starting session generation...")
        print("📱 You'll be asked for your phone number and verification code.")
        print()
        
        # Start the client to generate session
        with app:
            print("✅ Session generated successfully!")
            print("📁 Session file created: my_account.session")
            print()
            print("📋 Next steps:")
            print("1. Upload the 'my_account.session' file to your Vercel project")
            print("2. Or copy the session string from the file")
            print("3. Add it to your Vercel environment variables")
            print()
            print("🚀 Your bot is ready to use!")
            
    except KeyboardInterrupt:
        print("\n❌ Session generation cancelled by user")
    except Exception as e:
        print(f"❌ Error generating session: {e}")
        print()
        print("💡 Make sure you have pyrogram installed:")
        print("   pip install pyrogram")

if __name__ == "__main__":
    generate_session()