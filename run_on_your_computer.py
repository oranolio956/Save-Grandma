#!/usr/bin/env python3
"""
Run this script on YOUR computer to generate the session string
Copy this file to your computer and run it there
"""

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