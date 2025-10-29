#!/usr/bin/env python3
"""
Simple session generator for Moon-Userbot
"""

import os
from pyrogram import Client

def generate_session():
    """Generate a session string for Moon-Userbot"""
    
    # Read API credentials from .env
    api_id = 2040  # Default API ID
    api_hash = "b18441a1ff607e10a989891a5462e627"  # Default API Hash
    
    # Try to read from .env file
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("API_ID="):
                    try:
                        api_id = int(line.split("=")[1].strip())
                    except:
                        pass
                elif line.startswith("API_HASH="):
                    api_hash = line.split("=")[1].strip()
    
    print(f"Using API_ID: {api_id}")
    print(f"Using API_HASH: {api_hash}")
    
    # Create a temporary client to generate session
    try:
        with Client("temp_session", api_id, api_hash) as app:
            print("✅ Session generated successfully!")
            print("📱 Please check your phone for Telegram verification code")
            print("🔑 Session will be saved as 'temp_session.session'")
            return True
    except Exception as e:
        print(f"❌ Session generation failed: {e}")
        print("💡 You can generate session manually by running: python3 string_gen.py")
        return False

if __name__ == "__main__":
    generate_session()