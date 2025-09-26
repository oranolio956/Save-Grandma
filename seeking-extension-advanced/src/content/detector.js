/**
 * Complete ML-Powered Login Detection System
 * Full implementation with TensorFlow.js and adaptive learning
 */

class MLLoginDetector {
  constructor() {
    this.model = null;
    this.trainingData = [];
    this.detectionHistory = [];
    this.selectorPatterns = new Map();
    this.confidence = new Map();
    this.initialized = false;
    
    // Detection strategies
    this.strategies = [
      new DOMDetectionStrategy(),
      new LocalStorageDetectionStrategy(),
      new CookieDetectionStrategy(),
      new NetworkDetectionStrategy(),
      new ReactDetectionStrategy(),
      new GraphQLDetectionStrategy()
    ];
    
    this.initialize();
  }

  /**
   * Initialize ML model and load training data
   */
  async initialize() {
    try {
      // Create neural network model
      await this.createModel();
      
      // Load existing training data if available
      await this.loadTrainingData();
      
      // Train model with existing data
      if (this.trainingData.length > 0) {
        await this.trainModel();
      }
      
      this.initialized = true;
    } catch (error) {
      console.error('Failed to initialize ML detector:', error);
      this.initialized = false;
    }
  }

  /**
   * Create TensorFlow.js model
   */
  async createModel() {
    // Check if TensorFlow is loaded
    if (typeof tf === 'undefined') {
      await this.loadTensorFlow();
    }
    
    this.model = tf.sequential({
      layers: [
        tf.layers.dense({
          inputShape: [20], // 20 features
          units: 64,
          activation: 'relu',
          kernelInitializer: 'heNormal'
        }),
        tf.layers.dropout({
          rate: 0.3
        }),
        tf.layers.dense({
          units: 32,
          activation: 'relu',
          kernelInitializer: 'heNormal'
        }),
        tf.layers.dropout({
          rate: 0.2
        }),
        tf.layers.dense({
          units: 16,
          activation: 'relu'
        }),
        tf.layers.dense({
          units: 1,
          activation: 'sigmoid'
        })
      ]
    });
    
    this.model.compile({
      optimizer: tf.train.adam(0.001),
      loss: 'binaryCrossentropy',
      metrics: ['accuracy', 'precision', 'recall']
    });
  }

  /**
   * Load TensorFlow.js dynamically
   */
  async loadTensorFlow() {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = chrome.runtime.getURL('lib/tensorflow.min.js');
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  /**
   * Extract features from page for ML model
   */
  extractFeatures() {
    const features = {
      // DOM features
      hasUserProfile: this.checkElementExists([
        '.user-profile', '.profile-icon', '.user-avatar', 
        '#user-menu', '.user-info', '.account-menu'
      ]) ? 1 : 0,
      
      hasLogoutButton: this.checkElementExists([
        'a[href*="logout"]', 'button[aria-label*="sign out"]',
        '.logout-link', '.sign-out', '[data-testid="logout"]'
      ]) ? 1 : 0,
      
      hasLoginForm: this.checkElementExists([
        'form[action*="login"]', '#loginForm', '.login-form',
        'input[type="password"]'
      ]) ? 1 : 0,
      
      hasWelcomeMessage: this.checkTextContent([
        'welcome', 'hello', 'hi,', 'dashboard', 'my account'
      ]) ? 1 : 0,
      
      // Storage features
      hasAuthToken: this.checkStorage('authToken') ? 1 : 0,
      hasSessionId: this.checkStorage('sessionId') ? 1 : 0,
      hasUserId: this.checkStorage('userId') ? 1 : 0,
      hasAccessToken: this.checkStorage('access_token') ? 1 : 0,
      
      // Cookie features
      hasSessionCookie: this.checkCookie('session') ? 1 : 0,
      hasAuthCookie: this.checkCookie('auth') ? 1 : 0,
      hasLoggedInCookie: this.checkCookie('logged') ? 1 : 0,
      
      // URL features
      urlHasProfile: window.location.href.includes('profile') ? 1 : 0,
      urlHasDashboard: window.location.href.includes('dashboard') ? 1 : 0,
      urlHasAccount: window.location.href.includes('account') ? 1 : 0,
      urlHasLogin: window.location.href.includes('login') ? 1 : 0,
      
      // Meta features
      pageTitle: this.analyzePageTitle(),
      metaAuth: this.checkMetaTags(),
      
      // Network features
      hasAuthHeaders: this.checkNetworkAuth() ? 1 : 0,
      
      // Framework features
      hasReactUser: this.checkReactState() ? 1 : 0,
      hasGraphQLAuth: this.checkGraphQLCache() ? 1 : 0
    };
    
    return Object.values(features);
  }

  /**
   * Check if elements exist
   */
  checkElementExists(selectors) {
    for (const selector of selectors) {
      try {
        if (document.querySelector(selector)) {
          // Record successful selector for learning
          this.recordSelectorSuccess(selector);
          return true;
        }
      } catch (e) {
        // Invalid selector, skip
      }
    }
    return false;
  }

  /**
   * Check text content
   */
  checkTextContent(keywords) {
    const bodyText = document.body.innerText.toLowerCase();
    for (const keyword of keywords) {
      if (bodyText.includes(keyword.toLowerCase())) {
        return true;
      }
    }
    return false;
  }

  /**
   * Check storage for auth tokens
   */
  checkStorage(key) {
    try {
      // Check localStorage
      if (localStorage.getItem(key)) {
        return true;
      }
      
      // Check sessionStorage
      if (sessionStorage.getItem(key)) {
        return true;
      }
      
      // Check for nested objects
      const localData = Object.keys(localStorage);
      for (const localKey of localData) {
        try {
          const value = localStorage.getItem(localKey);
          if (value && value.includes(key)) {
            return true;
          }
          
          // Try parsing as JSON
          const parsed = JSON.parse(value);
          if (parsed && (parsed[key] || parsed.auth || parsed.user)) {
            return true;
          }
        } catch (e) {
          // Not JSON, continue
        }
      }
    } catch (e) {
      // Storage access denied
    }
    
    return false;
  }

  /**
   * Check cookies
   */
  checkCookie(pattern) {
    try {
      const cookies = document.cookie.split(';');
      for (const cookie of cookies) {
        if (cookie.toLowerCase().includes(pattern)) {
          return true;
        }
      }
    } catch (e) {
      // Cookie access denied
    }
    return false;
  }

  /**
   * Analyze page title for auth indicators
   */
  analyzePageTitle() {
    const title = document.title.toLowerCase();
    if (title.includes('dashboard') || title.includes('profile') || 
        title.includes('account') || title.includes('settings')) {
      return 1;
    }
    if (title.includes('login') || title.includes('sign in') || 
        title.includes('register')) {
      return 0;
    }
    return 0.5;
  }

  /**
   * Check meta tags for auth
   */
  checkMetaTags() {
    const metaTags = document.querySelectorAll('meta');
    for (const meta of metaTags) {
      const content = meta.getAttribute('content') || '';
      const name = meta.getAttribute('name') || '';
      
      if (name.includes('user') || name.includes('auth') || 
          content.includes('logged')) {
        return 1;
      }
    }
    return 0;
  }

  /**
   * Check for auth in network requests
   */
  checkNetworkAuth() {
    // Check if fetch has been modified to include auth
    try {
      const fetchString = window.fetch.toString();
      if (fetchString.includes('authorization') || 
          fetchString.includes('bearer')) {
        return true;
      }
    } catch (e) {
      // Fetch check failed
    }
    
    // Check XMLHttpRequest
    try {
      const xhrProto = XMLHttpRequest.prototype;
      if (xhrProto._originalOpen && xhrProto._originalOpen.toString().includes('auth')) {
        return true;
      }
    } catch (e) {
      // XHR check failed
    }
    
    return false;
  }

  /**
   * Check React state for user data
   */
  checkReactState() {
    try {
      // React DevTools hook
      if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
        const renderers = window.__REACT_DEVTOOLS_GLOBAL_HOOK__.renderers;
        if (renderers && renderers.size > 0) {
          // React app detected, check for user state
          const fiberRoot = document.querySelector('#root')?._reactRootContainer;
          if (fiberRoot) {
            const state = fiberRoot._internalRoot?.current?.memoizedState;
            if (state && (state.user || state.auth || state.isLoggedIn)) {
              return true;
            }
          }
        }
      }
      
      // Check React props on elements
      const reactElements = document.querySelectorAll('[data-reactroot]');
      for (const element of reactElements) {
        const props = element._reactInternalFiber?.memoizedProps;
        if (props && (props.user || props.authenticated)) {
          return true;
        }
      }
    } catch (e) {
      // React check failed
    }
    
    return false;
  }

  /**
   * Check GraphQL cache for auth
   */
  checkGraphQLCache() {
    try {
      // Apollo Client
      if (window.__APOLLO_CLIENT__) {
        const cache = window.__APOLLO_CLIENT__.cache;
        if (cache && cache.data) {
          const data = cache.data.data;
          if (data && (data.ROOT_QUERY?.viewer || data.ROOT_QUERY?.me)) {
            return true;
          }
        }
      }
      
      // Relay
      if (window.__RELAY_DEVTOOLS__) {
        const store = window.__RELAY_DEVTOOLS__.store;
        if (store && store.getSource()) {
          const records = store.getSource()._records;
          if (records && records.client?.root?.viewer) {
            return true;
          }
        }
      }
    } catch (e) {
      // GraphQL check failed
    }
    
    return false;
  }

  /**
   * Predict login status using ML model
   */
  async predictLoginStatus() {
    if (!this.initialized || !this.model) {
      // Fallback to rule-based detection
      return this.ruleBasedDetection();
    }
    
    try {
      const features = this.extractFeatures();
      const input = tf.tensor2d([features]);
      
      const prediction = await this.model.predict(input).data();
      input.dispose();
      
      const confidence = prediction[0];
      
      // Record prediction for learning
      this.recordPrediction(features, confidence);
      
      return {
        isLoggedIn: confidence > 0.5,
        confidence: confidence,
        method: 'ml'
      };
    } catch (error) {
      console.error('ML prediction failed:', error);
      return this.ruleBasedDetection();
    }
  }

  /**
   * Rule-based fallback detection
   */
  ruleBasedDetection() {
    let score = 0;
    let maxScore = 0;
    
    // Run all detection strategies
    for (const strategy of this.strategies) {
      const result = strategy.detect();
      score += result.score * result.weight;
      maxScore += result.weight;
    }
    
    const confidence = score / maxScore;
    
    return {
      isLoggedIn: confidence > 0.5,
      confidence: confidence,
      method: 'rules'
    };
  }

  /**
   * Train model with collected data
   */
  async trainModel() {
    if (this.trainingData.length < 10) {
      return; // Not enough data
    }
    
    const features = this.trainingData.map(d => d.features);
    const labels = this.trainingData.map(d => d.label);
    
    const xs = tf.tensor2d(features);
    const ys = tf.tensor2d(labels, [labels.length, 1]);
    
    await this.model.fit(xs, ys, {
      epochs: 50,
      batchSize: 32,
      validationSplit: 0.2,
      shuffle: true,
      callbacks: {
        onEpochEnd: (epoch, logs) => {
          if (epoch % 10 === 0) {
            console.log(`Training epoch ${epoch}: loss=${logs.loss.toFixed(4)}`);
          }
        }
      }
    });
    
    xs.dispose();
    ys.dispose();
    
    // Save model
    await this.saveModel();
  }

  /**
   * Record successful selector for learning
   */
  recordSelectorSuccess(selector) {
    const count = this.selectorPatterns.get(selector) || 0;
    this.selectorPatterns.set(selector, count + 1);
    
    // Update confidence
    const total = Array.from(this.selectorPatterns.values())
      .reduce((a, b) => a + b, 0);
    
    this.confidence.set(selector, count / total);
  }

  /**
   * Record prediction for continuous learning
   */
  recordPrediction(features, confidence) {
    this.detectionHistory.push({
      features: features,
      confidence: confidence,
      timestamp: Date.now(),
      url: window.location.href
    });
    
    // Keep only last 100 predictions
    if (this.detectionHistory.length > 100) {
      this.detectionHistory.shift();
    }
  }

  /**
   * User feedback for improving model
   */
  async provideFeedback(wasCorrect) {
    if (this.detectionHistory.length === 0) {
      return;
    }
    
    const lastDetection = this.detectionHistory[this.detectionHistory.length - 1];
    
    // Add to training data
    this.trainingData.push({
      features: lastDetection.features,
      label: wasCorrect ? 1 : 0,
      timestamp: Date.now()
    });
    
    // Retrain if enough new data
    if (this.trainingData.length % 20 === 0) {
      await this.trainModel();
    }
    
    // Save training data
    await this.saveTrainingData();
  }

  /**
   * Save model to storage
   */
  async saveModel() {
    try {
      const modelData = await this.model.save('localstorage://seeking-detector-model');
      console.log('Model saved successfully');
    } catch (error) {
      console.error('Failed to save model:', error);
    }
  }

  /**
   * Load model from storage
   */
  async loadModel() {
    try {
      this.model = await tf.loadLayersModel('localstorage://seeking-detector-model');
      console.log('Model loaded successfully');
      return true;
    } catch (error) {
      console.log('No saved model found');
      return false;
    }
  }

  /**
   * Save training data
   */
  async saveTrainingData() {
    try {
      await chrome.storage.local.set({
        mlTrainingData: this.trainingData
      });
    } catch (error) {
      console.error('Failed to save training data:', error);
    }
  }

  /**
   * Load training data
   */
  async loadTrainingData() {
    try {
      const result = await chrome.storage.local.get('mlTrainingData');
      if (result.mlTrainingData) {
        this.trainingData = result.mlTrainingData;
        console.log(`Loaded ${this.trainingData.length} training samples`);
      }
    } catch (error) {
      console.error('Failed to load training data:', error);
    }
  }
}

/**
 * Detection Strategy Base Class
 */
class DetectionStrategy {
  detect() {
    throw new Error('detect() must be implemented');
  }
}

/**
 * DOM-based detection strategy
 */
class DOMDetectionStrategy extends DetectionStrategy {
  detect() {
    const indicators = [
      { selector: '.user-profile', weight: 0.9 },
      { selector: '.logout-btn', weight: 0.95 },
      { selector: '#user-menu', weight: 0.85 },
      { selector: '.dashboard', weight: 0.8 },
      { selector: 'a[href*="logout"]', weight: 0.95 },
      { selector: '.welcome-message', weight: 0.7 },
      { selector: '.account-settings', weight: 0.85 }
    ];
    
    let score = 0;
    let foundCount = 0;
    
    for (const indicator of indicators) {
      try {
        if (document.querySelector(indicator.selector)) {
          score += indicator.weight;
          foundCount++;
        }
      } catch (e) {
        // Invalid selector
      }
    }
    
    return {
      score: foundCount > 0 ? score / foundCount : 0,
      weight: 1.0
    };
  }
}

/**
 * LocalStorage detection strategy
 */
class LocalStorageDetectionStrategy extends DetectionStrategy {
  detect() {
    const authKeys = [
      'authToken', 'accessToken', 'sessionId', 
      'userId', 'userToken', 'jwt'
    ];
    
    let found = false;
    
    for (const key of authKeys) {
      if (localStorage.getItem(key) || sessionStorage.getItem(key)) {
        found = true;
        break;
      }
    }
    
    // Check for JSON objects containing auth
    const allKeys = Object.keys(localStorage).concat(Object.keys(sessionStorage));
    for (const key of allKeys) {
      try {
        const value = localStorage.getItem(key) || sessionStorage.getItem(key);
        if (value && value.includes('token') || value.includes('auth')) {
          found = true;
          break;
        }
      } catch (e) {
        // Continue
      }
    }
    
    return {
      score: found ? 1 : 0,
      weight: 0.8
    };
  }
}

/**
 * Cookie detection strategy
 */
class CookieDetectionStrategy extends DetectionStrategy {
  detect() {
    const authPatterns = [
      'session', 'auth', 'token', 'logged', 'user'
    ];
    
    const cookies = document.cookie.toLowerCase();
    let found = false;
    
    for (const pattern of authPatterns) {
      if (cookies.includes(pattern)) {
        found = true;
        break;
      }
    }
    
    return {
      score: found ? 1 : 0,
      weight: 0.7
    };
  }
}

/**
 * Network request detection strategy
 */
class NetworkDetectionStrategy extends DetectionStrategy {
  detect() {
    // Check if fetch/XHR has auth headers
    let hasAuth = false;
    
    try {
      // Intercept fetch to check for auth headers
      const originalFetch = window.fetch;
      if (originalFetch._intercepted) {
        hasAuth = originalFetch._hasAuth || false;
      }
    } catch (e) {
      // Continue
    }
    
    return {
      score: hasAuth ? 1 : 0,
      weight: 0.6
    };
  }
}

/**
 * React state detection strategy
 */
class ReactDetectionStrategy extends DetectionStrategy {
  detect() {
    let hasUserState = false;
    
    try {
      // Check React DevTools
      if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
        // Look for user-related state
        const reactRoot = document.querySelector('#root');
        if (reactRoot && reactRoot._reactRootContainer) {
          hasUserState = true;
        }
      }
    } catch (e) {
      // React not present
    }
    
    return {
      score: hasUserState ? 1 : 0,
      weight: 0.5
    };
  }
}

/**
 * GraphQL cache detection strategy
 */
class GraphQLDetectionStrategy extends DetectionStrategy {
  detect() {
    let hasAuth = false;
    
    try {
      // Check Apollo Client cache
      if (window.__APOLLO_CLIENT__) {
        const cache = window.__APOLLO_CLIENT__.cache;
        if (cache && cache.data && cache.data.data) {
          const data = cache.data.data;
          if (data.ROOT_QUERY && (data.ROOT_QUERY.viewer || data.ROOT_QUERY.currentUser)) {
            hasAuth = true;
          }
        }
      }
    } catch (e) {
      // GraphQL not present
    }
    
    return {
      score: hasAuth ? 1 : 0,
      weight: 0.5
    };
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MLLoginDetector;
} else if (typeof window !== 'undefined') {
  window.MLLoginDetector = MLLoginDetector;
}