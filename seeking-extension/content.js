// seeking-extension/content.js

// Configuration object for selectors (easy to update)
const SELECTORS = {
  profile: ['.user-profile', '.profile-icon', '.user-avatar', '#user-menu'],
  logout: ['a[href*="logout"]', '[data-testid="logout"]', '.logout-link', 'button[aria-label="Sign out"]'],
  authTokens: ['authToken', 'sessionId', 'userToken', 'access_token'],
  userContent: ['.user-nav', '.dashboard', '.member-area'],
  targetInput: 'input[name="q"], input[type="search"], .search-input, #search-box'
};

// Global state management
let extensionEnabled = true;
let hasSimulated = false;

// Function to reliably detect login status
function isLoggedIn() {
  try {
    // Primary checks: DOM elements
    const profileElement = SELECTORS.profile.some(selector => 
      document.querySelector(selector) !== null
    );
    
    const logoutButton = SELECTORS.logout.some(selector => 
      document.querySelector(selector) !== null
    );
    
    // Fallback: Check localStorage for auth tokens
    const hasAuthToken = SELECTORS.authTokens.some(token => {
      const value = localStorage.getItem(token) || sessionStorage.getItem(token);
      return value && value.length > 0;
    });
    
    // Additional check: Look for user-specific content
    const userContent = SELECTORS.userContent.some(selector => 
      document.querySelector(selector) !== null
    ) || document.body.textContent.includes('Welcome');
    
    // Cookie check as additional fallback
    const hasAuthCookie = document.cookie.split(';').some(cookie => 
      cookie.includes('auth') || cookie.includes('session') || cookie.includes('logged')
    );
    
    const isLogged = !!(profileElement || logoutButton || hasAuthToken || userContent || hasAuthCookie);
    
    console.log('[Seeking Extension] Login detection:', {
      profileElement,
      logoutButton,
      hasAuthToken,
      userContent,
      hasAuthCookie,
      result: isLogged
    });
    
    return isLogged;
  } catch (error) {
    console.error('[Seeking Extension] Login detection failed:', error);
    return false;
  }
}

// Function to simulate Enter key with multiple fallbacks
function simulateEnter(targetSelector) {
  try {
    // Try to find the target element using multiple selectors
    const selectors = targetSelector.split(',').map(s => s.trim());
    let target = null;
    
    for (const selector of selectors) {
      target = document.querySelector(selector);
      if (target) break;
    }
    
    if (!target) {
      console.warn('[Seeking Extension] No target element found for simulation');
      return false;
    }
    
    console.log('[Seeking Extension] Target element found:', target);
    
    // Method 1: Focus and dispatch keyboard event
    target.focus();
    target.click(); // Ensure element is active
    
    const enterEvent = new KeyboardEvent('keydown', {
      key: 'Enter',
      code: 'Enter',
      keyCode: 13,
      which: 13,
      bubbles: true,
      cancelable: true,
      view: window,
      composed: true
    });
    
    const keyupEvent = new KeyboardEvent('keyup', {
      key: 'Enter',
      code: 'Enter',
      keyCode: 13,
      which: 13,
      bubbles: true,
      cancelable: true,
      view: window,
      composed: true
    });
    
    const keypressEvent = new KeyboardEvent('keypress', {
      key: 'Enter',
      code: 'Enter',
      keyCode: 13,
      which: 13,
      bubbles: true,
      cancelable: true,
      view: window,
      composed: true
    });
    
    // Dispatch all keyboard events for maximum compatibility
    target.dispatchEvent(enterEvent);
    target.dispatchEvent(keypressEvent);
    target.dispatchEvent(keyupEvent);
    
    // Method 2: Form submission fallback
    if (target.form && typeof target.form.submit === 'function') {
      console.log('[Seeking Extension] Attempting form submission fallback');
      setTimeout(() => {
        target.form.submit();
      }, 100);
    }
    
    // Method 3: Click fallback for submit buttons
    if (target.type === 'submit' || target.tagName === 'BUTTON') {
      console.log('[Seeking Extension] Attempting button click fallback');
      target.click();
    }
    
    // Method 4: Look for associated submit button
    if (target.form) {
      const submitBtn = target.form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn) {
        console.log('[Seeking Extension] Clicking associated submit button');
        submitBtn.click();
      }
    }
    
    // Method 5: Trigger change and input events
    const changeEvent = new Event('change', { bubbles: true });
    const inputEvent = new Event('input', { bubbles: true });
    target.dispatchEvent(inputEvent);
    target.dispatchEvent(changeEvent);
    
    console.log('[Seeking Extension] Enter simulation completed');
    return true;
    
  } catch (error) {
    console.error('[Seeking Extension] Enter simulation failed:', error);
    return false;
  }
}

// Function to check extension status
async function checkExtensionStatus() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(['enabled'], (result) => {
      extensionEnabled = result.enabled !== false; // Default to true
      resolve(extensionEnabled);
    });
  });
}

// Main execution function
async function executeMainLogic() {
  // Check if extension is enabled
  const isEnabled = await checkExtensionStatus();
  if (!isEnabled) {
    console.log('[Seeking Extension] Extension is disabled');
    return;
  }
  
  // Avoid duplicate execution
  if (hasSimulated) {
    console.log('[Seeking Extension] Already simulated, skipping');
    return;
  }
  
  if (isLoggedIn()) {
    console.log('[Seeking Extension] User is logged in on Seeking.com');
    
    // Wait a bit for page to fully load
    setTimeout(() => {
      const success = simulateEnter(SELECTORS.targetInput);
      if (success) {
        hasSimulated = true;
        // Send success message to service worker
        chrome.runtime.sendMessage({ 
          action: 'simulation_complete', 
          success: true,
          url: window.location.href 
        });
      }
    }, 1000);
    
  } else {
    console.log('[Seeking Extension] User is not logged in');
    chrome.runtime.sendMessage({ 
      action: 'login_status', 
      loggedIn: false,
      url: window.location.href 
    });
  }
}

// MutationObserver for dynamic content
const observer = new MutationObserver((mutations) => {
  // Check if significant changes occurred
  const significantChange = mutations.some(mutation => 
    mutation.addedNodes.length > 0 || 
    mutation.type === 'childList'
  );
  
  if (significantChange && !hasSimulated) {
    executeMainLogic();
  }
});

// Start observing when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    observer.observe(document.body, { 
      childList: true, 
      subtree: true,
      attributes: false // Avoid excessive triggers
    });
    executeMainLogic();
  });
} else {
  observer.observe(document.body, { 
    childList: true, 
    subtree: true,
    attributes: false
  });
  executeMainLogic();
}

// Listen for messages from popup or service worker
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'check_status') {
    sendResponse({ 
      loggedIn: isLoggedIn(),
      hasSimulated: hasSimulated,
      enabled: extensionEnabled
    });
  } else if (request.action === 'reset') {
    hasSimulated = false;
    executeMainLogic();
    sendResponse({ status: 'reset' });
  } else if (request.action === 'toggle') {
    extensionEnabled = !extensionEnabled;
    sendResponse({ enabled: extensionEnabled });
  }
  return true;
});

// Initial message to service worker
chrome.runtime.sendMessage({ 
  action: 'content_loaded', 
  url: window.location.href,
  timestamp: new Date().toISOString()
});

// Clean up observer on page unload
window.addEventListener('beforeunload', () => {
  observer.disconnect();
});