#!/usr/bin/env python3
"""
Flask Web Dashboard - Production-ready control panel for Seeking Chat Bot
Provides real-time monitoring, configuration, and control capabilities
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import secrets
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from loguru import logger
import yaml

from seeking_bot import SeekingBot
from seeking_bot.core.browser_manager import BrowserManager
from seeking_bot.ai.grok_client import GrokClient
from seeking_bot.utils.encryption import EncryptionManager
from seeking_bot.database.models import User, Conversation, Message
from seeking_bot.database.session_manager import SessionManager

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize Flask app
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Global bot instance
bot_instance: Optional[SeekingBot] = None
bot_lock = asyncio.Lock()

# In-memory user store (replace with database in production)
users_db = {}


class DashboardUser(UserMixin):
    """User model for dashboard authentication"""
    def __init__(self, user_id, username, password_hash):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return users_db.get(user_id)


def require_api_key(f):
    """Decorator to require API key for certain endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Main dashboard page"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Login page"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        # Check credentials
        user = None
        for u in users_db.values():
            if u.username == username:
                user = u
                break
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return jsonify({'success': True, 'redirect': url_for('index')})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')


@app.route('/register', methods=['POST'])
@limiter.limit("3 per hour")
def register():
    """Register new dashboard user"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Check if user exists
    for u in users_db.values():
        if u.username == username:
            return jsonify({'error': 'User already exists'}), 409
    
    # Create new user
    user_id = secrets.token_hex(16)
    password_hash = generate_password_hash(password)
    user = DashboardUser(user_id, username, password_hash)
    users_db[user_id] = user
    
    return jsonify({'success': True, 'message': 'User created successfully'})


@app.route('/logout')
@login_required
def logout():
    """Logout current user"""
    logout_user()
    return redirect(url_for('login'))


@app.route('/api/bot/start', methods=['POST'])
@login_required
@limiter.limit("5 per hour")
async def start_bot():
    """Start the bot with provided credentials"""
    global bot_instance
    
    data = request.get_json()
    seeking_username = data.get('username')
    seeking_password = data.get('password')
    
    if not seeking_username or not seeking_password:
        return jsonify({'error': 'Seeking.com credentials required'}), 400
    
    try:
        async with bot_lock:
            if bot_instance and bot_instance.status.value == 'active':
                return jsonify({'error': 'Bot is already running'}), 409
            
            # Create new bot instance
            bot_instance = SeekingBot(config)
            
            # Start bot
            success = await bot_instance.start(seeking_username, seeking_password)
            
            if success:
                # Emit status update via WebSocket
                socketio.emit('bot_status', {
                    'status': 'active',
                    'message': 'Bot started successfully'
                }, room='control')
                
                return jsonify({
                    'success': True,
                    'message': 'Bot started successfully',
                    'status': bot_instance.status.value
                })
            else:
                return jsonify({'error': 'Failed to start bot'}), 500
                
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/bot/stop', methods=['POST'])
@login_required
async def stop_bot():
    """Stop the bot"""
    global bot_instance
    
    try:
        async with bot_lock:
            if not bot_instance:
                return jsonify({'error': 'Bot is not running'}), 404
            
            await bot_instance.stop()
            
            # Get final statistics
            stats = bot_instance.get_stats()
            
            bot_instance = None
            
            # Emit status update
            socketio.emit('bot_status', {
                'status': 'stopped',
                'message': 'Bot stopped',
                'stats': stats
            }, room='control')
            
            return jsonify({
                'success': True,
                'message': 'Bot stopped successfully',
                'stats': stats
            })
            
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/bot/pause', methods=['POST'])
@login_required
async def pause_bot():
    """Pause bot operations"""
    global bot_instance
    
    if not bot_instance:
        return jsonify({'error': 'Bot is not running'}), 404
    
    await bot_instance.pause()
    
    socketio.emit('bot_status', {
        'status': 'paused',
        'message': 'Bot paused'
    }, room='control')
    
    return jsonify({'success': True, 'message': 'Bot paused'})


@app.route('/api/bot/resume', methods=['POST'])
@login_required
async def resume_bot():
    """Resume bot operations"""
    global bot_instance
    
    if not bot_instance:
        return jsonify({'error': 'Bot is not running'}), 404
    
    await bot_instance.resume()
    
    socketio.emit('bot_status', {
        'status': 'active',
        'message': 'Bot resumed'
    }, room='control')
    
    return jsonify({'success': True, 'message': 'Bot resumed'})


@app.route('/api/bot/status')
@login_required
def get_bot_status():
    """Get current bot status and statistics"""
    global bot_instance
    
    if not bot_instance:
        return jsonify({
            'status': 'stopped',
            'stats': {
                'messages_read': 0,
                'messages_sent': 0,
                'active_chats': 0,
                'errors': 0
            }
        })
    
    stats = bot_instance.get_stats()
    
    return jsonify({
        'status': bot_instance.status.value,
        'stats': stats,
        'active_sessions': len(bot_instance.active_sessions),
        'config': {
            'rate_limit': config['rate_limiting']['messages_per_hour'],
            'response_delay': config['anti_detection']['random_delays']
        }
    })


@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def manage_config():
    """Get or update bot configuration"""
    global config
    
    if request.method == 'GET':
        # Return current configuration (sanitized)
        safe_config = {
            'templates': config.get('templates', []),
            'keywords': config.get('keywords', {}),
            'safety': config.get('safety', {}),
            'rate_limiting': config.get('rate_limiting', {}),
            'anti_detection': config.get('anti_detection', {})
        }
        return jsonify(safe_config)
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Update configuration
        if 'templates' in data:
            config['templates'] = data['templates']
        if 'keywords' in data:
            config['keywords'] = data['keywords']
        if 'safety' in data:
            config['safety'].update(data['safety'])
        if 'rate_limiting' in data:
            config['rate_limiting'].update(data['rate_limiting'])
        
        # Save configuration
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Update bot instance if running
        if bot_instance:
            bot_instance.config = config
        
        return jsonify({'success': True, 'message': 'Configuration updated'})


@app.route('/api/templates', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_templates():
    """Manage response templates"""
    if request.method == 'GET':
        return jsonify({'templates': config.get('templates', [])})
    
    elif request.method == 'POST':
        data = request.get_json()
        template = data.get('template')
        
        if not template:
            return jsonify({'error': 'Template text required'}), 400
        
        if 'templates' not in config:
            config['templates'] = []
        
        config['templates'].append(template)
        
        # Save config
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return jsonify({'success': True, 'message': 'Template added'})
    
    elif request.method == 'DELETE':
        data = request.get_json()
        index = data.get('index')
        
        if index is not None and 0 <= index < len(config.get('templates', [])):
            config['templates'].pop(index)
            
            # Save config
            with open('config.yaml', 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            return jsonify({'success': True, 'message': 'Template deleted'})
        
        return jsonify({'error': 'Invalid template index'}), 400


@app.route('/api/keywords', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_keywords():
    """Manage keyword responses"""
    if request.method == 'GET':
        return jsonify({'keywords': config.get('keywords', {})})
    
    elif request.method == 'POST':
        data = request.get_json()
        keyword = data.get('keyword')
        response = data.get('response')
        
        if not keyword or not response:
            return jsonify({'error': 'Keyword and response required'}), 400
        
        if 'keywords' not in config:
            config['keywords'] = {}
        
        config['keywords'][keyword.lower()] = response
        
        # Save config
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return jsonify({'success': True, 'message': 'Keyword added'})
    
    elif request.method == 'DELETE':
        data = request.get_json()
        keyword = data.get('keyword')
        
        if keyword and keyword in config.get('keywords', {}):
            del config['keywords'][keyword]
            
            # Save config
            with open('config.yaml', 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            return jsonify({'success': True, 'message': 'Keyword deleted'})
        
        return jsonify({'error': 'Keyword not found'}), 404


@app.route('/api/logs')
@login_required
def get_logs():
    """Get message logs"""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # In production, fetch from database
    # For now, return mock data
    logs = [
        {
            'timestamp': datetime.now().isoformat(),
            'type': 'sent',
            'message': 'Hi there! How are you?',
            'chat_id': 'abc123',
            'user': 'Alice'
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'type': 'received',
            'message': 'Hey! I\'m doing great, thanks!',
            'chat_id': 'abc123',
            'user': 'Alice'
        }
    ]
    
    return jsonify({
        'logs': logs[offset:offset+limit],
        'total': len(logs)
    })


@app.route('/api/metrics')
@login_required
def get_metrics():
    """Get bot performance metrics"""
    global bot_instance
    
    metrics = {
        'response_time': {
            'average': 2.5,
            'min': 1.2,
            'max': 5.8
        },
        'success_rate': 0.95,
        'conversations': {
            'total': 150,
            'active': 5,
            'completed': 145
        },
        'ai_usage': {
            'tokens_used': 45000,
            'estimated_cost': 0.09,
            'cache_hits': 230
        }
    }
    
    if bot_instance and hasattr(bot_instance, 'grok_client'):
        ai_metrics = bot_instance.grok_client.get_metrics()
        metrics['ai_usage'].update(ai_metrics)
    
    return jsonify(metrics)


@app.route('/api/blacklist', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_blacklist():
    """Manage blacklisted keywords and users"""
    if request.method == 'GET':
        return jsonify({
            'keywords': config.get('safety', {}).get('blacklist', {}).get('keywords', []),
            'users': config.get('safety', {}).get('blacklist', {}).get('users', [])
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        item_type = data.get('type')  # 'keyword' or 'user'
        value = data.get('value')
        
        if not item_type or not value:
            return jsonify({'error': 'Type and value required'}), 400
        
        if item_type == 'keyword':
            config['safety']['blacklist']['keywords'].append(value)
        elif item_type == 'user':
            config['safety']['blacklist']['users'].append(value)
        else:
            return jsonify({'error': 'Invalid type'}), 400
        
        # Save config
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return jsonify({'success': True, 'message': f'{item_type} blacklisted'})


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        join_room('control')
        emit('connected', {'message': 'Connected to control room'})
        logger.info(f"User {current_user.username} connected to WebSocket")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        leave_room('control')
        logger.info(f"User {current_user.username} disconnected from WebSocket")


@socketio.on('request_status')
def handle_status_request():
    """Handle real-time status request"""
    global bot_instance
    
    if bot_instance:
        stats = bot_instance.get_stats()
        emit('bot_status', {
            'status': bot_instance.status.value,
            'stats': stats
        })
    else:
        emit('bot_status', {
            'status': 'stopped',
            'stats': {}
        })


@socketio.on('send_command')
@login_required
def handle_command(data):
    """Handle bot commands via WebSocket"""
    command = data.get('command')
    
    if command == 'screenshot':
        # Take screenshot if bot is running
        if bot_instance and bot_instance.browser_manager:
            asyncio.create_task(bot_instance.browser_manager.take_screenshot())
            emit('command_result', {'success': True, 'message': 'Screenshot taken'})
        else:
            emit('command_result', {'success': False, 'error': 'Bot not running'})


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal error: {error}")
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


# Initialize default admin user
def init_admin_user():
    """Create default admin user if none exists"""
    if not users_db:
        admin_id = 'admin'
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        admin_hash = generate_password_hash(admin_password)
        admin_user = DashboardUser(admin_id, 'admin', admin_hash)
        users_db[admin_id] = admin_user
        logger.info("Default admin user created")


if __name__ == '__main__':
    # Initialize admin user
    init_admin_user()
    
    # Run Flask app with SocketIO
    port = int(os.getenv('PORT', 5000))
    debug = config.get('app', {}).get('debug', False)
    
    logger.info(f"Starting Flask dashboard on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)