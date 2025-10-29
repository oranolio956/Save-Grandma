#!/usr/bin/env python3
"""
🌕 Moon-Userbot - Automatic Setup Script
This script handles everything automatically with zero user input.
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🌕 Moon-Userbot - Automatic Setup")
    print("=" * 40)
    
    # Check if already set up
    if os.path.exists(".env") and os.path.exists("my_account.session"):
        print("✅ Already set up! Starting bot...")
        os.system("python3 main.py")
        return
    
    print("🔧 Installing dependencies...")
    
    # Install requirements
    success, stdout, stderr = run_command("pip3 install -r requirements.txt --user --break-system-packages", check=False)
    if not success:
        success, stdout, stderr = run_command("pip3 install -r requirements.txt --user", check=False)
        if not success:
            print("❌ Failed to install dependencies. Trying with pip...")
            success, stdout, stderr = run_command("pip install -r requirements.txt --user", check=False)
    
    if not success:
        print("❌ Could not install dependencies automatically.")
        print("Please run: pip3 install -r requirements.txt")
        return
    
    print("✅ Dependencies installed!")
    
    # Create .env file
    print("⚙️  Creating configuration...")
    
    env_content = """# Moon-Userbot Configuration
API_ID=2040
API_HASH=b18441a1ff607e10a989891a5462e627
DATABASE_TYPE=sqlite3
DATABASE_NAME=db.sqlite3
PM_LIMIT=3
APIFLASH_KEY=
RMBG_KEY=
VT_KEY=
GEMINI_KEY=
COHERE_KEY=
SECOND_SESSION=
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Configuration created!")
    
    # Generate session
    print("🔑 Generating session...")
    success, stdout, stderr = run_command("python3 string_gen.py", check=False)
    
    if success:
        print("✅ Session generated!")
    else:
        print("⚠️  Session generation failed, but continuing...")
    
    print("\n🎉 Setup Complete!")
    print("=" * 40)
    print("📋 Next steps:")
    print("1. Get your API credentials: https://my.telegram.org/")
    print("2. Edit .env file with your real API_ID and API_HASH")
    print("3. Start the bot: python3 main.py")
    print("\n🚀 Starting bot now...")
    print("(Press Ctrl+C to stop)")
    print("=" * 40)
    
    # Start the bot
    os.system("python3 main.py")

if __name__ == "__main__":
    main()