"""
Anti-Detection Module - Advanced bot detection avoidance
Implements sophisticated techniques to avoid detection by dating platforms
"""

import random
import time
import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from loguru import logger
import pyautogui
from fake_useragent import UserAgent


class AntiDetection:
    """
    Advanced anti-detection system with multiple evasion techniques
    Implements human-like behavior patterns and fingerprint randomization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize anti-detection system
        
        Args:
            config: Anti-detection configuration
        """
        self.config = config
        self.user_agent = UserAgent()
        
        # Human behavior parameters
        self.typing_speed_wpm = random.randint(30, 60)  # Words per minute
        self.mouse_speed = random.uniform(0.5, 1.5)
        self.scroll_patterns = []
        self.click_patterns = []
        
        # Detection tracking
        self.detection_scores = []
        self.last_actions = []
        self.session_fingerprint = self._generate_session_fingerprint()
        
        # Initialize behavior patterns
        self._init_human_patterns()
        
    def _init_human_patterns(self):
        """Initialize realistic human behavior patterns"""
        # Typing patterns (inter-keystroke delays in ms)
        self.typing_patterns = {
            'fast': {'mean': 80, 'std': 20},
            'normal': {'mean': 120, 'std': 30},
            'slow': {'mean': 200, 'std': 50},
            'thinking': {'mean': 500, 'std': 200}
        }
        
        # Mouse movement patterns
        self.mouse_patterns = {
            'direct': {'curve': 0.1, 'overshoots': 0},
            'natural': {'curve': 0.3, 'overshoots': 1},
            'hesitant': {'curve': 0.5, 'overshoots': 2}
        }
        
        # Reading patterns (time spent on content)
        self.reading_speeds = {
            'skimming': 200,  # words per minute
            'normal': 250,
            'careful': 180
        }
        
    async def apply_stealth_measures(self, driver):
        """
        Apply comprehensive stealth measures to browser
        
        Args:
            driver: Selenium WebDriver instance
        """
        try:
            logger.info("Applying advanced stealth measures...")
            
            # Override navigator properties
            await self._override_navigator_properties(driver)
            
            # Randomize browser fingerprint
            await self._randomize_fingerprint(driver)
            
            # Add human-like browser history
            await self._inject_browser_history(driver)
            
            # Set realistic browser dimensions
            await self._set_realistic_dimensions(driver)
            
            # Inject anti-detection JavaScript
            await self._inject_stealth_javascript(driver)
            
            logger.success("Stealth measures applied successfully")
            
        except Exception as e:
            logger.error(f"Failed to apply stealth measures: {e}")
            raise
    
    async def _override_navigator_properties(self, driver):
        """Override navigator properties to hide automation"""
        scripts = [
            # Hide webdriver
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """,
            
            # Set realistic plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [
                        {
                            name: 'Chrome PDF Plugin',
                            filename: 'internal-pdf-viewer',
                            description: 'Portable Document Format'
                        },
                        {
                            name: 'Chrome PDF Viewer',
                            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                            description: 'PDF Viewer'
                        },
                        {
                            name: 'Native Client',
                            filename: 'internal-nacl-plugin',
                            description: 'Native Client Executable'
                        }
                    ];
                    return plugins;
                }
            });
            """,
            
            # Set realistic languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            """,
            
            # Override permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """,
            
            # Hide automation indicators
            """
            window.navigator.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            """,
            
            # Override WebGL vendor
            """
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, arguments);
            };
            """
        ]
        
        for script in scripts:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": script
            })
    
    async def _randomize_fingerprint(self, driver):
        """Randomize browser fingerprint to avoid tracking"""
        # Random screen resolution
        resolutions = [
            (1920, 1080), (1366, 768), (1440, 900),
            (1536, 864), (1680, 1050), (1280, 720)
        ]
        width, height = random.choice(resolutions)
        
        driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": random.choice([1, 1.5, 2]),
            "mobile": False
        })
        
        # Random timezone
        timezones = [
            "America/New_York", "America/Chicago", "America/Los_Angeles",
            "America/Denver", "America/Phoenix", "America/Detroit"
        ]
        driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {
            "timezoneId": random.choice(timezones)
        })
        
        # Random locale
        locales = ["en-US", "en-GB", "en-CA"]
        driver.execute_cdp_cmd("Emulation.setLocaleOverride", {
            "locale": random.choice(locales)
        })
    
    async def _inject_browser_history(self, driver):
        """Inject realistic browser history"""
        # Add common referrers
        referrers = [
            "https://www.google.com/",
            "https://www.facebook.com/",
            "https://www.instagram.com/",
            "https://www.reddit.com/"
        ]
        
        script = f"""
        Object.defineProperty(document, 'referrer', {{
            get: () => '{random.choice(referrers)}'
        }});
        """
        driver.execute_script(script)
    
    async def _set_realistic_dimensions(self, driver):
        """Set realistic browser window dimensions"""
        # Common desktop resolutions
        dimensions = [
            (1920, 1080), (1366, 768), (1440, 900),
            (1536, 864), (1680, 1050)
        ]
        
        width, height = random.choice(dimensions)
        
        # Add some randomness to avoid exact matches
        width += random.randint(-50, 50)
        height += random.randint(-50, 50)
        
        driver.set_window_size(width, height)
        
        # Random position
        x = random.randint(0, 200)
        y = random.randint(0, 100)
        driver.set_window_position(x, y)
    
    async def _inject_stealth_javascript(self, driver):
        """Inject additional stealth JavaScript"""
        script = """
        // Override toString methods
        window.navigator.toString = function() { return '[object Navigator]' };
        window.navigator.webdriver = undefined;
        
        // Add battery API
        navigator.getBattery = function() {
            return Promise.resolve({
                charging: true,
                chargingTime: 0,
                dischargingTime: Infinity,
                level: 0.98
            });
        };
        
        // Add media devices
        if (!navigator.mediaDevices) {
            navigator.mediaDevices = {};
        }
        
        // Override console.debug to hide logs
        const originalDebug = console.debug;
        console.debug = function() {
            if (![...arguments].some(arg => 
                typeof arg === 'string' && arg.includes('webdriver'))) {
                originalDebug.apply(console, arguments);
            }
        };
        """
        driver.execute_script(script)
    
    async def human_type(self, element, text: str, thinking_pauses: bool = True):
        """
        Type text with human-like patterns
        
        Args:
            element: Selenium WebElement
            text: Text to type
            thinking_pauses: Add thinking pauses between words
        """
        element.clear()
        
        for i, char in enumerate(text):
            element.send_keys(char)
            
            # Variable typing speed
            if char == ' ' and thinking_pauses and random.random() < 0.1:
                # Thinking pause
                delay = np.random.normal(
                    self.typing_patterns['thinking']['mean'],
                    self.typing_patterns['thinking']['std']
                ) / 1000
            else:
                # Normal typing
                pattern = random.choice(['fast', 'normal', 'slow'])
                delay = np.random.normal(
                    self.typing_patterns[pattern]['mean'],
                    self.typing_patterns[pattern]['std']
                ) / 1000
            
            # Ensure positive delay
            delay = max(0.01, delay)
            await asyncio.sleep(delay)
            
            # Occasional typos and corrections
            if random.random() < 0.02 and i < len(text) - 1:
                # Make a typo
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                element.send_keys(Keys.BACKSPACE)
                await asyncio.sleep(random.uniform(0.05, 0.15))
    
    async def human_click(self, driver, element):
        """
        Click element with human-like behavior
        
        Args:
            driver: Selenium WebDriver
            element: Element to click
        """
        # Move to element with curve
        await self._human_mouse_move(driver, element)
        
        # Small pause before click
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Click with slight offset
        action = ActionChains(driver)
        
        # Get element dimensions
        size = element.size
        
        # Click with small random offset from center
        x_offset = random.randint(-size['width']//4, size['width']//4)
        y_offset = random.randint(-size['height']//4, size['height']//4)
        
        action.move_to_element_with_offset(element, x_offset, y_offset)
        action.click()
        action.perform()
        
        # Record action
        self.last_actions.append({
            'type': 'click',
            'timestamp': datetime.now(),
            'element': element.tag_name
        })
    
    async def _human_mouse_move(self, driver, element):
        """Move mouse to element with human-like curve"""
        action = ActionChains(driver)
        
        # Get current position (approximate)
        current_element = driver.switch_to.active_element
        
        # Move with bezier curve simulation
        pattern = random.choice(['direct', 'natural', 'hesitant'])
        params = self.mouse_patterns[pattern]
        
        # Add overshoots
        for _ in range(params['overshoots']):
            # Overshoot past target
            overshoot_x = random.randint(10, 30)
            overshoot_y = random.randint(10, 30)
            action.move_to_element_with_offset(
                element, overshoot_x, overshoot_y
            )
            action.pause(random.uniform(0.05, 0.15))
        
        # Move to actual target
        action.move_to_element(element)
        action.perform()
    
    async def random_mouse_movement(self, driver):
        """Perform random mouse movements to appear human"""
        try:
            # Get viewport dimensions
            width = driver.execute_script("return window.innerWidth")
            height = driver.execute_script("return window.innerHeight")
            
            # Random movements
            movements = random.randint(2, 5)
            
            for _ in range(movements):
                x = random.randint(100, width - 100)
                y = random.randint(100, height - 100)
                
                # Use pyautogui for more realistic movements
                if self.config.get('use_pyautogui', False):
                    pyautogui.moveTo(x, y, duration=random.uniform(0.5, 1.5))
                else:
                    # Fallback to ActionChains
                    action = ActionChains(driver)
                    action.move_by_offset(x, y)
                    action.perform()
                
                await asyncio.sleep(random.uniform(0.5, 2))
                
        except Exception as e:
            logger.warning(f"Random mouse movement failed: {e}")
    
    async def random_scrolling(self, driver):
        """Perform human-like scrolling patterns"""
        scroll_patterns = [
            # Slow reading scroll
            lambda: driver.execute_script("window.scrollBy(0, 100)"),
            # Quick scan
            lambda: driver.execute_script("window.scrollBy(0, 500)"),
            # Page down
            lambda: driver.execute_script("window.scrollBy(0, window.innerHeight * 0.8)"),
            # Small adjustment
            lambda: driver.execute_script("window.scrollBy(0, 50)"),
            # Scroll up a bit
            lambda: driver.execute_script("window.scrollBy(0, -200)")
        ]
        
        # Perform 2-4 scrolls
        for _ in range(random.randint(2, 4)):
            pattern = random.choice(scroll_patterns)
            pattern()
            await asyncio.sleep(random.uniform(0.5, 2))
    
    async def human_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """
        Add human-like delay between actions
        
        Args:
            min_seconds: Minimum delay
            max_seconds: Maximum delay
        """
        # Use beta distribution for more realistic delays
        # Most delays cluster around the middle with occasional outliers
        delay = np.random.beta(2, 2) * (max_seconds - min_seconds) + min_seconds
        await asyncio.sleep(delay)
    
    async def simulate_reading(self, driver, text_length: int):
        """
        Simulate reading time based on text length
        
        Args:
            driver: Selenium WebDriver
            text_length: Number of characters to "read"
        """
        # Estimate words (average 5 chars per word)
        words = text_length / 5
        
        # Select reading speed
        speed = random.choice(['skimming', 'normal', 'careful'])
        wpm = self.reading_speeds[speed]
        
        # Calculate reading time with some variance
        reading_time = (words / wpm) * 60  # Convert to seconds
        reading_time *= random.uniform(0.8, 1.2)  # Add variance
        
        # Perform scrolling while reading
        scroll_times = int(reading_time / 3)
        for _ in range(max(1, scroll_times)):
            await asyncio.sleep(reading_time / max(1, scroll_times))
            if random.random() < 0.7:
                await self.random_scrolling(driver)
    
    def assess_detection_risk(self) -> Dict[str, Any]:
        """
        Assess current detection risk based on recent actions
        
        Returns:
            Risk assessment with score and recommendations
        """
        risk_score = 0
        factors = []
        
        # Check action frequency
        recent_actions = [
            a for a in self.last_actions
            if (datetime.now() - a['timestamp']).seconds < 60
        ]
        
        if len(recent_actions) > 30:
            risk_score += 30
            factors.append("High action frequency")
        
        # Check for patterns
        if len(set(a['type'] for a in recent_actions)) < 3:
            risk_score += 20
            factors.append("Repetitive action patterns")
        
        # Check timing regularity
        if len(recent_actions) > 2:
            intervals = []
            for i in range(1, len(recent_actions)):
                interval = (recent_actions[i]['timestamp'] - 
                          recent_actions[i-1]['timestamp']).seconds
                intervals.append(interval)
            
            if intervals and np.std(intervals) < 1:
                risk_score += 25
                factors.append("Too regular timing")
        
        # Determine risk level
        if risk_score < 30:
            risk_level = "LOW"
        elif risk_score < 60:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return {
            'score': risk_score,
            'level': risk_level,
            'factors': factors,
            'recommendation': self._get_risk_recommendation(risk_level)
        }
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            'LOW': "Continue normal operation",
            'MEDIUM': "Increase delays and add more variation",
            'HIGH': "Pause operations and rotate session"
        }
        return recommendations.get(risk_level, "Monitor closely")
    
    def _generate_session_fingerprint(self) -> str:
        """Generate unique session fingerprint"""
        data = f"{datetime.now().isoformat()}_{random.random()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    async def evade_detection_check(self, driver) -> bool:
        """
        Check if we're likely being detected
        
        Args:
            driver: Selenium WebDriver
            
        Returns:
            True if detection likely, False otherwise
        """
        detection_indicators = []
        
        # Check for common detection elements
        detection_selectors = [
            "div[class*='captcha']",
            "div[class*='challenge']",
            "div[id*='recaptcha']",
            "div[class*='bot-detection']",
            "div[class*='security-check']",
            "iframe[src*='captcha']",
            "div[class*='rate-limit']"
        ]
        
        for selector in detection_selectors:
            try:
                elements = driver.find_elements_by_css_selector(selector)
                if elements:
                    detection_indicators.append(f"Found {selector}")
            except:
                pass
        
        # Check for unusual redirects
        current_url = driver.current_url
        if any(term in current_url.lower() for term in 
               ['captcha', 'challenge', 'verify', 'blocked', 'denied']):
            detection_indicators.append(f"Suspicious URL: {current_url}")
        
        # Check page title
        title = driver.title.lower()
        if any(term in title for term in 
               ['blocked', 'denied', 'security', 'verification']):
            detection_indicators.append(f"Suspicious title: {title}")
        
        if detection_indicators:
            logger.warning(f"Detection indicators found: {detection_indicators}")
            return True
        
        return False
    
    async def handle_detection(self, driver):
        """
        Handle detection scenario
        
        Args:
            driver: Selenium WebDriver
        """
        logger.warning("Detection likely - initiating evasion protocol")
        
        # Pause all actions
        await asyncio.sleep(random.uniform(10, 30))
        
        # Clear cookies if necessary
        if self.config.get('clear_cookies_on_detection', False):
            driver.delete_all_cookies()
            logger.info("Cookies cleared")
        
        # Attempt to refresh with new fingerprint
        await self._randomize_fingerprint(driver)
        
        # Navigate away and back
        driver.get("https://www.google.com")
        await asyncio.sleep(random.uniform(5, 10))
        
        logger.info("Evasion protocol completed")