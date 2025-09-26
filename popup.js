// Popup script for Chrome extension
class PopupController {
  constructor() {
    this.config = {
      templates: [
        "That's interesting! Tell me more about that.",
        "I'd love to hear more about your thoughts on this!",
        "Thanks for sharing! What else is on your mind?",
        "That sounds great! How long have you been interested in that?",
        "Fascinating! What do you enjoy most about it?"
      ],
      keywords: {
        "hello": "Hi there! How are you doing today?",
        "meet": "That sounds interesting! When were you thinking?",
        "coffee": "Coffee sounds perfect! What's your favorite spot?",
        "dinner": "Dinner would be lovely! Do you have a place in mind?"
      },
      blockedKeywords: [],
      responseDelay: 5000,
      checkInterval: 3000,
      maxConversations: 1,
      useEmojis: true,
      logMessages: true
    };
    
    this.isActive = false;
    this.stats = {
      messagesRead: 0,
      messagesSent: 0,
      activeChats: 0
    };
    
    this.init();
  }

  async init() {
    // Load saved configuration
    await this.loadConfig();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Update UI with current state
    this.updateUI();
    
    // Get current status from content script
    this.requestStatus();
  }

  async loadConfig() {
    return new Promise((resolve) => {
      chrome.storage.local.get(['isActive', 'config', 'stats'], (result) => {
        if (result.isActive !== undefined) {
          this.isActive = result.isActive;
        }
        if (result.config) {
          this.config = { ...this.config, ...result.config };
        }
        if (result.stats) {
          this.stats = { ...this.stats, ...result.stats };
        }
        resolve();
      });
    });
  }

  setupEventListeners() {
    // Power toggle
    const powerToggle = document.getElementById('powerToggle');
    powerToggle.addEventListener('change', (e) => {
      this.toggleAutomation(e.target.checked);
    });
    
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        this.switchTab(e.target.dataset.tab);
      });
    });
    
    // Template management
    document.getElementById('addTemplateBtn').addEventListener('click', () => {
      this.addTemplate();
    });
    
    // Keyword management
    document.getElementById('addKeywordBtn').addEventListener('click', () => {
      this.addKeyword();
    });
    
    document.getElementById('addBlockedBtn').addEventListener('click', () => {
      this.addBlockedKeyword();
    });
    
    // Settings
    document.getElementById('saveSettingsBtn').addEventListener('click', () => {
      this.saveSettings();
    });
    
    // Logs
    document.getElementById('clearLogsBtn').addEventListener('click', () => {
      this.clearLogs();
    });
    
    document.getElementById('exportLogsBtn').addEventListener('click', () => {
      this.exportLogs();
    });
  }

  switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
      btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-pane').forEach(pane => {
      pane.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    
    // Load tab-specific content
    if (tabName === 'logs') {
      this.loadLogs();
    }
  }

  async toggleAutomation(enable) {
    this.isActive = enable;
    
    // Save state
    chrome.storage.local.set({ isActive: this.isActive });
    
    // Send message to content script
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs[0]) {
      chrome.tabs.sendMessage(tabs[0].id, {
        action: 'toggle',
        isActive: this.isActive
      }, (response) => {
        if (response && response.success) {
          this.showNotification(response.message, 'success');
        }
      });
    }
    
    // Update UI
    this.updateStatus();
  }

  updateUI() {
    // Update power toggle
    document.getElementById('powerToggle').checked = this.isActive;
    
    // Update status
    this.updateStatus();
    
    // Update templates
    this.renderTemplates();
    
    // Update keywords
    this.renderKeywords();
    
    // Update settings
    this.renderSettings();
    
    // Update statistics
    this.updateStats();
  }

  updateStatus() {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    if (this.isActive) {
      statusDot.classList.add('active');
      statusText.textContent = 'Active';
    } else {
      statusDot.classList.remove('active');
      statusText.textContent = 'Inactive';
    }
  }

  renderTemplates() {
    const templateList = document.getElementById('templateList');
    templateList.innerHTML = '';
    
    this.config.templates.forEach((template, index) => {
      const item = document.createElement('div');
      item.className = 'template-item';
      item.innerHTML = `
        <span>${template.substring(0, 50)}${template.length > 50 ? '...' : ''}</span>
        <button class="delete-btn" data-index="${index}">Delete</button>
      `;
      
      item.querySelector('.delete-btn').addEventListener('click', (e) => {
        this.deleteTemplate(parseInt(e.target.dataset.index));
      });
      
      templateList.appendChild(item);
    });
  }

  renderKeywords() {
    // Render keyword responses
    const keywordList = document.getElementById('keywordList');
    keywordList.innerHTML = '';
    
    Object.entries(this.config.keywords).forEach(([keyword, response]) => {
      const item = document.createElement('div');
      item.className = 'keyword-item';
      item.innerHTML = `
        <span><strong>${keyword}:</strong> ${response.substring(0, 30)}...</span>
        <button class="delete-btn" data-keyword="${keyword}">Delete</button>
      `;
      
      item.querySelector('.delete-btn').addEventListener('click', (e) => {
        this.deleteKeyword(e.target.dataset.keyword);
      });
      
      keywordList.appendChild(item);
    });
    
    // Render blocked keywords
    const blockedList = document.getElementById('blockedList');
    blockedList.innerHTML = '';
    
    this.config.blockedKeywords.forEach((keyword, index) => {
      const item = document.createElement('div');
      item.className = 'blocked-item';
      item.innerHTML = `
        <span>${keyword}</span>
        <button class="delete-btn" data-index="${index}">Remove</button>
      `;
      
      item.querySelector('.delete-btn').addEventListener('click', (e) => {
        this.deleteBlockedKeyword(parseInt(e.target.dataset.index));
      });
      
      blockedList.appendChild(item);
    });
  }

  renderSettings() {
    document.getElementById('responseDelay').value = this.config.responseDelay / 1000;
    document.getElementById('checkInterval').value = this.config.checkInterval / 1000;
    document.getElementById('maxConversations').value = this.config.maxConversations;
    document.getElementById('useEmojis').checked = this.config.useEmojis;
    document.getElementById('logMessages').checked = this.config.logMessages;
  }

  updateStats() {
    document.getElementById('messagesRead').textContent = this.stats.messagesRead;
    document.getElementById('messagesSent').textContent = this.stats.messagesSent;
    document.getElementById('activeChats').textContent = this.stats.activeChats;
  }

  addTemplate() {
    const input = document.getElementById('newTemplate');
    const template = input.value.trim();
    
    if (template) {
      this.config.templates.push(template);
      this.saveConfig();
      this.renderTemplates();
      input.value = '';
      this.showNotification('Template added successfully', 'success');
    }
  }

  deleteTemplate(index) {
    this.config.templates.splice(index, 1);
    this.saveConfig();
    this.renderTemplates();
  }

  addKeyword() {
    const keywordInput = document.getElementById('newKeyword');
    const responseInput = document.getElementById('newKeywordResponse');
    
    const keyword = keywordInput.value.trim().toLowerCase();
    const response = responseInput.value.trim();
    
    if (keyword && response) {
      this.config.keywords[keyword] = response;
      this.saveConfig();
      this.renderKeywords();
      keywordInput.value = '';
      responseInput.value = '';
      this.showNotification('Keyword added successfully', 'success');
    }
  }

  deleteKeyword(keyword) {
    delete this.config.keywords[keyword];
    this.saveConfig();
    this.renderKeywords();
  }

  addBlockedKeyword() {
    const input = document.getElementById('newBlocked');
    const keyword = input.value.trim().toLowerCase();
    
    if (keyword && !this.config.blockedKeywords.includes(keyword)) {
      this.config.blockedKeywords.push(keyword);
      this.saveConfig();
      this.renderKeywords();
      input.value = '';
      this.showNotification('Blocked keyword added', 'success');
    }
  }

  deleteBlockedKeyword(index) {
    this.config.blockedKeywords.splice(index, 1);
    this.saveConfig();
    this.renderKeywords();
  }

  saveSettings() {
    this.config.responseDelay = parseInt(document.getElementById('responseDelay').value) * 1000;
    this.config.checkInterval = parseInt(document.getElementById('checkInterval').value) * 1000;
    this.config.maxConversations = parseInt(document.getElementById('maxConversations').value);
    this.config.useEmojis = document.getElementById('useEmojis').checked;
    this.config.logMessages = document.getElementById('logMessages').checked;
    
    this.saveConfig();
    this.showNotification('Settings saved successfully', 'success');
  }

  async saveConfig() {
    chrome.storage.local.set({ config: this.config });
    
    // Send updated config to content script
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs[0]) {
      chrome.tabs.sendMessage(tabs[0].id, {
        action: 'updateConfig',
        config: this.config
      });
    }
  }

  async loadLogs() {
    chrome.storage.local.get(['messageLogs'], (result) => {
      const logs = result.messageLogs || [];
      const logList = document.getElementById('logList');
      logList.innerHTML = '';
      
      // Show latest logs first
      logs.reverse().slice(0, 50).forEach(log => {
        const item = document.createElement('div');
        item.className = `log-item ${log.type}`;
        
        const time = new Date(log.timestamp).toLocaleTimeString();
        item.innerHTML = `
          <div class="log-time">${time}</div>
          <div class="log-message">${log.type === 'sent' ? '→' : '←'} ${log.message}</div>
        `;
        
        logList.appendChild(item);
      });
      
      if (logs.length === 0) {
        logList.innerHTML = '<div class="log-item">No messages logged yet</div>';
      }
    });
  }

  clearLogs() {
    if (confirm('Are you sure you want to clear all logs?')) {
      chrome.storage.local.set({ messageLogs: [] });
      this.loadLogs();
      this.showNotification('Logs cleared', 'success');
    }
  }

  exportLogs() {
    chrome.storage.local.get(['messageLogs'], (result) => {
      const logs = result.messageLogs || [];
      const jsonData = JSON.stringify(logs, null, 2);
      
      const blob = new Blob([jsonData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `seeking-chat-logs-${Date.now()}.json`;
      a.click();
      
      URL.revokeObjectURL(url);
      this.showNotification('Logs exported successfully', 'success');
    });
  }

  async requestStatus() {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs[0]) {
      chrome.tabs.sendMessage(tabs[0].id, {
        action: 'getStatus'
      }, (response) => {
        if (response) {
          this.isActive = response.isActive;
          if (response.config) {
            this.config = { ...this.config, ...response.config };
          }
          if (response.stats) {
            this.stats = { ...this.stats, ...response.stats };
          }
          this.updateUI();
        }
      });
    }
  }

  showNotification(message, type = 'info') {
    // Create a temporary notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 10px 20px;
      background: ${type === 'success' ? '#28a745' : '#17a2b8'};
      color: white;
      border-radius: 5px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      z-index: 10000;
      animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 3000);
  }
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(style);

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new PopupController();
});