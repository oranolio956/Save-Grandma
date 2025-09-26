// Background service worker for Chrome extension
console.log('[SCA Background] Service worker initialized');

// Initialize default settings on install
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('[SCA Background] Extension installed, setting defaults');
    
    // Set default configuration
    const defaultConfig = {
      isActive: false,
      config: {
        templates: [
          "That's interesting! Tell me more about that.",
          "I'd love to hear more about your thoughts on this!",
          "Thanks for sharing! What else is on your mind?",
          "That sounds great! How long have you been interested in that?",
          "Fascinating! What do you enjoy most about it?"
        ],
        keywords: {
          "hello": "Hi there! How are you doing today?",
          "hi": "Hey! Nice to hear from you 😊",
          "how are you": "I'm doing great, thanks for asking! How about you?",
          "meet": "That sounds interesting! When were you thinking?",
          "coffee": "Coffee sounds perfect! What's your favorite spot?",
          "dinner": "Dinner would be lovely! Do you have a place in mind?",
          "weekend": "Weekends are great for me! What did you have in mind?"
        },
        blockedKeywords: [],
        responseDelay: 5000,
        checkInterval: 3000,
        maxConversations: 1,
        useEmojis: true,
        logMessages: true
      },
      stats: {
        messagesRead: 0,
        messagesSent: 0,
        activeChats: 0
      },
      messageLogs: []
    };
    
    chrome.storage.local.set(defaultConfig, () => {
      console.log('[SCA Background] Default configuration saved');
    });
    
    // Open welcome page or instructions
    chrome.tabs.create({
      url: chrome.runtime.getURL('welcome.html')
    });
  }
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('[SCA Background] Received message:', request);
  
  switch (request.action) {
    case 'updateStats':
      updateStats(request.stats);
      sendResponse({ success: true });
      break;
      
    case 'logMessage':
      logMessage(request.log);
      sendResponse({ success: true });
      break;
      
    case 'getConfig':
      chrome.storage.local.get(['config'], (result) => {
        sendResponse(result.config || {});
      });
      return true; // Keep message channel open
      
    default:
      sendResponse({ success: false, message: 'Unknown action' });
  }
});

// Update statistics
function updateStats(newStats) {
  chrome.storage.local.get(['stats'], (result) => {
    const stats = result.stats || {
      messagesRead: 0,
      messagesSent: 0,
      activeChats: 0
    };
    
    // Merge new stats
    Object.assign(stats, newStats);
    
    chrome.storage.local.set({ stats }, () => {
      console.log('[SCA Background] Stats updated:', stats);
    });
  });
}

// Log message
function logMessage(log) {
  chrome.storage.local.get(['messageLogs', 'config'], (result) => {
    const config = result.config || {};
    
    if (config.logMessages) {
      const logs = result.messageLogs || [];
      logs.push(log);
      
      // Keep only last 500 logs to prevent storage overflow
      if (logs.length > 500) {
        logs.splice(0, logs.length - 500);
      }
      
      chrome.storage.local.set({ messageLogs: logs }, () => {
        console.log('[SCA Background] Message logged');
      });
    }
  });
}

// Handle extension icon click (backup for popup)
chrome.action.onClicked.addListener((tab) => {
  // This only fires if there's no popup defined
  // Can be used for quick toggle functionality
  chrome.storage.local.get(['isActive'], (result) => {
    const newState = !result.isActive;
    chrome.storage.local.set({ isActive: newState });
    
    // Send message to content script
    chrome.tabs.sendMessage(tab.id, {
      action: 'toggle',
      isActive: newState
    });
  });
});

// Monitor for Seeking.com tabs
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    if (tab.url.includes('seeking.com')) {
      console.log('[SCA Background] Seeking.com tab detected:', tab.url);
      
      // Inject content script if needed (backup injection)
      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['content.js']
      }).catch(err => {
        // Script might already be injected
        console.log('[SCA Background] Script injection skipped:', err.message);
      });
    }
  }
});

// Periodic cleanup of old logs (runs every hour)
setInterval(() => {
  chrome.storage.local.get(['messageLogs'], (result) => {
    const logs = result.messageLogs || [];
    const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
    
    // Remove logs older than 24 hours
    const recentLogs = logs.filter(log => {
      const logTime = new Date(log.timestamp).getTime();
      return logTime > oneDayAgo;
    });
    
    if (recentLogs.length < logs.length) {
      chrome.storage.local.set({ messageLogs: recentLogs }, () => {
        console.log(`[SCA Background] Cleaned up ${logs.length - recentLogs.length} old logs`);
      });
    }
  });
}, 60 * 60 * 1000); // Every hour