// Content script for Seeking.com chat automation
class SeekingChatAutomation {
  constructor() {
    this.isActive = false;
    this.config = {
      responseDelay: 5000, // 5 seconds delay to mimic human typing
      checkInterval: 3000, // Check for new messages every 3 seconds
      templates: [],
      keywords: {},
      blockedUsers: []
    };
    this.observer = null;
    this.currentChat = null;
    this.messageHistory = new Map();
    this.init();
  }

  async init() {
    console.log('[SCA] Initializing Seeking Chat Automation...');
    
    // Load configuration from storage
    await this.loadConfig();
    
    // Listen for messages from popup
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      this.handleMessage(request, sendResponse);
      return true; // Keep message channel open for async response
    });

    // Start monitoring if active
    if (this.isActive) {
      this.startMonitoring();
    }
  }

  async loadConfig() {
    return new Promise((resolve) => {
      chrome.storage.local.get(['isActive', 'config'], (result) => {
        if (result.isActive !== undefined) {
          this.isActive = result.isActive;
        }
        if (result.config) {
          this.config = { ...this.config, ...result.config };
        }
        console.log('[SCA] Config loaded:', this.config);
        resolve();
      });
    });
  }

  handleMessage(request, sendResponse) {
    console.log('[SCA] Received message:', request);
    
    switch (request.action) {
      case 'toggle':
        this.isActive = request.isActive;
        if (this.isActive) {
          this.startMonitoring();
          sendResponse({ success: true, message: 'Automation started' });
        } else {
          this.stopMonitoring();
          sendResponse({ success: true, message: 'Automation stopped' });
        }
        break;
        
      case 'updateConfig':
        this.config = { ...this.config, ...request.config };
        chrome.storage.local.set({ config: this.config });
        sendResponse({ success: true, message: 'Configuration updated' });
        break;
        
      case 'getStatus':
        sendResponse({ 
          isActive: this.isActive, 
          config: this.config,
          stats: {
            messagesRead: this.messageHistory.size,
            currentChat: this.currentChat
          }
        });
        break;
        
      default:
        sendResponse({ success: false, message: 'Unknown action' });
    }
  }

  startMonitoring() {
    console.log('[SCA] Starting chat monitoring...');
    
    // Set up mutation observer for chat list changes
    this.setupChatObserver();
    
    // Set up periodic check for new messages
    this.messageCheckInterval = setInterval(() => {
      this.checkForNewMessages();
    }, this.config.checkInterval);
    
    // Initial check
    this.checkForNewMessages();
  }

  stopMonitoring() {
    console.log('[SCA] Stopping chat monitoring...');
    
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    
    if (this.messageCheckInterval) {
      clearInterval(this.messageCheckInterval);
      this.messageCheckInterval = null;
    }
  }

  setupChatObserver() {
    // Common selectors for chat interfaces - will need adjustment for actual site
    const chatSelectors = [
      '.chat-list',
      '.message-list',
      '[data-testid="chat-list"]',
      '.conversations',
      '.inbox',
      '#messages'
    ];
    
    let chatContainer = null;
    for (const selector of chatSelectors) {
      chatContainer = document.querySelector(selector);
      if (chatContainer) {
        console.log('[SCA] Found chat container:', selector);
        break;
      }
    }
    
    if (!chatContainer) {
      console.log('[SCA] Chat container not found, will retry...');
      setTimeout(() => this.setupChatObserver(), 2000);
      return;
    }
    
    // Create mutation observer
    this.observer = new MutationObserver((mutations) => {
      this.handleChatMutations(mutations);
    });
    
    // Start observing
    this.observer.observe(chatContainer, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'data-unread', 'data-new']
    });
  }

  handleChatMutations(mutations) {
    for (const mutation of mutations) {
      // Check for new message indicators
      if (mutation.type === 'childList' || mutation.type === 'attributes') {
        const unreadIndicators = [
          '.unread',
          '.new-message',
          '[data-unread="true"]',
          '.notification-badge',
          '.message-count'
        ];
        
        for (const selector of unreadIndicators) {
          const unreadElement = mutation.target.querySelector?.(selector);
          if (unreadElement) {
            console.log('[SCA] New message detected!');
            this.handleNewMessage(mutation.target);
            break;
          }
        }
      }
    }
  }

  checkForNewMessages() {
    if (!this.isActive) return;
    
    // Look for unread message indicators
    const unreadSelectors = [
      '.chat-item.unread',
      '.conversation-item[data-unread="true"]',
      '.message-preview.new',
      '[class*="unread"]',
      '[class*="new-message"]'
    ];
    
    for (const selector of unreadSelectors) {
      const unreadChats = document.querySelectorAll(selector);
      if (unreadChats.length > 0) {
        console.log(`[SCA] Found ${unreadChats.length} unread chats`);
        // Process the first unread chat
        this.selectAndOpenChat(unreadChats[0]);
        break;
      }
    }
  }

  selectAndOpenChat(chatElement) {
    console.log('[SCA] Opening chat...');
    
    // Simulate click to open chat
    chatElement.click();
    
    // Wait for chat to load
    setTimeout(() => {
      this.readAndProcessMessages();
    }, 1000);
  }

  handleNewMessage(element) {
    // Find the chat item containing the new message
    const chatItem = element.closest('.chat-item, .conversation-item, [data-chat-id]');
    if (chatItem) {
      this.selectAndOpenChat(chatItem);
    }
  }

  readAndProcessMessages() {
    console.log('[SCA] Reading messages...');
    
    // Common message container selectors
    const messageSelectors = [
      '.message-text',
      '.message-content',
      '[data-message-content]',
      '.chat-message',
      '.msg-text'
    ];
    
    let messages = [];
    for (const selector of messageSelectors) {
      const messageElements = document.querySelectorAll(selector);
      if (messageElements.length > 0) {
        messages = Array.from(messageElements);
        console.log(`[SCA] Found ${messages.length} messages with selector: ${selector}`);
        break;
      }
    }
    
    if (messages.length === 0) {
      console.log('[SCA] No messages found');
      return;
    }
    
    // Get the last message (most recent)
    const lastMessage = messages[messages.length - 1];
    const messageText = lastMessage.textContent.trim();
    
    // Check if this is a message from the other person (not our own)
    const isIncoming = this.isIncomingMessage(lastMessage);
    
    if (isIncoming && messageText) {
      console.log('[SCA] Processing incoming message:', messageText);
      
      // Check if we've already responded to this message
      const messageId = this.generateMessageId(messageText);
      if (!this.messageHistory.has(messageId)) {
        this.messageHistory.set(messageId, Date.now());
        this.generateAndSendResponse(messageText);
      } else {
        console.log('[SCA] Already responded to this message');
      }
    }
  }

  isIncomingMessage(messageElement) {
    // Check if message is from other person (not self)
    // Common patterns: different alignment, different class, etc.
    const selfIndicators = [
      '.message-sent',
      '.message-self',
      '.outgoing',
      '[data-sender="self"]'
    ];
    
    for (const selector of selfIndicators) {
      if (messageElement.matches(selector) || messageElement.closest(selector)) {
        return false;
      }
    }
    
    // Additional check: messages on the right are usually self
    const rect = messageElement.getBoundingClientRect();
    const parentRect = messageElement.parentElement.getBoundingClientRect();
    if (rect.left > parentRect.width / 2) {
      return false;
    }
    
    return true;
  }

  generateMessageId(text) {
    // Simple hash function for message deduplication
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `msg_${hash}_${text.length}`;
  }

  generateAndSendResponse(incomingMessage) {
    console.log('[SCA] Generating response for:', incomingMessage);
    
    // Analyze message and generate response
    const response = this.generateResponse(incomingMessage);
    
    if (response) {
      // Add human-like delay
      setTimeout(() => {
        this.sendMessage(response);
      }, this.config.responseDelay);
    }
  }

  generateResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    // Check for blocked keywords
    const blockedKeywords = this.config.blockedKeywords || [];
    for (const keyword of blockedKeywords) {
      if (lowerMessage.includes(keyword.toLowerCase())) {
        console.log('[SCA] Message contains blocked keyword:', keyword);
        return null;
      }
    }
    
    // Keyword-based response matching
    const keywordResponses = this.config.keywords || {};
    for (const [keyword, response] of Object.entries(keywordResponses)) {
      if (lowerMessage.includes(keyword.toLowerCase())) {
        console.log('[SCA] Matched keyword:', keyword);
        return this.personalizeResponse(response, message);
      }
    }
    
    // Use template responses
    const templates = this.config.templates || [];
    if (templates.length > 0) {
      // Simple rotation through templates or random selection
      const randomTemplate = templates[Math.floor(Math.random() * templates.length)];
      return this.personalizeResponse(randomTemplate, message);
    }
    
    // Default responses based on common patterns
    const defaultResponses = {
      'hello': "Hi there! How are you doing today?",
      'hi': "Hey! Nice to hear from you 😊",
      'how are you': "I'm doing great, thanks for asking! How about you?",
      'meet': "That sounds interesting! When were you thinking?",
      'coffee': "Coffee sounds perfect! What's your favorite spot?",
      'dinner': "Dinner would be lovely! Do you have a place in mind?",
      'weekend': "Weekends are great for me! What did you have in mind?",
      'available': "Let me check my schedule and get back to you!",
      'number': "Sure, let's chat a bit more here first 😊",
      'photo': "I'd love to see more about you! Tell me about yourself.",
      'work': "Work keeps me busy but I always make time for interesting people!",
      'hobby': "I love trying new things! What are you passionate about?"
    };
    
    // Check for default pattern matches
    for (const [pattern, response] of Object.entries(defaultResponses)) {
      if (lowerMessage.includes(pattern)) {
        return response;
      }
    }
    
    // Generic fallback response
    const fallbacks = [
      "That's interesting! Tell me more about that.",
      "I'd love to hear more about your thoughts on this!",
      "Thanks for sharing! What else is on your mind?",
      "That sounds great! How long have you been interested in that?",
      "Fascinating! What do you enjoy most about it?"
    ];
    
    return fallbacks[Math.floor(Math.random() * fallbacks.length)];
  }

  personalizeResponse(template, originalMessage) {
    // Add some personalization to templates
    let response = template;
    
    // Add occasional emojis for friendliness
    const emojis = ['😊', '😄', '🙂', '👍', '✨'];
    if (Math.random() > 0.7) {
      response += ' ' + emojis[Math.floor(Math.random() * emojis.length)];
    }
    
    // Add variation to avoid detection
    const variations = [
      (s) => s,
      (s) => s.replace('!', '.'),
      (s) => s.replace('.', '!'),
      (s) => s.charAt(0).toLowerCase() + s.slice(1),
    ];
    
    const variation = variations[Math.floor(Math.random() * variations.length)];
    return variation(response);
  }

  sendMessage(message) {
    console.log('[SCA] Sending message:', message);
    
    // Find input field
    const inputSelectors = [
      'textarea[placeholder*="message"]',
      'input[type="text"][placeholder*="message"]',
      '.message-input',
      '[contenteditable="true"]',
      'textarea.chat-input',
      '#message-input'
    ];
    
    let inputField = null;
    for (const selector of inputSelectors) {
      inputField = document.querySelector(selector);
      if (inputField) {
        console.log('[SCA] Found input field:', selector);
        break;
      }
    }
    
    if (!inputField) {
      console.error('[SCA] Could not find message input field');
      return;
    }
    
    // Set the message text
    if (inputField.tagName === 'INPUT' || inputField.tagName === 'TEXTAREA') {
      inputField.value = message;
      inputField.dispatchEvent(new Event('input', { bubbles: true }));
    } else if (inputField.contentEditable === 'true') {
      inputField.textContent = message;
      inputField.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    // Find and click send button
    setTimeout(() => {
      const sendButtonSelectors = [
        'button[type="submit"]',
        'button[aria-label*="send"]',
        '.send-button',
        '.message-send',
        'button.send',
        '[data-testid="send-button"]'
      ];
      
      let sendButton = null;
      for (const selector of sendButtonSelectors) {
        sendButton = document.querySelector(selector);
        if (sendButton) {
          console.log('[SCA] Found send button:', selector);
          sendButton.click();
          break;
        }
      }
      
      if (!sendButton) {
        // Try pressing Enter as fallback
        console.log('[SCA] No send button found, simulating Enter key');
        const enterEvent = new KeyboardEvent('keydown', {
          key: 'Enter',
          code: 'Enter',
          keyCode: 13,
          which: 13,
          bubbles: true
        });
        inputField.dispatchEvent(enterEvent);
      }
      
      // Log the sent message
      this.logMessage('sent', message);
      
    }, 500);
  }

  logMessage(type, message) {
    const log = {
      timestamp: new Date().toISOString(),
      type: type,
      message: message,
      url: window.location.href
    };
    
    console.log('[SCA] Message log:', log);
    
    // Store in chrome storage for popup display
    chrome.storage.local.get(['messageLogs'], (result) => {
      const logs = result.messageLogs || [];
      logs.push(log);
      // Keep only last 100 logs
      if (logs.length > 100) {
        logs.shift();
      }
      chrome.storage.local.set({ messageLogs: logs });
    });
  }
}

// Initialize automation when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new SeekingChatAutomation();
  });
} else {
  new SeekingChatAutomation();
}