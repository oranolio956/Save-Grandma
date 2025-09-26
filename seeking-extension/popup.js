// seeking-extension/popup.js

// DOM elements
const elements = {
  extensionStatus: document.getElementById('extensionStatus'),
  loginStatus: document.getElementById('loginStatus'),
  simulationStatus: document.getElementById('simulationStatus'),
  enableToggle: document.getElementById('enableToggle'),
  autoSimToggle: document.getElementById('autoSimToggle'),
  debugToggle: document.getElementById('debugToggle'),
  simulateBtn: document.getElementById('simulateBtn'),
  refreshBtn: document.getElementById('refreshBtn'),
  clearBtn: document.getElementById('clearBtn'),
  activityList: document.getElementById('activityList')
};

// State
let currentTab = null;
let settings = {
  enabled: true,
  autoSimulate: true,
  debugMode: false
};

// Initialize popup
async function init() {
  // Get current tab
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTab = tabs[0];
  
  // Load settings from storage
  await loadSettings();
  
  // Update UI based on current tab
  await updateStatus();
  
  // Load activity log
  await loadActivity();
  
  // Setup event listeners
  setupEventListeners();
}

// Load settings from storage
async function loadSettings() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(['enabled', 'autoSimulate', 'debugMode'], (result) => {
      settings = {
        enabled: result.enabled !== false,
        autoSimulate: result.autoSimulate !== false,
        debugMode: result.debugMode === true
      };
      
      // Update toggles
      elements.enableToggle.checked = settings.enabled;
      elements.autoSimToggle.checked = settings.autoSimulate;
      elements.debugToggle.checked = settings.debugMode;
      
      resolve();
    });
  });
}

// Update status display
async function updateStatus() {
  // Update extension status
  if (settings.enabled) {
    elements.extensionStatus.textContent = 'Active';
    elements.extensionStatus.className = 'status-value active';
  } else {
    elements.extensionStatus.textContent = 'Disabled';
    elements.extensionStatus.className = 'status-value inactive';
  }
  
  // Check if we're on a Seeking.com page
  if (currentTab && currentTab.url && currentTab.url.includes('seeking.com')) {
    // Query content script for status
    try {
      const response = await chrome.tabs.sendMessage(currentTab.id, { action: 'check_status' });
      
      if (response) {
        // Update login status
        if (response.loggedIn) {
          elements.loginStatus.textContent = 'Logged In';
          elements.loginStatus.className = 'status-value logged-in';
        } else {
          elements.loginStatus.textContent = 'Not Logged In';
          elements.loginStatus.className = 'status-value not-logged-in';
        }
        
        // Update simulation status
        if (response.hasSimulated) {
          elements.simulationStatus.textContent = 'Completed';
          elements.simulationStatus.className = 'status-value active';
        } else {
          elements.simulationStatus.textContent = 'Pending';
          elements.simulationStatus.className = 'status-value inactive';
        }
      }
    } catch (error) {
      console.error('Failed to get status from content script:', error);
      elements.loginStatus.textContent = 'Unknown';
      elements.loginStatus.className = 'status-value inactive';
      elements.simulationStatus.textContent = 'N/A';
      elements.simulationStatus.className = 'status-value inactive';
    }
  } else {
    elements.loginStatus.textContent = 'Not on Seeking.com';
    elements.loginStatus.className = 'status-value inactive';
    elements.simulationStatus.textContent = 'N/A';
    elements.simulationStatus.className = 'status-value inactive';
  }
}

// Load activity log
async function loadActivity() {
  chrome.runtime.sendMessage({ action: 'get_activity' }, (response) => {
    if (response && response.activity) {
      const activities = Object.values(response.activity);
      
      if (activities.length > 0) {
        elements.activityList.innerHTML = '';
        
        // Sort by time and show last 5
        activities
          .sort((a, b) => new Date(b.loadTime) - new Date(a.loadTime))
          .slice(0, 5)
          .forEach(activity => {
            const item = document.createElement('div');
            item.className = 'activity-item';
            
            const time = new Date(activity.loadTime).toLocaleTimeString();
            const url = new URL(activity.url).pathname.slice(0, 30);
            const status = activity.simulated ? '✅ Simulated' : activity.loggedIn ? '👤 Logged In' : '🔒 Not Logged';
            
            item.textContent = `${time} - ${url}... - ${status}`;
            elements.activityList.appendChild(item);
          });
      } else {
        elements.activityList.innerHTML = '<div class="activity-item">No activity yet</div>';
      }
    }
  });
}

// Setup event listeners
function setupEventListeners() {
  // Enable toggle
  elements.enableToggle.addEventListener('change', async (e) => {
    settings.enabled = e.target.checked;
    await chrome.storage.sync.set({ enabled: settings.enabled });
    
    // Update service worker
    chrome.runtime.sendMessage({ 
      action: 'update_settings', 
      settings: { enabled: settings.enabled }
    });
    
    updateStatus();
    showNotification(`Extension ${settings.enabled ? 'enabled' : 'disabled'}`);
  });
  
  // Auto-simulate toggle
  elements.autoSimToggle.addEventListener('change', async (e) => {
    settings.autoSimulate = e.target.checked;
    await chrome.storage.sync.set({ autoSimulate: settings.autoSimulate });
    
    chrome.runtime.sendMessage({ 
      action: 'update_settings', 
      settings: { autoSimulate: settings.autoSimulate }
    });
    
    showNotification(`Auto-simulation ${settings.autoSimulate ? 'enabled' : 'disabled'}`);
  });
  
  // Debug toggle
  elements.debugToggle.addEventListener('change', async (e) => {
    settings.debugMode = e.target.checked;
    await chrome.storage.sync.set({ debugMode: settings.debugMode });
    
    chrome.runtime.sendMessage({ 
      action: 'update_settings', 
      settings: { debugMode: settings.debugMode }
    });
    
    showNotification(`Debug mode ${settings.debugMode ? 'enabled' : 'disabled'}`);
  });
  
  // Simulate button
  elements.simulateBtn.addEventListener('click', async () => {
    if (!currentTab || !currentTab.url || !currentTab.url.includes('seeking.com')) {
      showNotification('Please navigate to Seeking.com first', 'error');
      return;
    }
    
    elements.simulateBtn.disabled = true;
    elements.simulateBtn.innerHTML = 'Simulating... <span class="spinner"></span>';
    
    try {
      await chrome.tabs.sendMessage(currentTab.id, { action: 'reset' });
      showNotification('Simulation triggered successfully');
      
      // Wait and update status
      setTimeout(() => {
        updateStatus();
        elements.simulateBtn.disabled = false;
        elements.simulateBtn.textContent = 'Simulate Now';
      }, 2000);
    } catch (error) {
      console.error('Failed to trigger simulation:', error);
      showNotification('Failed to trigger simulation', 'error');
      elements.simulateBtn.disabled = false;
      elements.simulateBtn.textContent = 'Simulate Now';
    }
  });
  
  // Refresh button
  elements.refreshBtn.addEventListener('click', async () => {
    elements.refreshBtn.disabled = true;
    elements.refreshBtn.innerHTML = 'Refreshing... <span class="spinner"></span>';
    
    await updateStatus();
    await loadActivity();
    
    setTimeout(() => {
      elements.refreshBtn.disabled = false;
      elements.refreshBtn.textContent = 'Refresh Status';
      showNotification('Status refreshed');
    }, 500);
  });
  
  // Clear activity button
  elements.clearBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'clear_activity' }, () => {
      elements.activityList.innerHTML = '<div class="activity-item">Activity cleared</div>';
      showNotification('Activity log cleared');
    });
  });
}

// Show notification
function showNotification(message, type = 'success') {
  // Create notification element
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    background: ${type === 'error' ? '#ef4444' : '#10b981'};
    color: white;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 1000;
    animation: slideIn 0.3s ease;
  `;
  notification.textContent = message;
  
  // Add animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(notification);
  
  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.animation = 'slideIn 0.3s ease reverse';
    setTimeout(() => {
      notification.remove();
      style.remove();
    }, 300);
  }, 3000);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}