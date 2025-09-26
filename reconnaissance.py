#!/usr/bin/env python3
"""
Reconnaissance Script - Discovers DOM selectors on Seeking.com
Run this script to automatically identify the correct selectors for chat elements
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from loguru import logger
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)


class SeekingReconnaissance:
    """
    Reconnaissance tool to discover DOM selectors on Seeking.com
    Helps identify the correct element selectors for automation
    """
    
    def __init__(self):
        self.driver = None
        self.selectors = {
            'login': {},
            'navigation': {},
            'chat': {},
            'messages': {},
            'profile': {},
            'misc': {}
        }
        self.findings = []
        
    def print_banner(self):
        """Print reconnaissance banner"""
        print(f"""
{Fore.CYAN}{'='*60}
{Fore.YELLOW}🔍 Seeking.com DOM Reconnaissance Tool
{Fore.GREEN}Discovering element selectors for automation...
{Fore.CYAN}{'='*60}
        """)
    
    async def setup_browser(self, headless: bool = False):
        """Setup browser for reconnaissance"""
        print(f"{Fore.YELLOW}[*] Setting up browser...")
        
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = uc.Chrome(options=options)
        self.driver.set_window_size(1920, 1080)
        
        print(f"{Fore.GREEN}[✓] Browser ready")
    
    async def login(self, username: str, password: str) -> bool:
        """
        Attempt login and discover login form selectors
        
        Args:
            username: Seeking.com username
            password: Seeking.com password
            
        Returns:
            Login success status
        """
        print(f"\n{Fore.YELLOW}[*] Navigating to Seeking.com...")
        self.driver.get("https://www.seeking.com")
        await asyncio.sleep(3)
        
        print(f"{Fore.YELLOW}[*] Discovering login selectors...")
        
        # Common login selector patterns to try
        login_patterns = {
            'username_field': [
                "input[type='email']",
                "input[name='email']",
                "input[id='email']",
                "input[placeholder*='email']",
                "#username",
                ".email-input"
            ],
            'password_field': [
                "input[type='password']",
                "input[name='password']",
                "input[id='password']",
                "#password",
                ".password-input"
            ],
            'login_button': [
                "button[type='submit']",
                "button.login-button",
                "input[type='submit']",
                "#login-button",
                ".btn-login",
                "button[contains(text(),'Log')]"
            ],
            'login_link': [
                "a[href*='login']",
                "a[contains(text(),'Log')]",
                ".login-link"
            ]
        }
        
        # Try to find login page
        for selector in login_patterns['login_link']:
            try:
                login_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                print(f"{Fore.GREEN}[✓] Found login link: {selector}")
                self.selectors['login']['login_link'] = selector
                login_link.click()
                await asyncio.sleep(2)
                break
            except NoSuchElementException:
                continue
        
        # Discover login form elements
        for field_name, patterns in login_patterns.items():
            if field_name == 'login_link':
                continue
                
            for selector in patterns:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"{Fore.GREEN}[✓] Found {field_name}: {selector}")
                    self.selectors['login'][field_name] = selector
                    
                    # Fill in credentials if found
                    if field_name == 'username_field' and username:
                        element.send_keys(username)
                    elif field_name == 'password_field' and password:
                        element.send_keys(password)
                    
                    break
                except NoSuchElementException:
                    continue
        
        # Try to login if we have all fields
        if all(k in self.selectors['login'] for k in ['username_field', 'password_field', 'login_button']):
            try:
                login_btn = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    self.selectors['login']['login_button']
                )
                login_btn.click()
                
                print(f"{Fore.YELLOW}[*] Attempting login...")
                await asyncio.sleep(5)
                
                # Check if login successful
                if "dashboard" in self.driver.current_url.lower() or "messages" in self.driver.current_url.lower():
                    print(f"{Fore.GREEN}[✓] Login successful!")
                    return True
                else:
                    print(f"{Fore.RED}[✗] Login may have failed")
                    return False
                    
            except Exception as e:
                print(f"{Fore.RED}[✗] Login error: {e}")
                return False
        
        return False
    
    async def discover_chat_selectors(self):
        """Discover chat and messaging selectors"""
        print(f"\n{Fore.YELLOW}[*] Discovering chat selectors...")
        
        # Navigate to messages section
        message_urls = [
            "https://www.seeking.com/messages",
            "https://www.seeking.com/inbox",
            "https://www.seeking.com/chat"
        ]
        
        for url in message_urls:
            try:
                self.driver.get(url)
                await asyncio.sleep(3)
                if "messages" in self.driver.current_url.lower():
                    print(f"{Fore.GREEN}[✓] Found messages page: {url}")
                    break
            except:
                continue
        
        # Common chat selector patterns
        chat_patterns = {
            'chat_list': [
                ".chat-list",
                ".conversation-list",
                ".message-list",
                "#messages-list",
                "[data-testid='chat-list']",
                ".inbox-conversations",
                "div[class*='conversation']",
                "div[class*='chat']"
            ],
            'chat_item': [
                ".chat-item",
                ".conversation-item",
                ".message-thread",
                "[data-chat-id]",
                "[data-conversation-id]",
                "a[href*='conversation']",
                "div[class*='thread']"
            ],
            'unread_indicator': [
                ".unread",
                ".new-message",
                "[data-unread='true']",
                ".notification-badge",
                ".message-count",
                "span[class*='badge']",
                "div[class*='unread']"
            ],
            'message_input': [
                "textarea[placeholder*='message']",
                "textarea[placeholder*='type']",
                "input[type='text'][placeholder*='message']",
                ".message-input",
                "#message-input",
                "[contenteditable='true']",
                "div[role='textbox']"
            ],
            'send_button': [
                "button[type='submit']",
                "button[aria-label*='send']",
                ".send-button",
                "#send-button",
                "button.send",
                "[data-testid='send-button']",
                "button[class*='send']"
            ],
            'message_content': [
                ".message-text",
                ".message-content",
                ".msg-text",
                "[data-message-content]",
                ".chat-message",
                "div[class*='message-bubble']",
                "p[class*='message']"
            ]
        }
        
        # Discover each element type
        for element_type, patterns in chat_patterns.items():
            print(f"\n{Fore.CYAN}[*] Looking for {element_type}...")
            found = False
            
            for selector in patterns:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"{Fore.GREEN}[✓] Found {element_type}: {selector} ({len(elements)} elements)")
                        self.selectors['chat'][element_type] = selector
                        
                        # Get sample attributes
                        if len(elements) > 0:
                            sample = elements[0]
                            attrs = self._get_element_attributes(sample)
                            if attrs:
                                print(f"{Fore.BLUE}    Attributes: {attrs}")
                        
                        found = True
                        break
                        
                except NoSuchElementException:
                    continue
            
            if not found:
                print(f"{Fore.YELLOW}[!] Could not find {element_type}")
    
    async def discover_profile_selectors(self):
        """Discover profile-related selectors"""
        print(f"\n{Fore.YELLOW}[*] Discovering profile selectors...")
        
        profile_patterns = {
            'profile_link': [
                "a[href*='profile']",
                ".profile-link",
                "[data-testid='profile']"
            ],
            'username': [
                ".username",
                ".user-name",
                "[data-username]",
                "h1.name",
                "span.name"
            ],
            'avatar': [
                ".avatar",
                ".profile-pic",
                "img[alt*='profile']",
                ".user-avatar"
            ],
            'status': [
                ".online-status",
                ".user-status",
                "[data-status]"
            ]
        }
        
        for element_type, patterns in profile_patterns.items():
            for selector in patterns:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"{Fore.GREEN}[✓] Found {element_type}: {selector}")
                    self.selectors['profile'][element_type] = selector
                    break
                except NoSuchElementException:
                    continue
    
    async def analyze_javascript_framework(self):
        """Detect JavaScript framework used by the site"""
        print(f"\n{Fore.YELLOW}[*] Analyzing JavaScript framework...")
        
        # Check for common frameworks
        framework_checks = {
            'React': "window.React || document.querySelector('[data-reactroot]')",
            'Vue': "window.Vue || document.querySelector('#app').__vue__",
            'Angular': "window.angular || document.querySelector('[ng-app]')",
            'jQuery': "window.jQuery || window.$"
        }
        
        for framework, check in framework_checks.items():
            try:
                result = self.driver.execute_script(f"return Boolean({check})")
                if result:
                    print(f"{Fore.GREEN}[✓] Detected {framework}")
                    self.selectors['misc']['framework'] = framework
            except:
                pass
    
    async def test_selectors(self):
        """Test discovered selectors to verify they work"""
        print(f"\n{Fore.YELLOW}[*] Testing discovered selectors...")
        
        test_results = {}
        
        for category, selectors in self.selectors.items():
            if not selectors:
                continue
                
            print(f"\n{Fore.CYAN}Testing {category} selectors:")
            
            for name, selector in selectors.items():
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"{Fore.GREEN}  ✓ {name}: {len(elements)} elements found")
                        test_results[f"{category}.{name}"] = {
                            'selector': selector,
                            'count': len(elements),
                            'status': 'working'
                        }
                    else:
                        print(f"{Fore.YELLOW}  ! {name}: No elements found")
                        test_results[f"{category}.{name}"] = {
                            'selector': selector,
                            'count': 0,
                            'status': 'no_elements'
                        }
                except Exception as e:
                    print(f"{Fore.RED}  ✗ {name}: Error - {str(e)[:50]}")
                    test_results[f"{category}.{name}"] = {
                        'selector': selector,
                        'error': str(e),
                        'status': 'error'
                    }
        
        return test_results
    
    def _get_element_attributes(self, element) -> Dict:
        """Get relevant attributes from an element"""
        attrs = {}
        
        try:
            if element.get_attribute('id'):
                attrs['id'] = element.get_attribute('id')
            if element.get_attribute('class'):
                attrs['class'] = element.get_attribute('class')
            if element.get_attribute('data-testid'):
                attrs['data-testid'] = element.get_attribute('data-testid')
            if element.get_attribute('href'):
                attrs['href'] = element.get_attribute('href')[:50]
        except:
            pass
        
        return attrs
    
    async def save_results(self, filename: str = "selectors_discovered.json"):
        """Save discovered selectors to file"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'url': self.driver.current_url if self.driver else None,
            'selectors': self.selectors,
            'findings': self.findings
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n{Fore.GREEN}[✓] Results saved to {filename}")
    
    def print_summary(self):
        """Print summary of discovered selectors"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}📊 Discovery Summary")
        print(f"{Fore.CYAN}{'='*60}")
        
        total_selectors = sum(len(s) for s in self.selectors.values())
        
        for category, selectors in self.selectors.items():
            if selectors:
                print(f"\n{Fore.GREEN}{category.upper()}:")
                for name, selector in selectors.items():
                    print(f"  {name}: {Fore.WHITE}{selector}")
        
        print(f"\n{Fore.YELLOW}Total selectors discovered: {total_selectors}")
    
    async def cleanup(self):
        """Cleanup browser"""
        if self.driver:
            self.driver.quit()
            print(f"\n{Fore.GREEN}[✓] Browser closed")


async def main():
    """Main reconnaissance function"""
    recon = SeekingReconnaissance()
    
    try:
        # Print banner
        recon.print_banner()
        
        # Get credentials (optional)
        print(f"\n{Fore.YELLOW}Enter credentials to test login (or press Enter to skip):")
        username = input("Username/Email: ").strip()
        password = input("Password: ").strip()
        
        # Setup browser
        headless = input("\nRun in headless mode? (y/n): ").lower() == 'y'
        await recon.setup_browser(headless)
        
        # Attempt login if credentials provided
        if username and password:
            await recon.login(username, password)
        else:
            print(f"{Fore.YELLOW}[!] Skipping login - some selectors may not be discoverable")
        
        # Discover selectors
        await recon.discover_chat_selectors()
        await recon.discover_profile_selectors()
        await recon.analyze_javascript_framework()
        
        # Test selectors
        test_results = await recon.test_selectors()
        
        # Save results
        await recon.save_results()
        
        # Print summary
        recon.print_summary()
        
        # Generate config update
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}📝 Suggested Config Updates:")
        print(f"{Fore.CYAN}{'='*60}")
        
        if recon.selectors['chat']:
            print(f"\n{Fore.WHITE}# Add these to your bot configuration:")
            print("selectors:")
            for key, value in recon.selectors['chat'].items():
                print(f"  {key}: '{value}'")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Reconnaissance interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}[✗] Error: {e}")
        logger.exception("Reconnaissance error")
    finally:
        await recon.cleanup()


if __name__ == "__main__":
    # Run reconnaissance
    asyncio.run(main())