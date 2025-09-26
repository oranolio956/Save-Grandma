"""
Browser Manager - Handles Selenium WebDriver with anti-detection measures
Implements undetected-chromedriver and various stealth techniques
"""

import os
import random
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger


class BrowserManager:
    """
    Manages browser instances with anti-detection features
    Uses undetected-chromedriver to bypass bot detection
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize browser manager
        
        Args:
            config: Browser configuration dictionary
        """
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.user_agent = UserAgent()
        self.proxy_list: List[str] = []
        self.current_proxy: Optional[str] = None
        
    async def create_driver(self) -> webdriver.Chrome:
        """
        Create a new browser instance with anti-detection measures
        
        Returns:
            Configured Chrome WebDriver instance
        """
        try:
            logger.info("Creating browser instance with anti-detection...")
            
            # Use undetected-chromedriver for better stealth
            options = uc.ChromeOptions()
            
            # Basic anti-detection options
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Disable webdriver flag
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-site-isolation-trials")
            
            # Set window size
            if self.config.get('window_size'):
                width, height = self.config['window_size']
                options.add_argument(f"--window-size={width},{height}")
            
            # Headless mode (if configured)
            if self.config.get('headless'):
                options.add_argument("--headless=new")  # New headless mode
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
            
            # User agent rotation
            if self.config.get('user_agent_rotation'):
                user_agent = self._get_random_user_agent()
                options.add_argument(f"user-agent={user_agent}")
            
            # Proxy configuration
            if self.config.get('use_proxies') and self.proxy_list:
                proxy = self._get_random_proxy()
                if proxy:
                    options.add_argument(f'--proxy-server={proxy}')
                    self.current_proxy = proxy
            
            # Additional stealth options
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "excludeSwitches": ["enable-automation"],
                "useAutomationExtension": False,
                # Disable images for faster loading (optional)
                # "profile.managed_default_content_settings.images": 2
            }
            options.add_experimental_option("prefs", prefs)
            
            # Chrome capabilities
            capabilities = DesiredCapabilities.CHROME
            capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
            
            # Create driver with undetected-chromedriver
            self.driver = uc.Chrome(
                options=options,
                desired_capabilities=capabilities,
                version_main=None,  # Auto-detect Chrome version
                use_subprocess=True  # Better process isolation
            )
            
            # Apply additional stealth JavaScript
            await self._apply_stealth_javascript()
            
            # Set proper viewport
            self.driver.set_window_size(width or 1920, height or 1080)
            
            # Randomize window position
            x = random.randint(0, 500)
            y = random.randint(0, 300)
            self.driver.set_window_position(x, y)
            
            logger.success("Browser instance created successfully")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to create browser: {e}")
            raise
    
    async def _apply_stealth_javascript(self):
        """Apply JavaScript patches to avoid detection"""
        try:
            # Override navigator.webdriver flag
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            
            # Override navigator.plugins to appear non-headless
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [
                            {
                                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf"},
                                description: "Portable Document Format",
                                filename: "internal-pdf-viewer",
                                length: 1,
                                name: "Chrome PDF Plugin"
                            }
                        ]
                    });
                """
            })
            
            # Override navigator.languages
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                """
            })
            
            # Override WebGL vendor and renderer
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) {
                            return 'Intel Inc.';
                        }
                        if (parameter === 37446) {
                            return 'Intel Iris OpenGL Engine';
                        }
                        return getParameter(parameter);
                    };
                """
            })
            
            # Override permissions API
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """
            })
            
            # Spoof timezone
            self.driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {
                "timezoneId": "America/New_York"
            })
            
            # Set realistic screen resolution
            self.driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            
            logger.debug("Stealth JavaScript applied successfully")
            
        except Exception as e:
            logger.warning(f"Some stealth JavaScript failed to apply: {e}")
    
    def _get_random_user_agent(self) -> str:
        """
        Get a random realistic user agent
        
        Returns:
            User agent string
        """
        # Prefer Chrome user agents for consistency
        chrome_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        
        # Use fake_useragent as fallback
        try:
            return self.user_agent.chrome
        except:
            return random.choice(chrome_agents)
    
    def _get_random_proxy(self) -> Optional[str]:
        """
        Get a random proxy from the proxy list
        
        Returns:
            Proxy string or None
        """
        if not self.proxy_list:
            self._load_proxies()
        
        if self.proxy_list:
            return random.choice(self.proxy_list)
        
        return None
    
    def _load_proxies(self):
        """Load proxy list from file or API"""
        proxy_file = Path("proxies.txt")
        
        if proxy_file.exists():
            with open(proxy_file, 'r') as f:
                self.proxy_list = [line.strip() for line in f if line.strip()]
                logger.info(f"Loaded {len(self.proxy_list)} proxies")
        else:
            logger.warning("No proxy file found, running without proxies")
    
    async def rotate_proxy(self):
        """Rotate to a new proxy"""
        if not self.proxy_list:
            return
        
        old_proxy = self.current_proxy
        new_proxy = self._get_random_proxy()
        
        if new_proxy and new_proxy != old_proxy:
            logger.info(f"Rotating proxy from {old_proxy} to {new_proxy}")
            
            # Need to restart browser with new proxy
            await self.close()
            await self.create_driver()
    
    async def take_screenshot(self, filename: str = None) -> str:
        """
        Take a screenshot of current page
        
        Args:
            filename: Optional filename for screenshot
            
        Returns:
            Path to screenshot file
        """
        if not self.driver:
            raise RuntimeError("No active browser instance")
        
        if not filename:
            filename = f"screenshot_{random.randint(1000, 9999)}.png"
        
        filepath = Path("screenshots") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        self.driver.save_screenshot(str(filepath))
        logger.debug(f"Screenshot saved to {filepath}")
        
        return str(filepath)
    
    async def execute_javascript(self, script: str) -> Any:
        """
        Execute JavaScript in the browser
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Script execution result
        """
        if not self.driver:
            raise RuntimeError("No active browser instance")
        
        return self.driver.execute_script(script)
    
    async def get_cookies(self) -> List[Dict]:
        """Get all cookies from current session"""
        if not self.driver:
            return []
        
        return self.driver.get_cookies()
    
    async def save_cookies(self, filepath: str = "cookies.json"):
        """Save cookies to file"""
        cookies = await self.get_cookies()
        
        with open(filepath, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        logger.debug(f"Cookies saved to {filepath}")
    
    async def load_cookies(self, filepath: str = "cookies.json"):
        """Load cookies from file"""
        if not Path(filepath).exists():
            logger.warning(f"Cookie file {filepath} not found")
            return
        
        with open(filepath, 'r') as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                logger.warning(f"Failed to add cookie: {e}")
        
        logger.debug(f"Loaded {len(cookies)} cookies")
    
    async def close(self):
        """Close browser and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                logger.debug("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            finally:
                self.driver = None
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass