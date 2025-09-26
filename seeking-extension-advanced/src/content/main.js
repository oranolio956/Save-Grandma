/**
 * Main Content Script - Complete Implementation
 * Orchestrates all modules with full functionality
 */

// Import modules (they're loaded via manifest.json)
/* global SecureStorage, PerformanceCache, DOMCache, HumanBehaviorSimulator, MLLoginDetector */

class SeekingAutomationController {
  constructor() {
    // Initialize all systems
    this.security = new SecureStorage();
    this.cache = new PerformanceCache({ maxSize: 500, maxMemory: 10 * 1024 * 1024 });
    this.domCache = new DOMCache();
    this.behaviorSimulator = new HumanBehaviorSimulator();
    this.loginDetector = new MLLoginDetector();
    
    // State management
    this.state = {
      enabled: true,
      hasSimulated: false,
      isLoggedIn: false,
      confidence: 0,
      lastCheck: null,
      sessionId: this.generateSessionId()
    };
    
    // Configuration
    this.config = {
      autoSimulate: true,
      debugMode: false,
      checkInterval: 2000,
      simulationDelay: 1000,
      retryAttempts: 3,
      targetSelectors: [
        'input[name="q"]',
        'input[type="search"]',
        '.search-input',
        '#search-box',
        'input[placeholder*="search" i]',
        'input[placeholder*="find" i]',
        'input.form-control',
        'input.text-input'
      ]
    };
    
    // Performance monitoring
    this.metrics = {
      detectionTime: [],
      simulationTime: [],
      successRate: { success: 0, total: 0 }
    };
    
    // Initialize
    this.initialize();
  }

  /**
   * Initialize the controller
   */
  async initialize() {
    console.log('[Seeking Extension] Initializing automation controller...');
    
    try {
      // Load settings from storage
      await this.loadSettings();
      
      // Setup message listeners
      this.setupMessageListeners();
      
      // Setup mutation observer for dynamic content
      this.setupMutationObserver();
      
      // Setup network interceptors
      this.setupNetworkInterceptors();
      
      // Setup keyboard shortcuts
      this.setupKeyboardShortcuts();
      
      // Perform initial detection
      await this.performDetection();
      
      // Start monitoring
      if (this.state.enabled) {
        this.startMonitoring();
      }
      
      // Send initialization complete message
      this.sendMessage('initialized', {
        sessionId: this.state.sessionId,
        url: window.location.href,
        timestamp: Date.now()
      });
      
      console.log('[Seeking Extension] Initialization complete');
    } catch (error) {
      console.error('[Seeking Extension] Initialization failed:', error);
      this.handleError(error);
    }
  }

  /**
   * Load settings from secure storage
   */
  async loadSettings() {
    try {
      const encryptedSettings = await chrome.storage.sync.get([
        'enabled', 'autoSimulate', 'debugMode', 'customSelectors'
      ]);
      
      // Decrypt sensitive settings
      if (encryptedSettings.customSelectors) {
        const decrypted = await this.security.secureGet('customSelectors');
        if (decrypted) {
          this.config.targetSelectors = [
            ...this.config.targetSelectors,
            ...decrypted
          ];
        }
      }
      
      // Apply settings
      this.state.enabled = encryptedSettings.enabled !== false;
      this.config.autoSimulate = encryptedSettings.autoSimulate !== false;
      this.config.debugMode = encryptedSettings.debugMode === true;
      
      if (this.config.debugMode) {
        console.log('[Seeking Extension] Settings loaded:', {
          enabled: this.state.enabled,
          autoSimulate: this.config.autoSimulate,
          selectors: this.config.targetSelectors.length
        });
      }
    } catch (error) {
      console.error('[Seeking Extension] Failed to load settings:', error);
    }
  }

  /**
   * Setup message listeners for communication with service worker and popup
   */
  setupMessageListeners() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (this.config.debugMode) {
        console.log('[Seeking Extension] Message received:', request.action);
      }
      
      switch (request.action) {
        case 'check_status':
          sendResponse(this.getStatus());
          break;
          
        case 'toggle':
          this.toggleExtension();
          sendResponse({ enabled: this.state.enabled });
          break;
          
        case 'simulate':
          this.manualSimulation();
          sendResponse({ status: 'simulating' });
          break;
          
        case 'reset':
          this.resetState();
          sendResponse({ status: 'reset' });
          break;
          
        case 'update_settings':
          this.updateSettings(request.settings);
          sendResponse({ status: 'updated' });
          break;
          
        case 'get_metrics':
          sendResponse(this.getMetrics());
          break;
          
        case 'provide_feedback':
          this.provideFeedback(request.correct);
          sendResponse({ status: 'feedback_received' });
          break;
          
        default:
          sendResponse({ error: 'Unknown action' });
      }
      
      return true; // Keep channel open for async response
    });
  }

  /**
   * Setup mutation observer for dynamic content changes
   */
  setupMutationObserver() {
    let observerTimeout = null;
    
    const observer = new MutationObserver((mutations) => {
      // Debounce mutations
      clearTimeout(observerTimeout);
      observerTimeout = setTimeout(() => {
        this.handleMutations(mutations);
      }, 500);
    });
    
    // Start observing with optimized config
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: false, // Don't observe attribute changes
      characterData: false // Don't observe text changes
    });
    
    // Store observer for cleanup
    this.observer = observer;
  }

  /**
   * Handle DOM mutations
   */
  async handleMutations(mutations) {
    // Check if significant changes occurred
    let significantChange = false;
    
    for (const mutation of mutations) {
      if (mutation.addedNodes.length > 0) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if added element might be login-related
            const element = node;
            if (element.classList?.contains('user') ||
                element.classList?.contains('profile') ||
                element.classList?.contains('login') ||
                element.id?.includes('user') ||
                element.querySelector?.('input[type="search"]')) {
              significantChange = true;
              break;
            }
          }
        }
      }
      
      if (significantChange) break;
    }
    
    if (significantChange && !this.state.hasSimulated) {
      if (this.config.debugMode) {
        console.log('[Seeking Extension] Significant DOM change detected');
      }
      
      // Invalidate DOM cache
      this.domCache.clear();
      
      // Re-run detection
      await this.performDetection();
    }
  }

  /**
   * Setup network interceptors for auth detection
   */
  setupNetworkInterceptors() {
    // Intercept fetch
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const [url, options] = args;
      
      // Check for auth headers
      if (options?.headers) {
        const headers = options.headers;
        if (headers.Authorization || headers.authorization || 
            headers['X-Auth-Token'] || headers['X-Session-Id']) {
          window.fetch._hasAuth = true;
          
          // Notify detector
          if (this.loginDetector) {
            this.loginDetector.recordNetworkAuth(true);
          }
        }
      }
      
      // Call original fetch
      const response = await originalFetch.apply(window, args);
      
      // Check response for auth indicators
      if (response.headers) {
        const authHeader = response.headers.get('X-Auth-Token') || 
                          response.headers.get('Set-Cookie');
        if (authHeader) {
          window.fetch._hasAuth = true;
        }
      }
      
      return response;
    };
    window.fetch._intercepted = true;
    
    // Intercept XMLHttpRequest
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;
    
    XMLHttpRequest.prototype.open = function(...args) {
      this._url = args[1];
      return originalOpen.apply(this, args);
    };
    
    XMLHttpRequest.prototype.setRequestHeader = function(header, value) {
      if (header.toLowerCase() === 'authorization' || 
          header.toLowerCase() === 'x-auth-token') {
        window.fetch._hasAuth = true;
      }
      return originalSetRequestHeader.apply(this, arguments);
    };
  }

  /**
   * Setup keyboard shortcuts
   */
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
      // Ctrl/Cmd + Shift + S: Toggle extension
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'S') {
        event.preventDefault();
        this.toggleExtension();
      }
      
      // Ctrl/Cmd + Shift + E: Manual simulation
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'E') {
        event.preventDefault();
        this.manualSimulation();
      }
    });
  }

  /**
   * Perform login detection
   */
  async performDetection() {
    const startTime = performance.now();
    
    try {
      // Use ML detector for prediction
      const result = await this.loginDetector.predictLoginStatus();
      
      this.state.isLoggedIn = result.isLoggedIn;
      this.state.confidence = result.confidence;
      this.state.lastCheck = Date.now();
      
      // Record metrics
      const detectionTime = performance.now() - startTime;
      this.metrics.detectionTime.push(detectionTime);
      
      if (this.config.debugMode) {
        console.log('[Seeking Extension] Detection result:', {
          isLoggedIn: result.isLoggedIn,
          confidence: (result.confidence * 100).toFixed(2) + '%',
          method: result.method,
          time: detectionTime.toFixed(2) + 'ms'
        });
      }
      
      // Send detection result to service worker
      this.sendMessage('detection_complete', {
        isLoggedIn: this.state.isLoggedIn,
        confidence: this.state.confidence,
        url: window.location.href
      });
      
      // Auto-simulate if logged in and not already simulated
      if (this.state.isLoggedIn && !this.state.hasSimulated && this.config.autoSimulate) {
        setTimeout(() => {
          this.performSimulation();
        }, this.config.simulationDelay);
      }
      
    } catch (error) {
      console.error('[Seeking Extension] Detection failed:', error);
      this.handleError(error);
    }
  }

  /**
   * Perform Enter key simulation
   */
  async performSimulation() {
    if (this.state.hasSimulated) {
      console.log('[Seeking Extension] Already simulated, skipping');
      return;
    }
    
    const startTime = performance.now();
    let success = false;
    
    try {
      // Find target element
      const targetElement = await this.findTargetElement();
      
      if (!targetElement) {
        console.warn('[Seeking Extension] No target element found');
        this.metrics.successRate.total++;
        return;
      }
      
      if (this.config.debugMode) {
        console.log('[Seeking Extension] Target element found:', {
          tag: targetElement.tagName,
          id: targetElement.id,
          class: targetElement.className
        });
      }
      
      // Use human behavior simulator for realistic interaction
      await this.behaviorSimulator.simulateCompleteInteraction(targetElement, '');
      
      // Simulate Enter key
      success = await this.simulateEnterKey(targetElement);
      
      if (success) {
        this.state.hasSimulated = true;
        this.metrics.successRate.success++;
        
        // Cache successful selector
        const selector = this.getElementSelector(targetElement);
        this.cache.set(`successful_selector_${window.location.hostname}`, selector, {
          ttl: 86400000 // 24 hours
        });
      }
      
    } catch (error) {
      console.error('[Seeking Extension] Simulation failed:', error);
      this.handleError(error);
    } finally {
      this.metrics.successRate.total++;
      
      const simulationTime = performance.now() - startTime;
      this.metrics.simulationTime.push(simulationTime);
      
      // Send result to service worker
      this.sendMessage('simulation_complete', {
        success: success,
        time: simulationTime,
        url: window.location.href
      });
    }
  }

  /**
   * Find target element for simulation
   */
  async findTargetElement() {
    // Check cache first
    const cachedSelector = this.cache.get(`successful_selector_${window.location.hostname}`);
    if (cachedSelector) {
      const element = this.domCache.getElement(cachedSelector);
      if (element) {
        return element;
      }
    }
    
    // Try each selector
    for (const selector of this.config.targetSelectors) {
      const element = this.domCache.getElement(selector);
      if (element && this.isValidTarget(element)) {
        return element;
      }
    }
    
    // Use ML to find best element
    const allInputs = document.querySelectorAll('input:not([type="hidden"])');
    if (allInputs.length > 0 && this.loginDetector) {
      const candidates = Array.from(allInputs).filter(el => this.isValidTarget(el));
      
      // Score each candidate
      const scored = [];
      for (const candidate of candidates) {
        const score = this.scoreElement(candidate);
        scored.push({ element: candidate, score });
      }
      
      // Sort by score and return best
      scored.sort((a, b) => b.score - a.score);
      if (scored.length > 0) {
        return scored[0].element;
      }
    }
    
    return null;
  }

  /**
   * Check if element is valid target
   */
  isValidTarget(element) {
    if (!element || !element.isConnected) return false;
    if (element.disabled || element.readOnly) return false;
    if (element.type === 'hidden' || element.type === 'password') return false;
    
    const style = window.getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden') return false;
    if (parseFloat(style.opacity) === 0) return false;
    
    const rect = element.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return false;
    
    return true;
  }

  /**
   * Score element for targeting
   */
  scoreElement(element) {
    let score = 0;
    
    // Position score (higher = better)
    const rect = element.getBoundingClientRect();
    if (rect.top < window.innerHeight / 2) score += 2; // Upper half of viewport
    if (rect.left < window.innerWidth / 2) score += 1; // Left half
    
    // Attribute score
    const placeholder = element.placeholder?.toLowerCase() || '';
    if (placeholder.includes('search')) score += 5;
    if (placeholder.includes('find')) score += 4;
    if (placeholder.includes('query')) score += 3;
    
    const name = element.name?.toLowerCase() || '';
    if (name === 'q') score += 5;
    if (name.includes('search')) score += 4;
    if (name.includes('query')) score += 3;
    
    // Type score
    if (element.type === 'search') score += 5;
    if (element.type === 'text') score += 2;
    
    // Class/ID score
    const className = element.className?.toLowerCase() || '';
    const id = element.id?.toLowerCase() || '';
    
    if (className.includes('search') || id.includes('search')) score += 3;
    if (className.includes('input') || id.includes('input')) score += 1;
    
    // Form association
    if (element.form) score += 2;
    
    return score;
  }

  /**
   * Get CSS selector for element
   */
  getElementSelector(element) {
    if (element.id) {
      return `#${element.id}`;
    }
    
    if (element.className) {
      const classes = element.className.split(' ').filter(c => c.length > 0);
      if (classes.length > 0) {
        return `${element.tagName.toLowerCase()}.${classes.join('.')}`;
      }
    }
    
    // Generate path selector
    const path = [];
    let current = element;
    
    while (current && current.nodeType === Node.ELEMENT_NODE) {
      let selector = current.nodeName.toLowerCase();
      
      if (current.id) {
        selector = `#${current.id}`;
        path.unshift(selector);
        break;
      }
      
      const sibling = current.parentNode?.children;
      if (sibling && sibling.length > 1) {
        const index = Array.from(sibling).indexOf(current) + 1;
        selector += `:nth-child(${index})`;
      }
      
      path.unshift(selector);
      current = current.parentNode;
    }
    
    return path.join(' > ');
  }

  /**
   * Simulate Enter key with multiple methods
   */
  async simulateEnterKey(element) {
    const methods = [
      () => this.simulateKeyboardEvent(element),
      () => this.simulateFormSubmit(element),
      () => this.simulateButtonClick(element),
      () => this.simulateInputEvent(element),
      () => this.simulateNativeEvent(element)
    ];
    
    for (let attempt = 0; attempt < this.config.retryAttempts; attempt++) {
      for (const method of methods) {
        try {
          const success = await method();
          if (success) {
            return true;
          }
        } catch (error) {
          if (this.config.debugMode) {
            console.warn('[Seeking Extension] Method failed:', error);
          }
        }
      }
      
      // Wait before retry
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    return false;
  }

  /**
   * Simulate keyboard event
   */
  async simulateKeyboardEvent(element) {
    element.focus();
    
    const events = ['keydown', 'keypress', 'keyup'];
    
    for (const eventType of events) {
      const event = new KeyboardEvent(eventType, {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        which: 13,
        charCode: 13,
        bubbles: true,
        cancelable: true,
        composed: true,
        view: window
      });
      
      const prevented = !element.dispatchEvent(event);
      
      if (prevented && eventType === 'keydown') {
        // Event was handled
        return true;
      }
      
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    
    return false;
  }

  /**
   * Simulate form submit
   */
  async simulateFormSubmit(element) {
    if (element.form) {
      // Check if form has submit button
      const submitButton = element.form.querySelector(
        'button[type="submit"], input[type="submit"], button:not([type])'
      );
      
      if (submitButton) {
        submitButton.click();
        return true;
      }
      
      // Try form submit
      if (typeof element.form.submit === 'function') {
        element.form.submit();
        return true;
      }
      
      // Dispatch submit event
      const submitEvent = new Event('submit', {
        bubbles: true,
        cancelable: true
      });
      
      const prevented = !element.form.dispatchEvent(submitEvent);
      if (!prevented) {
        element.form.submit();
      }
      
      return true;
    }
    
    return false;
  }

  /**
   * Simulate button click
   */
  async simulateButtonClick(element) {
    // Find nearby button
    const parent = element.parentElement;
    if (parent) {
      const button = parent.querySelector('button, [role="button"]');
      if (button) {
        button.click();
        return true;
      }
    }
    
    return false;
  }

  /**
   * Simulate input event
   */
  async simulateInputEvent(element) {
    const inputEvent = new Event('input', {
      bubbles: true,
      cancelable: true
    });
    
    element.dispatchEvent(inputEvent);
    
    const changeEvent = new Event('change', {
      bubbles: true,
      cancelable: true
    });
    
    element.dispatchEvent(changeEvent);
    
    return false; // This method doesn't confirm success
  }

  /**
   * Simulate native event using Chrome Debugger API
   */
  async simulateNativeEvent(element) {
    // This requires debugger permission
    if (chrome.debugger) {
      try {
        const tabId = await this.getTabId();
        
        await chrome.debugger.attach({ tabId }, "1.3");
        
        await chrome.debugger.sendCommand(
          { tabId },
          "Input.dispatchKeyEvent",
          {
            type: "keyDown",
            key: "Enter",
            code: "Enter",
            nativeVirtualKeyCode: 13,
            windowsVirtualKeyCode: 13
          }
        );
        
        await chrome.debugger.detach({ tabId });
        
        return true;
      } catch (error) {
        // Debugger not available or failed
      }
    }
    
    return false;
  }

  /**
   * Get current tab ID
   */
  async getTabId() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: 'get_tab_id' }, (response) => {
        resolve(response.tabId);
      });
    });
  }

  /**
   * Start monitoring for changes
   */
  startMonitoring() {
    if (this.monitorInterval) {
      clearInterval(this.monitorInterval);
    }
    
    this.monitorInterval = setInterval(() => {
      if (this.state.enabled && !this.state.hasSimulated) {
        this.performDetection();
      }
    }, this.config.checkInterval);
  }

  /**
   * Stop monitoring
   */
  stopMonitoring() {
    if (this.monitorInterval) {
      clearInterval(this.monitorInterval);
      this.monitorInterval = null;
    }
  }

  /**
   * Toggle extension on/off
   */
  toggleExtension() {
    this.state.enabled = !this.state.enabled;
    
    if (this.state.enabled) {
      this.startMonitoring();
      this.performDetection();
    } else {
      this.stopMonitoring();
    }
    
    // Save state
    chrome.storage.sync.set({ enabled: this.state.enabled });
    
    // Notify service worker
    this.sendMessage('toggle', { enabled: this.state.enabled });
    
    console.log(`[Seeking Extension] Extension ${this.state.enabled ? 'enabled' : 'disabled'}`);
  }

  /**
   * Manual simulation trigger
   */
  async manualSimulation() {
    console.log('[Seeking Extension] Manual simulation triggered');
    
    this.state.hasSimulated = false;
    await this.performSimulation();
  }

  /**
   * Reset state
   */
  resetState() {
    this.state.hasSimulated = false;
    this.state.isLoggedIn = false;
    this.state.confidence = 0;
    
    // Clear caches
    this.cache.clear();
    this.domCache.clear();
    
    console.log('[Seeking Extension] State reset');
    
    // Re-run detection
    this.performDetection();
  }

  /**
   * Update settings
   */
  async updateSettings(settings) {
    if (settings.enabled !== undefined) {
      this.state.enabled = settings.enabled;
    }
    
    if (settings.autoSimulate !== undefined) {
      this.config.autoSimulate = settings.autoSimulate;
    }
    
    if (settings.debugMode !== undefined) {
      this.config.debugMode = settings.debugMode;
    }
    
    // Save to storage
    await chrome.storage.sync.set(settings);
    
    // Apply changes
    if (this.state.enabled) {
      this.startMonitoring();
    } else {
      this.stopMonitoring();
    }
  }

  /**
   * Get current status
   */
  getStatus() {
    return {
      enabled: this.state.enabled,
      isLoggedIn: this.state.isLoggedIn,
      hasSimulated: this.state.hasSimulated,
      confidence: this.state.confidence,
      lastCheck: this.state.lastCheck,
      sessionId: this.state.sessionId
    };
  }

  /**
   * Get performance metrics
   */
  getMetrics() {
    const avgDetectionTime = this.metrics.detectionTime.length > 0
      ? this.metrics.detectionTime.reduce((a, b) => a + b, 0) / this.metrics.detectionTime.length
      : 0;
    
    const avgSimulationTime = this.metrics.simulationTime.length > 0
      ? this.metrics.simulationTime.reduce((a, b) => a + b, 0) / this.metrics.simulationTime.length
      : 0;
    
    const successRate = this.metrics.successRate.total > 0
      ? (this.metrics.successRate.success / this.metrics.successRate.total) * 100
      : 0;
    
    return {
      avgDetectionTime: avgDetectionTime.toFixed(2) + 'ms',
      avgSimulationTime: avgSimulationTime.toFixed(2) + 'ms',
      successRate: successRate.toFixed(2) + '%',
      totalDetections: this.metrics.detectionTime.length,
      totalSimulations: this.metrics.successRate.total,
      cacheStats: this.cache.getStats(),
      sessionDuration: Date.now() - parseInt(this.state.sessionId.split('-')[0])
    };
  }

  /**
   * Provide feedback for ML model
   */
  async provideFeedback(wasCorrect) {
    await this.loginDetector.provideFeedback(wasCorrect);
    
    console.log(`[Seeking Extension] Feedback provided: ${wasCorrect ? 'correct' : 'incorrect'}`);
  }

  /**
   * Send message to service worker
   */
  sendMessage(action, data) {
    chrome.runtime.sendMessage({
      action: action,
      data: data,
      timestamp: Date.now()
    }).catch(error => {
      // Service worker might not be ready
      if (this.config.debugMode) {
        console.warn('[Seeking Extension] Failed to send message:', error);
      }
    });
  }

  /**
   * Handle errors
   */
  handleError(error) {
    console.error('[Seeking Extension] Error:', error);
    
    // Send error to service worker for logging
    this.sendMessage('error', {
      message: error.message,
      stack: error.stack,
      url: window.location.href
    });
  }

  /**
   * Generate unique session ID
   */
  generateSessionId() {
    return Date.now() + '-' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Cleanup on unload
   */
  destroy() {
    // Stop monitoring
    this.stopMonitoring();
    
    // Disconnect observer
    if (this.observer) {
      this.observer.disconnect();
    }
    
    // Clear caches
    this.cache.clear();
    this.domCache.destroy();
    
    // Save final metrics
    this.sendMessage('session_end', {
      sessionId: this.state.sessionId,
      metrics: this.getMetrics()
    });
    
    console.log('[Seeking Extension] Controller destroyed');
  }
}

// Initialize controller when DOM is ready
let controller = null;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    controller = new SeekingAutomationController();
  });
} else {
  controller = new SeekingAutomationController();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (controller) {
    controller.destroy();
  }
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SeekingAutomationController;
}