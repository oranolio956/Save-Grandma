# Seeking Chat Automation Chrome Extension

## 📋 Overview

A Chrome extension that automates chat responses on Seeking.com, designed to help users manage conversations efficiently. The extension detects new messages, reads them, and sends appropriate responses based on configurable templates and keywords.

**Version:** 1.0.0  
**Platform:** Chrome/Edge (Manifest V3)  
**Target Site:** Seeking.com

## 🚀 Features

### Core Functionality
- **Real-time Message Detection**: Monitors for new/unread messages using DOM observers
- **Automated Response Generation**: Keyword-based and template responses
- **Human-like Behavior**: Configurable delays between actions (5-10 seconds)
- **Smart Filtering**: Block unwanted conversations with keyword filters
- **Message Logging**: Track all automated interactions
- **Statistics Dashboard**: Monitor messages read/sent and active chats

### Technical Features
- Chrome Extension Manifest V3 compliance
- Persistent configuration storage
- Background service worker for reliability
- Content script injection for DOM manipulation
- Popup UI for easy configuration

## 📦 Installation

### Development Installation

1. **Clone or Download the Repository**
   ```bash
   git clone <repository-url>
   # or download and extract the ZIP file
   ```

2. **Open Chrome Extension Management**
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)

3. **Load the Extension**
   - Click "Load unpacked"
   - Select the extension directory containing `manifest.json`

4. **Generate Icons** (Optional)
   - Open `icons/generate_icons.html` in a browser
   - Right-click each canvas and save as PNG with the specified filename

### Production Build (Future)
```bash
# Install dependencies (if any)
npm install

# Build extension
npm run build

# Output will be in dist/ directory
```

## 🎮 Usage

### Initial Setup

1. **Navigate to Seeking.com**
   - Log in to your account
   - The extension will automatically activate

2. **Configure Settings**
   - Click the extension icon in toolbar
   - Set up response templates
   - Configure keywords and responses
   - Adjust timing settings

3. **Enable Automation**
   - Toggle the power switch in popup
   - Extension begins monitoring for messages

### Configuration Options

#### Response Templates
Pre-written responses that rotate or are selected randomly:
```javascript
"That's interesting! Tell me more about that."
"I'd love to hear more about your thoughts on this!"
"Thanks for sharing! What else is on your mind?"
```

#### Keyword Mapping
Specific responses for detected keywords:
```javascript
"coffee" → "Coffee sounds perfect! What's your favorite spot?"
"meet" → "That sounds interesting! When were you thinking?"
"weekend" → "Weekends are great for me! What did you have in mind?"
```

#### Settings
- **Response Delay**: 5-30 seconds (default: 5s)
- **Check Interval**: 1-60 seconds (default: 3s)
- **Max Conversations**: 1-10 simultaneous (default: 1)
- **Use Emojis**: Add friendly emojis to responses
- **Log Messages**: Keep conversation history

## 🏗️ Architecture

### File Structure
```
seeking-chat-automation/
├── manifest.json           # Extension configuration
├── background.js          # Service worker
├── content.js            # DOM interaction script
├── popup.html            # Control panel UI
├── popup.js              # Popup logic
├── popup.css             # Popup styles
├── styles.css            # Content script styles
├── welcome.html          # Onboarding page
├── icons/                # Extension icons
│   ├── icon-16.png
│   ├── icon-32.png
│   ├── icon-48.png
│   └── icon-128.png
└── README.md            # Documentation
```

### Component Overview

#### Content Script (`content.js`)
- Monitors DOM for chat updates
- Detects new messages
- Extracts message content
- Generates and sends responses
- Main class: `SeekingChatAutomation`

#### Background Script (`background.js`)
- Manages extension lifecycle
- Handles storage operations
- Coordinates between components
- Performs periodic cleanup

#### Popup Interface (`popup.html/js`)
- User configuration panel
- Template management
- Statistics display
- Log viewer
- Main class: `PopupController`

## 🔧 Development

### DOM Selectors Strategy

The extension uses multiple fallback selectors to handle site changes:

```javascript
// Chat container selectors
const chatSelectors = [
  '.chat-list',
  '.message-list',
  '[data-testid="chat-list"]',
  '.conversations',
  '.inbox'
];

// Message selectors
const messageSelectors = [
  '.message-text',
  '.message-content',
  '[data-message-content]',
  '.chat-message'
];
```

### Message Detection Flow

1. **MutationObserver** watches for DOM changes
2. **Check for unread indicators** (badges, classes)
3. **Click to open chat** programmatically
4. **Extract message text** from DOM
5. **Generate response** using templates/keywords
6. **Insert and send** response with delay

### Storage Schema

```javascript
{
  isActive: boolean,
  config: {
    templates: string[],
    keywords: { [key: string]: string },
    blockedKeywords: string[],
    responseDelay: number,
    checkInterval: number,
    maxConversations: number,
    useEmojis: boolean,
    logMessages: boolean
  },
  stats: {
    messagesRead: number,
    messagesSent: number,
    activeChats: number
  },
  messageLogs: Array<{
    timestamp: string,
    type: 'sent' | 'received',
    message: string,
    url: string
  }>
}
```

## 🧪 Testing

### Manual Testing Checklist

1. **Installation**
   - [ ] Extension loads without errors
   - [ ] Icons display correctly
   - [ ] Welcome page opens on first install

2. **Configuration**
   - [ ] Templates can be added/removed
   - [ ] Keywords save correctly
   - [ ] Settings persist after reload

3. **Automation**
   - [ ] Detects new messages
   - [ ] Sends responses with delay
   - [ ] Handles multiple conversations
   - [ ] Logs messages properly

4. **Edge Cases**
   - [ ] Handles site structure changes
   - [ ] Recovers from errors gracefully
   - [ ] Respects blocked keywords

### Debug Mode

Enable debug output in console:
```javascript
// In content.js, set debug flag
const DEBUG = true;
```

## 🚦 Roadmap

### Phase 1 (Current MVP)
- ✅ Basic message detection
- ✅ Template-based responses
- ✅ Keyword matching
- ✅ Configuration UI
- ✅ Message logging

### Phase 2 (Enhancements)
- [ ] AI integration (OpenAI/Claude API)
- [ ] Advanced conversation context
- [ ] Multi-language support
- [ ] Scheduling system
- [ ] Profile analysis

### Phase 3 (Scale)
- [ ] Cloud sync for settings
- [ ] Team collaboration features
- [ ] Analytics dashboard
- [ ] Mobile companion app
- [ ] Browser compatibility (Firefox, Safari)

## ⚠️ Important Considerations

### Ethical Usage
- Use responsibly and transparently
- Respect other users' time and expectations
- Maintain authentic interactions when appropriate
- Do not use for deceptive purposes

### Technical Limitations
- Depends on site structure (may break with updates)
- Browser performance impact with many conversations
- Storage limits for message logs
- Rate limiting considerations

### Legal Compliance
- Review Seeking.com Terms of Service
- Comply with local laws regarding automated communications
- Consider GDPR/privacy implications
- User consent for automated responses

## 🐛 Troubleshooting

### Common Issues

**Extension not detecting messages:**
- Check if you're logged into Seeking.com
- Verify extension is enabled in popup
- Inspect console for errors
- Site structure may have changed

**Responses not sending:**
- Check response delay settings
- Verify input field selectors
- Look for blocked keywords
- Check browser console for errors

**Configuration not saving:**
- Check Chrome storage permissions
- Clear extension storage and reconfigure
- Reinstall extension if needed

### Console Commands

```javascript
// Check extension status
chrome.storage.local.get(null, console.log)

// Clear all data
chrome.storage.local.clear()

// Force reload extension
chrome.runtime.reload()
```

## 📄 License

This project is provided for educational purposes. Users are responsible for ensuring their use complies with all applicable terms of service and laws.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review console logs for errors
- Test with latest Chrome version
- Ensure Seeking.com hasn't changed structure

## 🔒 Security

- No external data transmission
- All data stored locally in browser
- No tracking or analytics
- Open source for transparency

---

**Disclaimer:** This extension is not affiliated with Seeking.com. Use at your own risk and ensure compliance with all applicable terms of service and laws.