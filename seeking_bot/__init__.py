"""
Seeking Chat Automation Bot - Production Ready
A comprehensive chat automation system with AI integration, anti-detection, and ethical safeguards.
"""

__version__ = "2.0.0"
__author__ = "SeekingBot Team"

from .core.bot_engine import SeekingBot
from .core.browser_manager import BrowserManager
from .ai.grok_client import GrokClient
from .utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

__all__ = [
    'SeekingBot',
    'BrowserManager', 
    'GrokClient',
    'logger'
]