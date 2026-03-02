/**
 * Service Worker with Complete State Machine Implementation
 * Full background processing and orchestration
 */

// State Machine Implementation
class ExtensionStateMachine {
  constructor() {
    this.states = {
      IDLE: 'idle',
      INITIALIZING: 'initializing',
      DETECTING: 'detecting', 
      SIMULATING: 'simulating',
      COMPLETED: 'completed',
      ERROR: 'error',
      DISABLED: 'disabled'
    };
    
    this.currentState = this.states.IDLE;
    this.stateHistory = [];
    this.maxHistorySize = 100;
    
    // Define valid transitions
    this.transitions = new Map([
      // From IDLE
      [`${this.states.IDLE}:initialize`, this.states.INITIALIZING],
      [`${this.states.IDLE}:detect`, this.states.DETECTING],
      [`${this.states.IDLE}:disable`, this.states.DISABLED],
      
      // From INITIALIZING  
      [`${this.states.INITIALIZING}:ready`, this.states.IDLE],
      [`${this.states.INITIALIZING}:error`, this.states.ERROR],
      
      // From DETECTING
      [`${this.states.DETECTING}:found`, this.states.SIMULATING],
      [`${this.states.DETECTING}:notfound`, this.states.IDLE],
      [`${this.states.DETECTING}:error`, this.states.ERROR],
      
      // From SIMULATING
      [`${this.states.SIMULATING}:success`, this.states.COMPLETED],
      [`${this.states.SIMULATING}:failure`, this.states.ERROR],
      
      // From COMPLETED
      [`${this.states.COMPLETED}:reset`, this.states.IDLE],
      [`${this.states.COMPLETED}:detect`, this.states.DETECTING],
      
      // From ERROR
      [`${this.states.ERROR}:retry`, this.states.DETECTING],
      [`${this.states.ERROR}:reset`, this.states.IDLE],
      
      // From DISABLED
      [`${this.states.DISABLED}:enable`, this.states.IDLE]
    ]);
    
    // State handlers
    this.stateHandlers = new Map([
      [this.states.IDLE, this.handleIdleState.bind(this)],
      [this.states.INITIALIZING, this.handleInitializingState.bind(this)],
      [this.states.DETECTING, this.handleDetectingState.bind(this)],
      [this.states.SIMULATING, this.handleSimulatingState.bind(this)],
      [this.states.COMPLETED, this.handleCompletedState.bind(this)],
      [this.states.ERROR, this.handleErrorState.bind(this)],
      [this.states.DISABLED, this.handleDisabledState.bind(this)]
    ]);
  }
  
  /**
   * Transition to new state
   */
  transition(action, data = {}) {
    const key = `${this.currentState}:${action}`;
    const nextState = this.transitions.get(key);
    
    if (!nextState) {
      console.warn(`Invalid transition attempted: ${key}`);
      return false;
    }
    
    // Record transition
    this.recordTransition(this.currentState, nextState, action, data);
    
    // Update state
    const previousState = this.currentState;
    this.currentState = nextState;
    
    // Execute state handler
    const handler = this.stateHandlers.get(nextState);
    if (handler) {
      handler(data, previousState);
    }
    
    // Notify listeners
    this.notifyStateChange(nextState, previousState, data);
    
    return true;
  }
  
  /**
   * Record state transition
   */
  recordTransition(from, to, action, data) {
    const transition = {
      from,
      to,
      action,
      data,
      timestamp: Date.now()
    };
    
    this.stateHistory.push(transition);
    
    // Trim history if too large
    if (this.stateHistory.length > this.maxHistorySize) {
      this.stateHistory.shift();
    }
  }
  
  /**
   * State handlers
   */
  handleIdleState(data) {
    console.log('[State Machine] Entered IDLE state');
  }
  
  handleInitializingState(data) {
    console.log('[State Machine] Entered INITIALIZING state');
  }
  
  handleDetectingState(data) {
    console.log('[State Machine] Entered DETECTING state');
  }
  
  handleSimulatingState(data) {
    console.log('[State Machine] Entered SIMULATING state');
  }
  
  handleCompletedState(data) {
    console.log('[State Machine] Entered COMPLETED state');
  }
  
  handleErrorState(data) {
    console.log('[State Machine] Entered ERROR state:', data.error);
  }
  
  handleDisabledState(data) {
    console.log('[State Machine] Entered DISABLED state');
  }
  
  /**
   * Notify all tabs about state change
   */
  async notifyStateChange(newState, previousState, data) {
    const tabs = await chrome.tabs.query({ url: "*://*.seeking.com/*" });
    
    for (const tab of tabs) {
      chrome.tabs.sendMessage(tab.id, {
        action: 'state_changed',
        newState,
        previousState,
        data
      }).catch(() => {
        // Tab might not have content script loaded
      });
    }
  }
  
  /**
   * Get current state
   */
  getCurrentState() {
    return this.currentState;
  }
  
  /**
   * Get state history
   */
  getHistory() {
    return this.stateHistory;
  }
  
  /**
   * Reset state machine
   */
  reset() {
    this.currentState = this.states.IDLE;
    this.stateHistory = [];
  }
}

// Analytics System
class AnalyticsSystem {
  constructor() {
    this.events = [];
    this.sessions = new Map();
    this.metrics = {
      totalEvents: 0,
      totalSessions: 0,
      successfulSimulations: 0,
      failedSimulations: 0,
      detectionAccuracy: { correct: 0, total: 0 },
      averageSessionDuration: 0
    };
    
    this.initializeAnalytics();
  }
  
  /**
   * Initialize analytics
   */
  async initializeAnalytics() {
    // Load existing metrics
    const stored = await chrome.storage.local.get('analytics');
    if (stored.analytics) {
      this.metrics = { ...this.metrics, ...stored.analytics };
    }
    
    // Start periodic save
    setInterval(() => {
      this.saveAnalytics();
    }, 60000); // Save every minute
  }
  
  /**
   * Track event
   */
  trackEvent(eventName, properties = {}) {
    const event = {
      name: eventName,
      properties,
      timestamp: Date.now(),
      sessionId: properties.sessionId || 'unknown',
      tabId: properties.tabId || null,
      url: properties.url || null
    };
    
    this.events.push(event);
    this.metrics.totalEvents++;
    
    // Process specific events
    this.processEvent(event);
    
    // Trim events if too many
    if (this.events.length > 1000) {
      this.events = this.events.slice(-500);
    }
  }
  
  /**
   * Process specific event types
   */
  processEvent(event) {
    switch (event.name) {
      case 'session_start':
        this.startSession(event.sessionId, event);
        break;
        
      case 'session_end':
        this.endSession(event.sessionId, event);
        break;
        
      case 'simulation_success':
        this.metrics.successfulSimulations++;
        break;
        
      case 'simulation_failure':
        this.metrics.failedSimulations++;
        break;
        
      case 'detection_feedback':
        if (event.properties.correct) {
          this.metrics.detectionAccuracy.correct++;
        }
        this.metrics.detectionAccuracy.total++;
        break;
    }
  }
  
  /**
   * Start session tracking
   */
  startSession(sessionId, event) {
    this.sessions.set(sessionId, {
      startTime: event.timestamp,
      events: [event],
      tabId: event.tabId,
      url: event.url
    });
    
    this.metrics.totalSessions++;
  }
  
  /**
   * End session tracking
   */
  endSession(sessionId, event) {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.endTime = event.timestamp;
      session.duration = session.endTime - session.startTime;
      
      // Update average duration
      const allDurations = Array.from(this.sessions.values())
        .filter(s => s.duration)
        .map(s => s.duration);
      
      if (allDurations.length > 0) {
        this.metrics.averageSessionDuration = 
          allDurations.reduce((a, b) => a + b, 0) / allDurations.length;
      }
    }
  }
  
  /**
   * Get analytics report
   */
  getReport() {
    const successRate = this.metrics.successfulSimulations / 
      (this.metrics.successfulSimulations + this.metrics.failedSimulations) || 0;
    
    const accuracy = this.metrics.detectionAccuracy.total > 0
      ? this.metrics.detectionAccuracy.correct / this.metrics.detectionAccuracy.total
      : 0;
    
    return {
      ...this.metrics,
      successRate: (successRate * 100).toFixed(2) + '%',
      detectionAccuracy: (accuracy * 100).toFixed(2) + '%',
      averageSessionDuration: this.formatDuration(this.metrics.averageSessionDuration),
      recentEvents: this.events.slice(-20)
    };
  }
  
  /**
   * Format duration
   */
  formatDuration(ms) {
    if (ms < 1000) return ms + 'ms';
    if (ms < 60000) return (ms / 1000).toFixed(1) + 's';
    if (ms < 3600000) return (ms / 60000).toFixed(1) + 'm';
    return (ms / 3600000).toFixed(1) + 'h';
  }
  
  /**
   * Save analytics to storage
   */
  async saveAnalytics() {
    await chrome.storage.local.set({
      analytics: this.metrics
    });
  }
}

// Tab Manager
class TabManager {
  constructor() {
    this.tabs = new Map();
    this.setupListeners();
  }
  
  /**
   * Setup tab listeners
   */
  setupListeners() {
    // Tab created
    chrome.tabs.onCreated.addListener((tab) => {
      if (this.isSeekingTab(tab)) {
        this.registerTab(tab);
      }
    });
    
    // Tab updated
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete' && this.isSeekingTab(tab)) {
        this.updateTab(tabId, tab);
      }
    });
    
    // Tab removed
    chrome.tabs.onRemoved.addListener((tabId) => {
      this.unregisterTab(tabId);
    });
    
    // Tab activated
    chrome.tabs.onActivated.addListener(async (activeInfo) => {
      const tab = await chrome.tabs.get(activeInfo.tabId);
      if (this.isSeekingTab(tab)) {
        this.setActiveTab(activeInfo.tabId);
      }
    });
  }
  
  /**
   * Check if tab is Seeking.com
   */
  isSeekingTab(tab) {
    return tab.url && (
      tab.url.includes('seeking.com') ||
      tab.url.includes('seekingarrangement.com')
    );
  }
  
  /**
   * Register tab
   */
  registerTab(tab) {
    this.tabs.set(tab.id, {
      id: tab.id,
      url: tab.url,
      title: tab.title,
      status: 'registered',
      state: 'idle',
      hasContentScript: false,
      lastActivity: Date.now()
    });
    
    console.log(`[Tab Manager] Registered tab ${tab.id}: ${tab.url}`);
  }
  
  /**
   * Update tab info
   */
  updateTab(tabId, tab) {
    const tabInfo = this.tabs.get(tabId) || {};
    
    this.tabs.set(tabId, {
      ...tabInfo,
      id: tab.id,
      url: tab.url,
      title: tab.title,
      lastActivity: Date.now()
    });
  }
  
  /**
   * Unregister tab
   */
  unregisterTab(tabId) {
    this.tabs.delete(tabId);
    console.log(`[Tab Manager] Unregistered tab ${tabId}`);
  }
  
  /**
   * Set active tab
   */
  setActiveTab(tabId) {
    const tabInfo = this.tabs.get(tabId);
    if (tabInfo) {
      tabInfo.isActive = true;
      tabInfo.lastActivity = Date.now();
    }
    
    // Mark other tabs as inactive
    for (const [id, info] of this.tabs.entries()) {
      if (id !== tabId) {
        info.isActive = false;
      }
    }
  }
  
  /**
   * Get tab info
   */
  getTabInfo(tabId) {
    return this.tabs.get(tabId);
  }
  
  /**
   * Get all tabs
   */
  getAllTabs() {
    return Array.from(this.tabs.values());
  }
}

// Main Service Worker Controller
class ServiceWorkerController {
  constructor() {
    this.stateMachine = new ExtensionStateMachine();
    this.analytics = new AnalyticsSystem();
    this.tabManager = new TabManager();
    
    this.settings = {
      enabled: true,
      autoSimulate: true,
      debugMode: false
    };
    
    this.initialize();
  }
  
  /**
   * Initialize service worker
   */
  async initialize() {
    console.log('[Service Worker] Initializing...');
    
    // Load settings
    await this.loadSettings();
    
    // Setup listeners
    this.setupListeners();
    
    // Setup alarms for periodic tasks
    this.setupAlarms();
    
    // Setup context menus
    this.setupContextMenus();
    
    // Setup commands
    this.setupCommands();
    
    console.log('[Service Worker] Initialization complete');
  }
  
  /**
   * Load settings from storage
   */
  async loadSettings() {
    const stored = await chrome.storage.sync.get([
      'enabled', 'autoSimulate', 'debugMode'
    ]);
    
    this.settings = { ...this.settings, ...stored };
    
    // Apply initial state
    if (!this.settings.enabled) {
      this.stateMachine.transition('disable');
    }
  }
  
  /**
   * Setup message listeners
   */
  setupListeners() {
    // Message from content scripts
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      this.handleMessage(request, sender, sendResponse);
      return true; // Keep channel open
    });
    
    // Extension installed/updated
    chrome.runtime.onInstalled.addListener((details) => {
      this.handleInstalled(details);
    });
    
    // Browser started
    chrome.runtime.onStartup.addListener(() => {
      this.handleStartup();
    });
  }
  
  /**
   * Handle messages
   */
  async handleMessage(request, sender, sendResponse) {
    const tabId = sender.tab?.id;
    const url = sender.tab?.url;
    
    if (this.settings.debugMode) {
      console.log(`[Service Worker] Message from tab ${tabId}:`, request.action);
    }
    
    // Track event
    this.analytics.trackEvent(request.action, {
      ...request.data,
      tabId,
      url
    });
    
    switch (request.action) {
      case 'initialized':
        this.handleContentScriptInitialized(tabId, request.data);
        sendResponse({ status: 'acknowledged' });
        break;
        
      case 'detection_complete':
        this.handleDetectionComplete(tabId, request.data);
        sendResponse({ status: 'acknowledged' });
        break;
        
      case 'simulation_complete':
        this.handleSimulationComplete(tabId, request.data);
        sendResponse({ status: 'acknowledged' });
        break;
        
      case 'get_tab_id':
        sendResponse({ tabId });
        break;
        
      case 'toggle':
        this.handleToggle(request.data);
        sendResponse({ status: 'toggled' });
        break;
        
      case 'error':
        this.handleError(tabId, request.data);
        sendResponse({ status: 'logged' });
        break;
        
      case 'get_analytics':
        sendResponse(this.analytics.getReport());
        break;
        
      case 'get_state':
        sendResponse({
          state: this.stateMachine.getCurrentState(),
          history: this.stateMachine.getHistory()
        });
        break;
        
      default:
        sendResponse({ error: 'Unknown action' });
    }
  }
  
  /**
   * Handle content script initialized
   */
  handleContentScriptInitialized(tabId, data) {
    // Update tab info
    const tabInfo = this.tabManager.getTabInfo(tabId);
    if (tabInfo) {
      tabInfo.hasContentScript = true;
      tabInfo.sessionId = data.sessionId;
    }
    
    // Transition state
    this.stateMachine.transition('initialize', { tabId, ...data });
    
    // Track session start
    this.analytics.trackEvent('session_start', {
      sessionId: data.sessionId,
      tabId,
      url: data.url
    });
  }
  
  /**
   * Handle detection complete
   */
  handleDetectionComplete(tabId, data) {
    // Update tab state
    const tabInfo = this.tabManager.getTabInfo(tabId);
    if (tabInfo) {
      tabInfo.state = data.isLoggedIn ? 'logged_in' : 'not_logged_in';
      tabInfo.confidence = data.confidence;
    }
    
    // Transition state
    if (data.isLoggedIn) {
      this.stateMachine.transition('found', { tabId, ...data });
    } else {
      this.stateMachine.transition('notfound', { tabId, ...data });
    }
  }
  
  /**
   * Handle simulation complete
   */
  handleSimulationComplete(tabId, data) {
    // Update tab state
    const tabInfo = this.tabManager.getTabInfo(tabId);
    if (tabInfo) {
      tabInfo.state = data.success ? 'simulated' : 'simulation_failed';
    }
    
    // Transition state
    if (data.success) {
      this.stateMachine.transition('success', { tabId, ...data });
      this.analytics.trackEvent('simulation_success', { tabId, ...data });
    } else {
      this.stateMachine.transition('failure', { tabId, ...data });
      this.analytics.trackEvent('simulation_failure', { tabId, ...data });
    }
    
    // Show notification if debug mode
    if (this.settings.debugMode) {
      this.showNotification(
        data.success ? 'Simulation Successful' : 'Simulation Failed',
        data.success 
          ? `Enter key simulated in ${data.time}ms`
          : 'Failed to simulate Enter key'
      );
    }
  }
  
  /**
   * Handle toggle
   */
  handleToggle(data) {
    this.settings.enabled = data.enabled;
    
    if (data.enabled) {
      this.stateMachine.transition('enable');
    } else {
      this.stateMachine.transition('disable');
    }
    
    // Save setting
    chrome.storage.sync.set({ enabled: data.enabled });
    
    // Notify all tabs
    this.broadcastToTabs('toggle', { enabled: data.enabled });
  }
  
  /**
   * Handle error
   */
  handleError(tabId, data) {
    console.error(`[Service Worker] Error from tab ${tabId}:`, data);
    
    // Transition to error state
    this.stateMachine.transition('error', { tabId, ...data });
    
    // Track error
    this.analytics.trackEvent('error', { tabId, ...data });
  }
  
  /**
   * Setup alarms for periodic tasks
   */
  setupAlarms() {
    // Cleanup alarm (every hour)
    chrome.alarms.create('cleanup', { periodInMinutes: 60 });
    
    // Analytics save (every 5 minutes)
    chrome.alarms.create('save_analytics', { periodInMinutes: 5 });
    
    // Health check (every 30 minutes)
    chrome.alarms.create('health_check', { periodInMinutes: 30 });
    
    chrome.alarms.onAlarm.addListener((alarm) => {
      switch (alarm.name) {
        case 'cleanup':
          this.performCleanup();
          break;
          
        case 'save_analytics':
          this.analytics.saveAnalytics();
          break;
          
        case 'health_check':
          this.performHealthCheck();
          break;
      }
    });
  }
  
  /**
   * Setup context menus
   */
  setupContextMenus() {
    // Toggle extension
    chrome.contextMenus.create({
      id: 'toggle_extension',
      title: 'Toggle Seeking Extension',
      contexts: ['page'],
      documentUrlPatterns: ['*://*.seeking.com/*']
    });
    
    // Manual simulation
    chrome.contextMenus.create({
      id: 'manual_simulation',
      title: 'Simulate Enter Key',
      contexts: ['page'],
      documentUrlPatterns: ['*://*.seeking.com/*']
    });
    
    // Show analytics
    chrome.contextMenus.create({
      id: 'show_analytics',
      title: 'Show Analytics',
      contexts: ['page'],
      documentUrlPatterns: ['*://*.seeking.com/*']
    });
    
    chrome.contextMenus.onClicked.addListener((info, tab) => {
      this.handleContextMenu(info, tab);
    });
  }
  
  /**
   * Handle context menu clicks
   */
  handleContextMenu(info, tab) {
    switch (info.menuItemId) {
      case 'toggle_extension':
        this.settings.enabled = !this.settings.enabled;
        this.handleToggle({ enabled: this.settings.enabled });
        break;
        
      case 'manual_simulation':
        chrome.tabs.sendMessage(tab.id, { action: 'simulate' });
        break;
        
      case 'show_analytics':
        const report = this.analytics.getReport();
        console.log('Analytics Report:', report);
        this.showNotification('Analytics', 
          `Success Rate: ${report.successRate}\n` +
          `Detection Accuracy: ${report.detectionAccuracy}`
        );
        break;
    }
  }
  
  /**
   * Setup keyboard commands
   */
  setupCommands() {
    chrome.commands.onCommand.addListener((command) => {
      switch (command) {
        case 'toggle-extension':
          this.settings.enabled = !this.settings.enabled;
          this.handleToggle({ enabled: this.settings.enabled });
          break;
          
        case 'simulate-enter':
          this.broadcastToTabs('simulate', {});
          break;
      }
    });
  }
  
  /**
   * Handle extension installed/updated
   */
  handleInstalled(details) {
    if (details.reason === 'install') {
      console.log('[Service Worker] Extension installed');
      
      // Set default settings
      chrome.storage.sync.set({
        enabled: true,
        autoSimulate: true,
        debugMode: false,
        installDate: Date.now()
      });
      
      // Open welcome page
      chrome.tabs.create({
        url: chrome.runtime.getURL('src/welcome.html')
      });
      
    } else if (details.reason === 'update') {
      console.log('[Service Worker] Extension updated to version', 
        chrome.runtime.getManifest().version);
      
      // Migrate settings if needed
      this.migrateSettings();
    }
  }
  
  /**
   * Handle browser startup
   */
  handleStartup() {
    console.log('[Service Worker] Browser started');
    this.initialize();
  }
  
  /**
   * Migrate settings from old versions
   */
  async migrateSettings() {
    // Check for old settings format and migrate if needed
    const oldSettings = await chrome.storage.local.get(null);
    
    if (oldSettings.extension_enabled !== undefined) {
      // Migrate from old format
      await chrome.storage.sync.set({
        enabled: oldSettings.extension_enabled,
        autoSimulate: oldSettings.auto_simulate || true,
        debugMode: oldSettings.debug_mode || false
      });
      
      // Remove old settings
      await chrome.storage.local.remove([
        'extension_enabled', 'auto_simulate', 'debug_mode'
      ]);
      
      console.log('[Service Worker] Settings migrated');
    }
  }
  
  /**
   * Perform cleanup tasks
   */
  performCleanup() {
    console.log('[Service Worker] Performing cleanup');
    
    // Clean old analytics events
    if (this.analytics.events.length > 1000) {
      this.analytics.events = this.analytics.events.slice(-500);
    }
    
    // Clean old sessions
    const oneDayAgo = Date.now() - 86400000;
    for (const [sessionId, session] of this.analytics.sessions.entries()) {
      if (session.startTime < oneDayAgo) {
        this.analytics.sessions.delete(sessionId);
      }
    }
    
    // Clean inactive tabs
    const oneHourAgo = Date.now() - 3600000;
    for (const [tabId, info] of this.tabManager.tabs.entries()) {
      if (info.lastActivity < oneHourAgo) {
        this.tabManager.unregisterTab(tabId);
      }
    }
  }
  
  /**
   * Perform health check
   */
  async performHealthCheck() {
    console.log('[Service Worker] Performing health check');
    
    // Check all registered tabs
    for (const [tabId, info] of this.tabManager.tabs.entries()) {
      try {
        // Try to ping tab
        await chrome.tabs.sendMessage(tabId, { action: 'ping' });
      } catch (error) {
        // Tab is not responding, remove it
        this.tabManager.unregisterTab(tabId);
      }
    }
    
    // Check state machine
    const currentState = this.stateMachine.getCurrentState();
    console.log(`[Service Worker] Current state: ${currentState}`);
    
    // Check analytics
    const report = this.analytics.getReport();
    console.log(`[Service Worker] Total events: ${report.totalEvents}`);
  }
  
  /**
   * Broadcast message to all tabs
   */
  async broadcastToTabs(action, data) {
    const tabs = await chrome.tabs.query({ url: "*://*.seeking.com/*" });
    
    for (const tab of tabs) {
      chrome.tabs.sendMessage(tab.id, { action, ...data })
        .catch(() => {
          // Tab might not have content script
        });
    }
  }
  
  /**
   * Show notification
   */
  showNotification(title, message) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: chrome.runtime.getURL('assets/icons/icon128.png'),
      title: title,
      message: message
    });
  }
}

// Initialize service worker
const controller = new ServiceWorkerController();

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ServiceWorkerController, ExtensionStateMachine, AnalyticsSystem };
}