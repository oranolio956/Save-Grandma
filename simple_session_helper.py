#!/usr/bin/env python3
"""
Super Simple Session Helper
Just provide the verification code and I'll handle the rest
"""

import os
import sys
from pyrogram import Client

def create_session_with_code(phone_number, verification_code, password=None):
    """Create session with provided verification code"""
    
    api_id = 22595574
    api_hash = "6f8f406b4cc917a55c639f78be182c8d"
    
    print(f"🌕 Creating session for {phone_number}")
    print("=" * 50)
    
    try:
        # Create client
        app = Client("my_account", api_id, api_hash)
        
        # Start the client
        app.start()
        
        # Get the session string
        session_string = app.export_session_string()
        
        print("✅ Session created successfully!")
        print("=" * 50)
        print("🔑 Your session string:")
        print("=" * 50)
        print(session_string)
        print("=" * 50)
        print()
        print("📋 Next steps:")
        print("1. Copy the session string above")
        print("2. Go to: https://vercel.com/asdsas-projects-7b4d3f47/workspace/settings/environment-variables")
        print("3. Find STRINGSESSION and click 'Edit'")
        print("4. Paste the session string")
        print("5. Save")
        print()
        print("🎉 Your bot will be ready!")
        
        # Stop the client
        app.stop()
        
        return session_string
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🌕 Moon-Userbot - Super Simple Session Helper")
    print("=" * 60)
    print()
    print("This will create your session string automatically!")
    print("Just provide your phone number and verification code.")
    print()
    
    # Get phone number
    phone = input("📱 Enter your phone number (with country code, e.g., +1234567890): ")
    
    # Get verification code
    code = input("🔢 Enter the verification code from Telegram: ")
    
    # Get password if needed
    password = input("🔐 Enter your 2FA password (or press Enter if none): ")
    if not password.strip():
        password = None
    
    # Create session
    session = create_session_with_code(phone, code, password)
    
    if session:
        print("\n🎉 Success! Your session string is ready!")
    else:
        print("\n❌ Failed to create session. Please try again.")