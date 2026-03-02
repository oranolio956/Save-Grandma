// seeking-extension/service-worker.js

// Store for tracking activity across tabs
let tabActivity = {};
let globalSettings = {
  enabled: true,
  autoSimulate: true,
  debugMode: false
};

// Initialize settings on install
chrome.runtime.onInstalled.addListener(() => {
  console.log('[Service Worker] Extension installed');
  
  // Set default settings
  chrome.storage.sync.set({
    enabled: true,
    autoSimulate: true,
    debugMode: false,
    installDate: new Date().toISOString()
  });
  
  // Create context menu items
  chrome.contextMenus.create({
    id: 'toggle-extension',
    title: 'Toggle Seeking Extension',
    contexts: ['page']
  });
});

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  const tabId = sender.tab?.id;
  const url = sender.tab?.url;
  
  console.log('[Service Worker] Message received:', request.action, 'from tab:', tabId);
  
  switch (request.action) {
    case 'content_loaded':
      // Track when content script loads
      tabActivity[tabId] = {
        url: request.url,
        loadTime: request.timestamp,
        status: 'loaded'
      };
      sendResponse({ status: 'acknowledged' });
      break;
      
    case 'login_status':
      // Track login status
      if (tabActivity[tabId]) {
        tabActivity[tabId].loggedIn = request.loggedIn;
      }
      console.log('[Service Worker] Login status:', request.loggedIn, 'for', url);
      sendResponse({ status: 'recorded' });
      break;
      
    case 'simulation_complete':
      // Track simulation completion
      if (tabActivity[tabId]) {
        tabActivity[tabId].simulated = true;
        tabActivity[tabId].simulationTime = new Date().toISOString();
      }
      console.log('[Service Worker] Simulation completed for', url);
      
      // Optional: Show notification
      if (globalSettings.debugMode) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icon48.png',
          title: 'Seeking Extension',
          message: 'Enter key simulated successfully'
        });
      }
      sendResponse({ status: 'success' });
      break;
      
    case 'get_settings':
      // Provide current settings
      chrome.storage.sync.get(['enabled', 'autoSimulate', 'debugMode'], (result) => {
        globalSettings = { ...globalSettings, ...result };
        sendResponse(globalSettings);
      });
      return true; // Keep channel open for async response
      
    case 'update_settings':
      // Update settings
      if (request.settings) {
        chrome.storage.sync.set(request.settings, () => {
          globalSettings = { ...globalSettings, ...request.settings };
          sendResponse({ status: 'updated', settings: globalSettings });
        });
        return true;
      }
      break;
      
    case 'get_activity':
      // Provide activity log
      sendResponse({ 
        activity: tabActivity,
        currentTab: tabId 
      });
      break;
      
    case 'clear_activity':
      // Clear activity log
      tabActivity = {};
      sendResponse({ status: 'cleared' });
      break;
      
    case 'log':
      // Simple logging
      console.log('[Content Script Log]:', request.message);
      sendResponse({ status: 'logged' });
      break;
      
    default:
      console.warn('[Service Worker] Unknown action:', request.action);
      sendResponse({ status: 'unknown_action' });
  }
  
  return false; // Synchronous response
});

// Handle tab events
chrome.tabs.onRemoved.addListener((tabId) => {
  // Clean up activity for closed tabs
  if (tabActivity[tabId]) {
    delete tabActivity[tabId];
    console.log('[Service Worker] Cleaned up activity for tab:', tabId);
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // Reset activity when navigating to new page
  if (changeInfo.status === 'loading' && tabActivity[tabId]) {
    tabActivity[tabId] = {
      url: tab.url,
      loadTime: new Date().toISOString(),
      status: 'loading'
    };
  }
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'toggle-extension') {
    globalSettings.enabled = !globalSettings.enabled;
    chrome.storage.sync.set({ enabled: globalSettings.enabled }, () => {
      // Notify all content scripts
      chrome.tabs.query({}, (tabs) => {
        tabs.forEach(tab => {
          if (tab.url && tab.url.includes('seeking.com')) {
            chrome.tabs.sendMessage(tab.id, { 
              action: 'toggle',
              enabled: globalSettings.enabled 
            });
          }
        });
      });
      
      // Show notification
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon48.png',
        title: 'Seeking Extension',
        message: `Extension ${globalSettings.enabled ? 'enabled' : 'disabled'}`
      });
    });
  }
});

// Periodic cleanup (every hour)
setInterval(() => {
  const oneHourAgo = Date.now() - (60 * 60 * 1000);
  
  Object.keys(tabActivity).forEach(tabId => {
    const activity = tabActivity[tabId];
    if (activity.loadTime) {
      const loadTime = new Date(activity.loadTime).getTime();
      if (loadTime < oneHourAgo) {
        delete tabActivity[tabId];
        console.log('[Service Worker] Cleaned up stale activity for tab:', tabId);
      }
    }
  });
}, 3600000); // 1 hour

// Handle extension icon click (when popup is not set)
chrome.action.onClicked.addListener((tab) => {
  // This only works if default_popup is not set in manifest
  console.log('[Service Worker] Extension icon clicked');
});

// Export for debugging (accessible via chrome.extension.getBackgroundPage())
if (typeof window !== 'undefined') {
  window.debugInfo = {
    getActivity: () => tabActivity,
    getSettings: () => globalSettings,
    clearActivity: () => { tabActivity = {}; }
  };
}

console.log('[Service Worker] Initialized successfully');