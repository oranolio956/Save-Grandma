from flask import Flask
import os
import threading
import time

app = Flask(__name__)

# Global variable to track if bot is running
bot_running = False
bot_thread = None

def run_bot():
    """Run the Moon-Userbot in a separate thread"""
    global bot_running
    try:
        import main
        bot_running = True
        print("🌕 Moon-Userbot started successfully!")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        bot_running = False

@app.route("/")
def hello_world():
    global bot_running
    status = "🟢 Running" if bot_running else "🔴 Stopped"
    return f"""
    <html>
    <head>
        <title>🌕 Moon-Userbot</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .status {{ font-size: 24px; margin: 20px; }}
            .info {{ background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px; }}
        </style>
    </head>
    <body>
        <h1>🌕 Moon-Userbot</h1>
        <div class="status">Status: {status}</div>
        <div class="info">
            <p><strong>Bot is running on the cloud!</strong></p>
            <p>Send <code>.help</code> in any Telegram chat to see commands.</p>
            <p>This page refreshes every 30 seconds.</p>
        </div>
    </body>
    </html>
    """

@app.route("/start")
def start_bot():
    """Start the bot"""
    global bot_thread, bot_running
    if not bot_running:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        return "🚀 Bot starting..."
    return "✅ Bot is already running!"

@app.route("/status")
def bot_status():
    """Check bot status"""
    global bot_running
    return {"status": "running" if bot_running else "stopped"}

if __name__ == "__main__":
    # Start bot in background
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
