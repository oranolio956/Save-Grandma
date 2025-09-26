"""
Core Bot Engine - Main orchestrator for the chat automation system
Handles browser automation, message processing, and response generation
"""

import asyncio
import time
import random
import threading
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger

from ..browser_manager import BrowserManager
from ..ai.grok_client import GrokClient
from ..ai.context_manager import ContextManager
from ..utils.anti_detection import AntiDetection
from ..utils.rate_limiter import RateLimiter
from ..database.models import Conversation, Message, User
from ..database.session_manager import SessionManager
from ..utils.encryption import EncryptionManager


class BotStatus(Enum):
    """Bot operational states"""
    IDLE = "idle"
    ACTIVE = "active"
    PROCESSING = "processing"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class ChatSession:
    """Represents an active chat session"""
    chat_id: str
    user_name: str
    messages: List[Dict] = field(default_factory=list)
    context: Dict = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)
    response_count: int = 0
    ai_context_id: Optional[str] = None
    is_active: bool = True
    disclosed_bot: bool = False


class SeekingBot:
    """
    Main bot engine that orchestrates all automation activities
    Implements production-ready features including error handling, rate limiting, and monitoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the bot with configuration
        
        Args:
            config: Configuration dictionary from config.yaml
        """
        self.config = config
        self.status = BotStatus.IDLE
        self.browser_manager = None
        self.grok_client = None
        self.context_manager = None
        self.anti_detection = None
        self.rate_limiter = None
        self.encryption_manager = None
        self.db_session = None
        
        # Active sessions tracking
        self.active_sessions: Dict[str, ChatSession] = {}
        self.session_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'messages_read': 0,
            'messages_sent': 0,
            'active_chats': 0,
            'errors': 0,
            'start_time': None,
            'total_runtime': 0
        }
        
        # Control flags
        self.should_stop = False
        self.is_paused = False
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all bot components"""
        try:
            logger.info("Initializing bot components...")
            
            # Browser automation
            self.browser_manager = BrowserManager(self.config['browser'])
            
            # AI client
            self.grok_client = GrokClient(
                api_key=self.config['ai']['api_key'],
                model=self.config['ai']['model']
            )
            
            # Context management
            self.context_manager = ContextManager(
                strategy=self.config['response_strategy']['context_management']['strategy'],
                window_size=self.config['response_strategy']['context_management']['window_size']
            )
            
            # Anti-detection measures
            self.anti_detection = AntiDetection(self.config['anti_detection'])
            
            # Rate limiting
            self.rate_limiter = RateLimiter(
                messages_per_hour=self.config['rate_limiting']['messages_per_hour'],
                messages_per_day=self.config['rate_limiting']['messages_per_day']
            )
            
            # Security
            self.encryption_manager = EncryptionManager(
                key=self.config['security']['encryption_key']
            )
            
            # Database
            self.db_session = SessionManager(self.config['database']['url'])
            
            logger.success("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            self.status = BotStatus.ERROR
            raise
    
    async def start(self, username: str, password: str) -> bool:
        """
        Start the bot and login to Seeking.com
        
        Args:
            username: Seeking.com username
            password: Seeking.com password (will be encrypted)
            
        Returns:
            Success status
        """
        try:
            logger.info("Starting Seeking Bot...")
            self.status = BotStatus.ACTIVE
            self.stats['start_time'] = datetime.now()
            
            # Encrypt credentials
            encrypted_password = self.encryption_manager.encrypt(password)
            
            # Initialize browser
            driver = await self.browser_manager.create_driver()
            
            # Apply anti-detection measures
            await self.anti_detection.apply_stealth_measures(driver)
            
            # Login to Seeking.com
            login_success = await self._login(driver, username, password)
            if not login_success:
                logger.error("Failed to login to Seeking.com")
                return False
            
            # Start monitoring for messages
            asyncio.create_task(self._monitor_messages())
            
            # Start periodic tasks
            asyncio.create_task(self._periodic_cleanup())
            asyncio.create_task(self._health_check())
            
            logger.success("Bot started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            self.status = BotStatus.ERROR
            return False
    
    async def _login(self, driver, username: str, password: str) -> bool:
        """
        Login to Seeking.com with anti-detection measures
        
        Args:
            driver: Selenium WebDriver instance
            username: Account username
            password: Account password
            
        Returns:
            Login success status
        """
        try:
            logger.info("Attempting to login to Seeking.com...")
            
            # Navigate to login page
            driver.get("https://www.seeking.com/login")
            
            # Random delay to appear human
            await self.anti_detection.human_delay(2, 4)
            
            # Find and fill username field with typing simulation
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            await self.anti_detection.human_type(username_field, username)
            
            # Random delay between fields
            await self.anti_detection.human_delay(1, 2)
            
            # Find and fill password field
            password_field = driver.find_element(By.ID, "password")
            await self.anti_detection.human_type(password_field, password)
            
            # Random mouse movement
            await self.anti_detection.random_mouse_movement(driver)
            
            # Click login button
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            await self.anti_detection.human_click(driver, login_button)
            
            # Wait for login to complete
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
            )
            
            logger.success("Successfully logged in to Seeking.com")
            return True
            
        except TimeoutException:
            logger.error("Login timeout - check credentials or site structure")
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def _monitor_messages(self):
        """
        Main loop to monitor for new messages
        Implements smart polling with exponential backoff
        """
        logger.info("Starting message monitoring...")
        consecutive_errors = 0
        
        while not self.should_stop:
            try:
                if self.is_paused:
                    await asyncio.sleep(1)
                    continue
                
                # Check for new messages
                new_messages = await self._check_for_new_messages()
                
                if new_messages:
                    logger.info(f"Found {len(new_messages)} new messages")
                    
                    # Process messages in parallel with rate limiting
                    tasks = []
                    for msg in new_messages:
                        if self.rate_limiter.can_send_message():
                            task = asyncio.create_task(self._process_message(msg))
                            tasks.append(task)
                        else:
                            logger.warning("Rate limit reached, queuing message")
                            await self._queue_message(msg)
                    
                    # Wait for all messages to be processed
                    if tasks:
                        await asyncio.gather(*tasks)
                
                # Reset error counter on success
                consecutive_errors = 0
                
                # Smart delay based on activity
                delay = self._calculate_polling_delay()
                await asyncio.sleep(delay)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in message monitoring: {e}")
                
                # Exponential backoff on errors
                backoff_delay = min(60, 2 ** consecutive_errors)
                await asyncio.sleep(backoff_delay)
                
                # Stop after too many errors
                if consecutive_errors > 5:
                    logger.critical("Too many consecutive errors, stopping bot")
                    await self.stop()
    
    async def _check_for_new_messages(self) -> List[Dict]:
        """
        Check for new unread messages on Seeking.com
        
        Returns:
            List of new message dictionaries
        """
        try:
            driver = self.browser_manager.driver
            new_messages = []
            
            # Navigate to messages if not already there
            current_url = driver.current_url
            if "messages" not in current_url:
                driver.get("https://www.seeking.com/messages")
                await self.anti_detection.human_delay(2, 3)
            
            # Find unread message indicators (these selectors need reconnaissance)
            unread_selectors = [
                "div[data-unread='true']",
                ".conversation-item.unread",
                ".message-preview.new",
                "[class*='unread']"
            ]
            
            for selector in unread_selectors:
                try:
                    unread_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if unread_elements:
                        logger.debug(f"Found {len(unread_elements)} unread with selector: {selector}")
                        
                        for element in unread_elements[:self.config['rate_limiting']['messages_per_hour']]:
                            # Extract message data
                            message_data = await self._extract_message_data(element)
                            if message_data:
                                new_messages.append(message_data)
                        break
                        
                except NoSuchElementException:
                    continue
            
            return new_messages
            
        except Exception as e:
            logger.error(f"Error checking for new messages: {e}")
            return []
    
    async def _extract_message_data(self, element) -> Optional[Dict]:
        """
        Extract message data from a DOM element
        
        Args:
            element: Selenium WebElement
            
        Returns:
            Message data dictionary
        """
        try:
            # Extract relevant data (selectors need adjustment based on reconnaissance)
            message_data = {
                'chat_id': element.get_attribute('data-chat-id') or self._generate_chat_id(element),
                'sender_name': element.find_element(By.CLASS_NAME, 'sender-name').text,
                'message_text': element.find_element(By.CLASS_NAME, 'message-preview').text,
                'timestamp': datetime.now(),
                'element': element
            }
            
            # Get sender profile data if available
            try:
                profile_link = element.find_element(By.CSS_SELECTOR, 'a[href*="/profile/"]')
                message_data['profile_url'] = profile_link.get_attribute('href')
            except:
                pass
            
            return message_data
            
        except Exception as e:
            logger.error(f"Failed to extract message data: {e}")
            return None
    
    async def _process_message(self, message_data: Dict):
        """
        Process a single message and generate/send response
        
        Args:
            message_data: Dictionary containing message information
        """
        try:
            chat_id = message_data['chat_id']
            
            # Create or update chat session
            with self.session_lock:
                if chat_id not in self.active_sessions:
                    self.active_sessions[chat_id] = ChatSession(
                        chat_id=chat_id,
                        user_name=message_data['sender_name']
                    )
                
                session = self.active_sessions[chat_id]
                session.messages.append({
                    'type': 'received',
                    'text': message_data['message_text'],
                    'timestamp': message_data['timestamp']
                })
            
            # Update statistics
            self.stats['messages_read'] += 1
            
            # Store in database
            await self._store_message(message_data, 'received')
            
            # Check for blacklisted keywords
            if self._is_blacklisted(message_data['message_text']):
                logger.warning(f"Message contains blacklisted content, skipping")
                return
            
            # Generate response
            response = await self._generate_response(session, message_data)
            
            if response:
                # Apply safety checks
                if self.config['safety']['bot_disclosure']['enabled'] and not session.disclosed_bot:
                    response = self._add_bot_disclosure(response)
                    session.disclosed_bot = True
                
                # Send response with human-like delay
                delay = random.uniform(
                    self.config['anti_detection']['random_delays']['min'],
                    self.config['anti_detection']['random_delays']['max']
                )
                await asyncio.sleep(delay)
                
                # Send the message
                success = await self._send_message(message_data['element'], response)
                
                if success:
                    # Update session
                    session.messages.append({
                        'type': 'sent',
                        'text': response,
                        'timestamp': datetime.now()
                    })
                    session.response_count += 1
                    
                    # Update statistics
                    self.stats['messages_sent'] += 1
                    
                    # Store in database
                    await self._store_message({'text': response, 'chat_id': chat_id}, 'sent')
                    
                    # Check auto-stop conditions
                    if self._should_auto_stop(session):
                        logger.info(f"Auto-stopping conversation with {session.user_name}")
                        session.is_active = False
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.stats['errors'] += 1
    
    async def _generate_response(self, session: ChatSession, message_data: Dict) -> Optional[str]:
        """
        Generate an intelligent response using AI and templates
        
        Args:
            session: Current chat session
            message_data: Incoming message data
            
        Returns:
            Generated response text
        """
        try:
            # Get conversation context
            context = self.context_manager.get_context(session)
            
            # Determine response strategy
            use_ai_probability = 1 - self.config['response_strategy']['template_weight']
            use_ai = random.random() < use_ai_probability
            
            if use_ai and self.grok_client:
                # Generate AI response with context
                prompt = self._build_ai_prompt(session, message_data, context)
                response = await self.grok_client.generate_response(
                    prompt=prompt,
                    temperature=self.config['ai']['temperature'],
                    max_tokens=self.config['ai']['max_tokens']
                )
                
                # Validate AI response
                if self._validate_ai_response(response):
                    return response
                else:
                    logger.warning("AI response failed validation, falling back to templates")
            
            # Fallback to template/keyword matching
            return self._get_template_response(message_data['message_text'])
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response()
    
    def _build_ai_prompt(self, session: ChatSession, message_data: Dict, context: Dict) -> str:
        """
        Build a context-aware prompt for AI response generation
        
        Args:
            session: Chat session
            message_data: Message data
            context: Conversation context
            
        Returns:
            Formatted prompt string
        """
        # Get recent conversation history
        recent_messages = session.messages[-5:] if len(session.messages) > 5 else session.messages
        
        conversation_history = "\n".join([
            f"{'User' if msg['type'] == 'received' else 'Assistant'}: {msg['text']}"
            for msg in recent_messages
        ])
        
        prompt = f"""You are having a friendly conversation on a dating platform. 
        
Previous conversation:
{conversation_history}

Current message from {session.user_name}: {message_data['message_text']}

Guidelines:
- Be friendly, engaging, and authentic
- Keep responses concise (under 50 words)
- Show interest in getting to know the person
- Avoid overly forward or inappropriate content
- If asked about meeting, suggest public places
- Don't share personal contact information immediately

Generate a natural, contextual response:"""
        
        return prompt
    
    def _validate_ai_response(self, response: str) -> bool:
        """
        Validate AI-generated response for safety and appropriateness
        
        Args:
            response: AI-generated response text
            
        Returns:
            Validation status
        """
        if not response or len(response) < 5:
            return False
        
        # Check for inappropriate content
        inappropriate_patterns = [
            'personal information',
            'phone number',
            'address',
            'credit card',
            'social security'
        ]
        
        response_lower = response.lower()
        for pattern in inappropriate_patterns:
            if pattern in response_lower:
                logger.warning(f"Response contains inappropriate content: {pattern}")
                return False
        
        # Check response length
        if len(response) > 500:
            logger.warning("Response too long")
            return False
        
        return True
    
    def _get_template_response(self, message: str) -> str:
        """
        Get response from templates and keyword matching
        
        Args:
            message: Incoming message text
            
        Returns:
            Template response
        """
        message_lower = message.lower()
        
        # Check keyword matches first
        keywords = self.config.get('keywords', {})
        for keyword, response in keywords.items():
            if keyword.lower() in message_lower:
                return self._add_variation(response)
        
        # Use random template
        templates = self.config.get('templates', [])
        if templates:
            return self._add_variation(random.choice(templates))
        
        # Final fallback
        return self._get_fallback_response()
    
    def _add_variation(self, text: str) -> str:
        """Add slight variations to avoid detection"""
        variations = [
            lambda s: s,
            lambda s: s + " 😊",
            lambda s: s + "!",
            lambda s: s.replace(".", "!"),
            lambda s: s[0].lower() + s[1:] if len(s) > 1 else s
        ]
        return random.choice(variations)(text)
    
    def _get_fallback_response(self) -> str:
        """Get a safe fallback response"""
        fallbacks = [
            "That's interesting! Tell me more.",
            "I'd love to hear more about that!",
            "Thanks for sharing! What else is on your mind?",
            "That sounds great! How long have you been interested in that?"
        ]
        return random.choice(fallbacks)
    
    async def _send_message(self, chat_element, message: str) -> bool:
        """
        Send a message in the chat with human-like behavior
        
        Args:
            chat_element: Chat DOM element
            message: Message text to send
            
        Returns:
            Success status
        """
        try:
            driver = self.browser_manager.driver
            
            # Click on chat to open it
            await self.anti_detection.human_click(driver, chat_element)
            await self.anti_detection.human_delay(1, 2)
            
            # Find message input field (selectors need reconnaissance)
            input_selectors = [
                "textarea[placeholder*='message']",
                "input[type='text'][placeholder*='Type']",
                ".message-input",
                "[contenteditable='true']"
            ]
            
            input_field = None
            for selector in input_selectors:
                try:
                    input_field = driver.find_element(By.CSS_SELECTOR, selector)
                    if input_field:
                        break
                except NoSuchElementException:
                    continue
            
            if not input_field:
                logger.error("Could not find message input field")
                return False
            
            # Type message with human-like simulation
            await self.anti_detection.human_type(input_field, message)
            
            # Random delay before sending
            await self.anti_detection.human_delay(0.5, 1.5)
            
            # Find and click send button
            send_selectors = [
                "button[type='submit']",
                "button[aria-label*='send']",
                ".send-button",
                "[data-testid='send-button']"
            ]
            
            for selector in send_selectors:
                try:
                    send_button = driver.find_element(By.CSS_SELECTOR, selector)
                    await self.anti_detection.human_click(driver, send_button)
                    logger.success(f"Message sent successfully")
                    return True
                except NoSuchElementException:
                    continue
            
            # Fallback: press Enter
            input_field.send_keys('\n')
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def _is_blacklisted(self, text: str) -> bool:
        """Check if message contains blacklisted content"""
        blacklist = self.config['safety']['blacklist']['keywords']
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in blacklist)
    
    def _should_auto_stop(self, session: ChatSession) -> bool:
        """Check if conversation should be auto-stopped"""
        config = self.config['safety']['auto_stop']
        
        # Check message count
        if session.response_count >= config['after_messages']:
            return True
        
        # Check time limit
        if config['after_hours']:
            time_diff = datetime.now() - session.messages[0]['timestamp']
            if time_diff.total_seconds() / 3600 >= config['after_hours']:
                return True
        
        return False
    
    def _add_bot_disclosure(self, message: str) -> str:
        """Add bot disclosure to message"""
        disclosure = self.config['safety']['bot_disclosure']['message']
        return f"{disclosure}\n\n{message}"
    
    def _calculate_polling_delay(self) -> float:
        """Calculate intelligent polling delay based on activity"""
        base_delay = self.config['rate_limiting']['cooldown_between_messages']
        
        # Adjust based on time of day
        current_hour = datetime.now().hour
        if 2 <= current_hour <= 8:  # Late night/early morning
            return base_delay * 2
        elif 18 <= current_hour <= 22:  # Peak evening hours
            return base_delay * 0.5
        
        return base_delay
    
    def _generate_chat_id(self, element) -> str:
        """Generate unique chat ID from element"""
        text = element.text or str(time.time())
        return hashlib.md5(text.encode()).hexdigest()[:16]
    
    async def _store_message(self, message_data: Dict, message_type: str):
        """Store message in database"""
        try:
            # Implementation depends on database models
            pass
        except Exception as e:
            logger.error(f"Failed to store message: {e}")
    
    async def _queue_message(self, message: Dict):
        """Queue message for later processing"""
        # Implementation for message queuing
        pass
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of old sessions and data"""
        while not self.should_stop:
            await asyncio.sleep(3600)  # Run every hour
            
            with self.session_lock:
                # Clean up inactive sessions
                cutoff_time = datetime.now() - timedelta(hours=24)
                to_remove = [
                    chat_id for chat_id, session in self.active_sessions.items()
                    if session.last_activity < cutoff_time
                ]
                
                for chat_id in to_remove:
                    del self.active_sessions[chat_id]
                    
                if to_remove:
                    logger.info(f"Cleaned up {len(to_remove)} inactive sessions")
    
    async def _health_check(self):
        """Periodic health check"""
        while not self.should_stop:
            await asyncio.sleep(60)  # Check every minute
            
            # Log statistics
            logger.info(f"Bot Stats - Read: {self.stats['messages_read']}, "
                       f"Sent: {self.stats['messages_sent']}, "
                       f"Active Chats: {len(self.active_sessions)}, "
                       f"Errors: {self.stats['errors']}")
    
    async def pause(self):
        """Pause bot operations"""
        logger.info("Pausing bot...")
        self.is_paused = True
        self.status = BotStatus.PAUSED
    
    async def resume(self):
        """Resume bot operations"""
        logger.info("Resuming bot...")
        self.is_paused = False
        self.status = BotStatus.ACTIVE
    
    async def stop(self):
        """Stop bot and cleanup resources"""
        logger.info("Stopping bot...")
        self.should_stop = True
        self.status = BotStatus.STOPPED
        
        # Calculate total runtime
        if self.stats['start_time']:
            self.stats['total_runtime'] = (datetime.now() - self.stats['start_time']).total_seconds()
        
        # Cleanup browser
        if self.browser_manager:
            await self.browser_manager.close()
        
        # Close database connections
        if self.db_session:
            self.db_session.close()
        
        logger.success("Bot stopped successfully")
    
    def get_stats(self) -> Dict:
        """Get current bot statistics"""
        return {
            **self.stats,
            'active_chats': len(self.active_sessions),
            'status': self.status.value
        }