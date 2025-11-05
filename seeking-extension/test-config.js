// test-config.js - Configuration for testing the extension

const TEST_CONFIG = {
  // Test URLs for different Seeking.com pages
  testUrls: [
    'https://www.seeking.com/',
    'https://www.seeking.com/login',
    'https://www.seeking.com/dashboard',
    'https://www.seeking.com/search',
    'https://www.seeking.com/profile'
  ],
  
  // Selectors to test (update based on actual site inspection)
  testSelectors: {
    // Login indicators
    loginIndicators: [
      '.user-profile',
      '.profile-icon',
      '.user-avatar',
      '#user-menu',
      'a[href*="logout"]',
      '[data-testid="logout"]',
      '.logout-link',
      'button[aria-label="Sign out"]'
    ],
    
    // Input fields to test Enter simulation
    inputFields: [
      'input[name="q"]',
      'input[type="search"]',
      '.search-input',
      '#search-box',
      'input[placeholder*="search"]',
      'input[placeholder*="Search"]'
    ],
    
    // Forms to test
    forms: [
      'form[action*="search"]',
      'form.search-form',
      '#searchForm'
    ]
  },
  
  // Test scenarios
  testScenarios: [
    {
      name: 'Login Detection - Logged In',
      steps: [
        '1. Navigate to Seeking.com while logged in',
        '2. Open DevTools Console',
        '3. Check for log: "[Seeking Extension] User is logged in"',
        '4. Verify popup shows "Logged In" status'
      ],
      expectedResult: 'Extension correctly detects logged-in state'
    },
    {
      name: 'Login Detection - Not Logged In',
      steps: [
        '1. Navigate to Seeking.com in incognito (not logged in)',
        '2. Open DevTools Console',
        '3. Check for log: "[Seeking Extension] User is not logged in"',
        '4. Verify popup shows "Not Logged In" status'
      ],
      expectedResult: 'Extension correctly detects logged-out state'
    },
    {
      name: 'Enter Key Simulation',
      steps: [
        '1. Navigate to Seeking.com search page while logged in',
        '2. Focus on search input field',
        '3. Wait for automatic Enter simulation',
        '4. Check if form was submitted or search triggered'
      ],
      expectedResult: 'Enter key is simulated and triggers expected action'
    },
    {
      name: 'Manual Control via Popup',
      steps: [
        '1. Click extension icon to open popup',
        '2. Toggle "Enable Extension" switch',
        '3. Verify extension stops/starts working',
        '4. Click "Simulate Now" button',
        '5. Verify manual simulation works'
      ],
      expectedResult: 'All popup controls function correctly'
    },
    {
      name: 'Persistence Test',
      steps: [
        '1. Disable extension via popup',
        '2. Close and reopen browser',
        '3. Check if disabled state persists',
        '4. Enable and verify it persists'
      ],
      expectedResult: 'Settings persist across browser sessions'
    }
  ],
  
  // Debug commands for console
  debugCommands: {
    checkLoginStatus: `
      // Run in DevTools Console on Seeking.com
      const checkLogin = () => {
        const indicators = [
          document.querySelector('.user-profile'),
          document.querySelector('a[href*="logout"]'),
          localStorage.getItem('authToken'),
          document.cookie.includes('session')
        ];
        console.log('Login indicators found:', indicators);
        return indicators.some(i => !!i);
      };
      console.log('Is logged in?', checkLogin());
    `,
    
    testEnterSimulation: `
      // Test Enter key simulation
      const testEnter = (selector) => {
        const element = document.querySelector(selector);
        if (element) {
          element.focus();
          const event = new KeyboardEvent('keydown', {
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,
            bubbles: true
          });
          element.dispatchEvent(event);
          console.log('Enter simulated on:', selector);
        } else {
          console.log('Element not found:', selector);
        }
      };
      testEnter('input[type="search"]');
    `,
    
    inspectStorage: `
      // Inspect extension storage
      chrome.storage.sync.get(null, (data) => {
        console.log('Extension settings:', data);
      });
    `,
    
    getElementSelectors: `
      // Get CSS selector for clicked element
      document.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const path = [];
        let el = e.target;
        while (el && el.nodeType === Node.ELEMENT_NODE) {
          let selector = el.nodeName.toLowerCase();
          if (el.id) {
            selector += '#' + el.id;
            path.unshift(selector);
            break;
          } else if (el.className) {
            selector += '.' + el.className.split(' ').join('.');
          }
          path.unshift(selector);
          el = el.parentNode;
        }
        console.log('Selector:', path.join(' > '));
        return false;
      }, true);
      console.log('Click any element to get its selector');
    `
  }
};

// Export for use in testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TEST_CONFIG;
}

// Log config if run directly
if (typeof window !== 'undefined') {
  console.log('Test Configuration Loaded:', TEST_CONFIG);
  console.log('Run TEST_CONFIG.debugCommands.checkLoginStatus in console to test login detection');
}