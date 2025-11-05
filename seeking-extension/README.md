# Seeking Auto Detector Chrome Extension

## ⚠️ IMPORTANT SAFETY & LEGAL NOTICE

**This extension is intended for personal, educational, or efficiency purposes only.** 

Automating interactions on sites like Seeking.com can violate their terms of service and may result in:
- Account suspension or permanent ban
- Legal consequences
- Security vulnerabilities
- Loss of access to services

**Always comply with website terms of service. Do not use this extension for:**
- Spamming or harassment
- Data scraping
- Malicious activities
- Commercial purposes without permission
- Excessive automation that impacts server performance

**USE AT YOUR OWN RISK. The developers are not responsible for any consequences resulting from the use of this extension.**

## 📋 Features

- **Automatic Login Detection**: Reliably detects user login status on Seeking.com pages
- **Enter Key Simulation**: Automatically simulates Enter key press with multiple fallback methods
- **Manual Control**: Toggle features on/off via popup interface
- **Activity Logging**: Track extension activity and status
- **Debug Mode**: Optional debug notifications and enhanced logging
- **Secure & Minimal Permissions**: Only requests necessary permissions for operation

## 🚀 Installation Guide

### Prerequisites
- Chrome browser version 88+ (for full Manifest V3 support)
- Basic understanding of Chrome extensions
- Access to Chrome Developer Mode

### Step-by-Step Installation

1. **Download/Clone the Extension**
   ```bash
   git clone [repository-url]
   # OR download and extract the ZIP file
   ```

2. **Open Chrome Extension Management**
   - Open Chrome browser
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right corner)

3. **Load the Extension**
   - Click "Load unpacked"
   - Select the `seeking-extension` folder
   - The extension should appear in your extensions list

4. **Create Icon Files** (if missing)
   - Create three PNG files: `icon16.png`, `icon48.png`, `icon128.png`
   - Or use the provided `generate-icons.js` script for placeholder SVGs
   - Place them in the extension folder

5. **Verify Installation**
   - Look for the extension icon in your Chrome toolbar
   - Click the icon to open the popup and verify it loads correctly

## 🔧 Configuration & Usage

### Initial Setup

1. **Inspect Seeking.com Elements** (Important!)
   - Navigate to Seeking.com
   - Open Chrome DevTools (F12)
   - Go to Elements tab
   - Find login indicators (profile icons, logout links, etc.)
   - Update selectors in `content.js` if needed:
   ```javascript
   const SELECTORS = {
     profile: ['.user-profile', '.profile-icon'],  // Update these
     logout: ['a[href*="logout"]'],                // based on
     targetInput: 'input[name="q"]'                // actual site
   };
   ```

2. **Test Login Detection**
   - Visit Seeking.com while logged in
   - Open DevTools Console
   - Look for: `[Seeking Extension] User is logged in`
   - If not detected, update selectors

### Using the Extension

#### Automatic Mode (Default)
- Extension activates automatically on Seeking.com pages
- Detects login status
- Simulates Enter key when conditions are met

#### Manual Control via Popup
- Click extension icon to open control panel
- Toggle features:
  - **Enable Extension**: Master on/off switch
  - **Auto-Simulate Enter**: Toggle automatic key simulation
  - **Debug Mode**: Enable detailed logging
- Actions:
  - **Simulate Now**: Manually trigger Enter simulation
  - **Refresh Status**: Update current status
  - **Clear Activity**: Clear activity log

### Customization

#### Modify Target Elements
Edit `content.js` to change which element receives the Enter key:
```javascript
const SELECTORS = {
  targetInput: 'input[name="q"], input[type="search"], .custom-input'
};
```

#### Adjust Timing
Modify delay before simulation in `content.js`:
```javascript
setTimeout(() => {
  const success = simulateEnter(SELECTORS.targetInput);
}, 1000);  // Change delay (milliseconds)
```

#### Add Site-Specific Logic
Extend login detection in `content.js`:
```javascript
function isLoggedIn() {
  // Add custom checks
  const customCheck = document.querySelector('.my-custom-element');
  return !!(profileElement || customCheck);
}
```

## 🐛 Troubleshooting

### Extension Not Loading
- Ensure Developer Mode is enabled
- Check for errors in `chrome://extensions/`
- Verify all files are present
- Check manifest.json syntax

### Login Not Detected
1. Open DevTools Console
2. Check for error messages
3. Verify selectors match current site structure
4. Test localStorage/sessionStorage keys:
   ```javascript
   console.log(localStorage);
   console.log(sessionStorage);
   ```

### Enter Key Not Working
- Some sites block synthetic events for security
- Try different fallback methods:
  - Form submission
  - Button click
  - Direct navigation
- Check Content Security Policy (CSP) restrictions

### Debugging Steps
1. Enable Debug Mode in popup
2. Check Console for logs
3. Monitor Network tab for requests
4. Use Chrome Extension Debugger

## 📁 File Structure

```
seeking-extension/
├── manifest.json          # Extension configuration
├── content.js            # Main content script
├── service-worker.js     # Background service worker
├── popup.html           # Popup UI
├── popup.js            # Popup logic
├── icon16.png          # Toolbar icon (16x16)
├── icon48.png          # Extension icon (48x48)
├── icon128.png         # Store icon (128x128)
├── generate-icons.js   # Icon generation helper
└── README.md          # This file
```

## 🔒 Security Considerations

### Permissions Explained
- **scripting**: Required for content script injection
- **activeTab**: Access to current tab only
- **storage**: Save user preferences
- **host_permissions**: Limited to `*.seeking.com/*`

### Best Practices
1. Never store sensitive data in extension storage
2. Avoid injecting into payment or password fields
3. Respect rate limits and server resources
4. Review code before installation
5. Keep extension updated

## 🚦 Testing Checklist

- [ ] Extension loads without errors
- [ ] Popup opens and displays correctly
- [ ] Login detection works when logged in
- [ ] Login detection works when logged out
- [ ] Enter simulation triggers on correct element
- [ ] Toggle switches save state
- [ ] Activity log updates
- [ ] Manual simulation button works
- [ ] Debug mode shows notifications
- [ ] Extension respects disabled state

## 🔄 Updates & Maintenance

### Updating Selectors
When Seeking.com updates their HTML:
1. Inspect new element structure
2. Update `SELECTORS` object in `content.js`
3. Test thoroughly
4. Reload extension

### Version Updates
1. Update version in `manifest.json`
2. Document changes
3. Test all features
4. Reload in Chrome

## ⚡ Performance Tips

- Extension uses MutationObserver for efficiency
- Avoids continuous polling
- Disconnects observers after action
- Cleans up on page unload
- Minimal memory footprint

## 🤝 Ethical Guidelines

1. **Personal Use Only**: Do not distribute for commercial purposes
2. **Respect Privacy**: Do not collect user data
3. **Transparent Operation**: Users should understand what the extension does
4. **Compliance**: Follow all applicable laws and terms of service
5. **Responsible Automation**: Avoid overwhelming servers

## 📚 Additional Resources

- [Chrome Extension Documentation](https://developer.chrome.com/docs/extensions/mv3/)
- [Manifest V3 Migration Guide](https://developer.chrome.com/docs/extensions/mv3/intro/)
- [Content Scripts Guide](https://developer.chrome.com/docs/extensions/mv3/content_scripts/)
- [Chrome Extension Security](https://developer.chrome.com/docs/extensions/mv3/security/)

## 🎯 Alternative Solutions

If this extension doesn't meet your needs, consider:
- **Automa**: Browser automation extension (no coding required)
- **Puppeteer**: Headless browser automation (Node.js)
- **Selenium**: Web automation framework
- **Tampermonkey**: Userscript manager

## 📝 License & Disclaimer

This extension is provided "as is" without warranty of any kind. Use at your own risk. The authors are not liable for any damages or consequences arising from its use.

**Remember**: Always prioritize ethical use and compliance with terms of service.

## 🆘 Support

For issues or questions:
1. Check this README thoroughly
2. Review console logs for errors
3. Ensure you're using the latest version
4. Test in incognito mode (with extension allowed)
5. Create an issue with detailed information

---

**Last Updated**: 2025
**Version**: 1.0
**Manifest Version**: V3