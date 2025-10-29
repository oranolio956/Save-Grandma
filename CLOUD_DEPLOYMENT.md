# 🌕 Moon-Userbot - Cloud Deployment Guide

**Deploy Moon-Userbot to the cloud without needing a computer!**

## 🚀 Quick Deploy Options

### Option 1: Render (Recommended - Free)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/The-MoonTg-project/Moon-Userbot)

### Option 2: Vercel (Free)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/The-MoonTg-project/Moon-Userbot)

### Option 3: Railway (Free)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

---

## 📋 Step-by-Step Deployment

### 🌟 Method 1: Render (Easiest)

1. **Click the Deploy Button Above**
   - Or go to: https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub account

2. **Configure the Service**
   - **Name**: `moon-userbot` (or any name you like)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

3. **Set Environment Variables**
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   STRINGSESSION=your_session_string
   DATABASE_TYPE=sqlite3
   DATABASE_NAME=db.sqlite3
   PM_LIMIT=3
   ```

4. **Deploy!**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Your bot will be running at the provided URL

### 🌟 Method 2: Vercel

1. **Fork the Repository**
   - Go to: https://github.com/The-MoonTg-project/Moon-Userbot
   - Click "Fork" to create your own copy

2. **Deploy to Vercel**
   - Go to: https://vercel.com
   - Click "New Project"
   - Import your forked repository
   - Vercel will auto-detect it's a Python project

3. **Set Environment Variables**
   - In Vercel dashboard, go to "Settings" → "Environment Variables"
   - Add all the variables from the list above

4. **Deploy!**
   - Click "Deploy"
   - Your bot will be running at `your-project.vercel.app`

### 🌟 Method 3: Railway

1. **Connect GitHub**
   - Go to: https://railway.app
   - Sign in with GitHub
   - Click "New Project"

2. **Deploy from GitHub**
   - Select "Deploy from GitHub repo"
   - Choose the Moon-Userbot repository
   - Railway will auto-detect the configuration

3. **Set Environment Variables**
   - Go to "Variables" tab
   - Add all required environment variables

4. **Deploy!**
   - Railway will automatically deploy
   - Your bot will be running at the provided URL

---

## 🔑 Getting Your API Credentials

### Step 1: Get API_ID and API_HASH
1. Go to: https://my.telegram.org/
2. Login with your phone number
3. Go to "API development tools"
4. Click "Create application"
5. Fill in the form:
   - **App title**: `Moon-Userbot`
   - **Short name**: `moonub`
   - **Platform**: `Desktop`
6. Copy your `API_ID` and `API_HASH`

### Step 2: Generate Session String
1. **Option A: Use the online generator**
   - Go to: https://replit.com/@ABHITHEMODDER/MoonUb-Session-Gen
   - Enter your API_ID and API_HASH
   - Login with your phone number
   - Copy the generated session string

2. **Option B: Use the local generator**
   ```bash
   python3 string_gen.py
   ```
   - Enter your API_ID and API_HASH
   - Login with your phone number
   - Copy the generated session string

---

## ⚙️ Environment Variables

Set these in your cloud platform:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `API_ID` | ✅ Yes | Your Telegram API ID | `1234567` |
| `API_HASH` | ✅ Yes | Your Telegram API Hash | `abcdef123456` |
| `STRINGSESSION` | ✅ Yes | Your session string | `1BVts...` |
| `DATABASE_TYPE` | ❌ No | Database type | `sqlite3` |
| `DATABASE_NAME` | ❌ No | Database name | `db.sqlite3` |
| `PM_LIMIT` | ❌ No | PM warning limit | `3` |
| `APIFLASH_KEY` | ❌ No | For web screenshots | `your_key` |
| `RMBG_KEY` | ❌ No | For background removal | `your_key` |
| `VT_KEY` | ❌ No | For VirusTotal | `your_key` |
| `GEMINI_KEY` | ❌ No | For Gemini AI | `your_key` |
| `COHERE_KEY` | ❌ No | For Cohere AI | `your_key` |

---

## 🎮 Using Your Deployed Bot

### Check Status
- Visit your deployment URL
- You'll see a status page showing if the bot is running

### Bot Commands
Send these in any Telegram chat:
- `.help` - Show all commands
- `.ping` - Test if bot is working
- `.id` - Get your user ID
- `.afk` - Set AFK status

### Monitor Your Bot
- **Render**: Check the "Logs" tab in your dashboard
- **Vercel**: Check the "Functions" tab
- **Railway**: Check the "Deployments" tab

---

## 🔧 Troubleshooting

### Bot Not Starting?
1. **Check Environment Variables**
   - Make sure all required variables are set
   - Verify API_ID and API_HASH are correct

2. **Check Session String**
   - Regenerate your session string
   - Make sure it's complete and valid

3. **Check Logs**
   - Look at the deployment logs for errors
   - Common issues: missing variables, invalid session

### Bot Not Responding?
1. **Check if it's running**
   - Visit your deployment URL
   - Look for "🟢 Running" status

2. **Restart the service**
   - In your platform dashboard, restart the service
   - This will reload the bot

### Session Expired?
1. **Generate new session**
   - Use the session generator again
   - Update the STRINGSESSION variable
   - Restart the service

---

## 💡 Pro Tips

1. **Free Tier Limits**
   - Render: 750 hours/month (free)
   - Vercel: 100GB bandwidth/month (free)
   - Railway: $5 credit/month (free)

2. **Keep Your Bot Running**
   - Free tiers may sleep after inactivity
   - Use a service like UptimeRobot to ping your bot
   - Or upgrade to a paid plan for 24/7 uptime

3. **Security**
   - Never share your API credentials
   - Use environment variables, not hardcoded values
   - Regularly rotate your session string

---

## 🎉 You're Done!

Your Moon-Userbot is now running in the cloud! 

- ✅ No computer needed
- ✅ Runs 24/7 (on paid plans)
- ✅ Accessible from anywhere
- ✅ Easy to manage and monitor

**Need help?** Join the [support chat](https://t.me/moonub_chat) or check the [documentation](README.md).