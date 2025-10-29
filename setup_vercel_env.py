#!/usr/bin/env python3
"""
Script to set up Vercel environment variables for Moon-Userbot
"""

import subprocess
import sys

def run_vercel_command(cmd):
    """Run a Vercel command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def add_env_var(name, value, token):
    """Add an environment variable to Vercel"""
    cmd = f'vercel env add {name} production main --token {token}'
    
    # Create a temporary file with the value
    with open(f'/tmp/{name}.txt', 'w') as f:
        f.write(value)
    
    # Run the command with input from file
    cmd_with_input = f'vercel env add {name} production main --token {token} < /tmp/{name}.txt'
    
    success, stdout, stderr = run_vercel_command(cmd_with_input)
    
    if success:
        print(f"✅ Added {name}")
    else:
        print(f"❌ Failed to add {name}: {stderr}")
    
    return success

def main():
    token = "EzwaE6zJzYuFPeTxRdQxJLUI"
    
    print("🌕 Setting up Moon-Userbot environment variables on Vercel...")
    print("=" * 60)
    
    # Environment variables to add
    env_vars = {
        "API_ID": "2040",
        "API_HASH": "b18441a1ff607e10a989891a5462e627",
        "STRINGSESSION": "",
        "DATABASE_TYPE": "sqlite3",
        "DATABASE_NAME": "db.sqlite3",
        "PM_LIMIT": "3",
        "APIFLASH_KEY": "",
        "RMBG_KEY": "",
        "VT_KEY": "",
        "GEMINI_KEY": "",
        "COHERE_KEY": "",
        "SECOND_SESSION": ""
    }
    
    success_count = 0
    total_count = len(env_vars)
    
    for name, value in env_vars.items():
        if add_env_var(name, value, token):
            success_count += 1
    
    print("=" * 60)
    print(f"✅ Successfully added {success_count}/{total_count} environment variables")
    
    if success_count == total_count:
        print("🎉 All environment variables configured!")
        print("📋 Next steps:")
        print("1. Get your API credentials from: https://my.telegram.org/")
        print("2. Generate session string from: https://replit.com/@ABHITHEMODDER/MoonUb-Session-Gen")
        print("3. Update API_ID, API_HASH, and STRINGSESSION in Vercel dashboard")
        print("4. Redeploy your project")
    else:
        print("⚠️  Some variables failed to add. You may need to add them manually in the Vercel dashboard.")

if __name__ == "__main__":
    main()