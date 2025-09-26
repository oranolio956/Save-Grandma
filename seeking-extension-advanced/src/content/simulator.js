/**
 * Complete Human Behavior Simulation System
 * Full implementation of mouse, keyboard, and scroll patterns
 */

class HumanBehaviorSimulator {
  constructor() {
    // Generate unique human profile
    this.profile = this.generateHumanProfile();
    
    // Track behavior patterns
    this.mouseHistory = [];
    this.keyHistory = [];
    this.scrollHistory = [];
    this.clickHistory = [];
    
    // Timing patterns
    this.lastActionTime = Date.now();
    this.sessionStartTime = Date.now();
    
    // Initialize sub-simulators
    this.mouseSimulator = new MouseSimulator(this.profile);
    this.keyboardSimulator = new KeyboardSimulator(this.profile);
    this.scrollSimulator = new ScrollSimulator(this.profile);
  }

  /**
   * Generate realistic human profile
   */
  generateHumanProfile() {
    return {
      // Typing characteristics
      typingSpeed: 40 + Math.random() * 60, // 40-100 WPM
      typoRate: 0.01 + Math.random() * 0.04, // 1-5% typos
      keyPressVariation: 20 + Math.random() * 30, // ms variation
      pauseBetweenWords: 100 + Math.random() * 200, // ms
      thinkingPauseChance: 0.05 + Math.random() * 0.1,
      
      // Mouse characteristics  
      mouseSpeed: 400 + Math.random() * 600, // pixels/second
      mouseAcceleration: 1.5 + Math.random() * 1,
      clickAccuracy: 0.85 + Math.random() * 0.14, // 85-99% accuracy
      doubleClickSpeed: 200 + Math.random() * 100, // ms
      dragSmoothness: 0.7 + Math.random() * 0.25,
      
      // Scroll characteristics
      scrollSpeed: 50 + Math.random() * 100, // pixels per wheel
      scrollAcceleration: 1.2 + Math.random() * 0.6,
      smoothScrolling: Math.random() > 0.3,
      scrollPauseChance: 0.1 + Math.random() * 0.2,
      
      // Reading patterns
      readingSpeed: 150 + Math.random() * 150, // 150-300 WPM
      skimming: Math.random() > 0.5,
      rereading: Math.random() > 0.7,
      
      // General behavior
      reactionTime: 150 + Math.random() * 150, // 150-300ms
      fatigueFactor: 0.001 + Math.random() * 0.002, // Slowdown over time
      focusWandering: 0.05 + Math.random() * 0.1,
      patience: 0.5 + Math.random() * 0.5
    };
  }

  /**
   * Wait with human-like variation
   */
  async humanWait(baseTime) {
    // Add fatigue effect
    const sessionDuration = Date.now() - this.sessionStartTime;
    const fatigue = 1 + (sessionDuration * this.profile.fatigueFactor / 1000);
    
    // Add random variation
    const variation = baseTime * (0.5 + Math.random());
    const actualTime = baseTime * fatigue + variation;
    
    return new Promise(resolve => setTimeout(resolve, actualTime));
  }

  /**
   * Simulate complete human interaction flow
   */
  async simulateCompleteInteraction(targetElement, text = '') {
    // Move mouse to element
    await this.mouseSimulator.moveToElement(targetElement);
    
    // Hesitation before clicking
    await this.humanWait(this.profile.reactionTime);
    
    // Click with possible miss and retry
    await this.mouseSimulator.clickElement(targetElement);
    
    // If it's an input, type text
    if (targetElement.tagName === 'INPUT' || targetElement.tagName === 'TEXTAREA') {
      await this.humanWait(200);
      await this.keyboardSimulator.typeText(text, targetElement);
    }
    
    // Record interaction
    this.recordInteraction('complete', targetElement);
  }

  /**
   * Record interaction for pattern analysis
   */
  recordInteraction(type, target) {
    const interaction = {
      type: type,
      target: target.tagName,
      timestamp: Date.now(),
      sessionTime: Date.now() - this.sessionStartTime,
      coordinates: this.getElementCoordinates(target)
    };
    
    // Store in appropriate history
    switch(type) {
      case 'mouse':
        this.mouseHistory.push(interaction);
        break;
      case 'keyboard':
        this.keyHistory.push(interaction);
        break;
      case 'scroll':
        this.scrollHistory.push(interaction);
        break;
      default:
        this.clickHistory.push(interaction);
    }
    
    // Trim history to last 100 items
    if (this.mouseHistory.length > 100) this.mouseHistory.shift();
    if (this.keyHistory.length > 100) this.keyHistory.shift();
    if (this.scrollHistory.length > 100) this.scrollHistory.shift();
    if (this.clickHistory.length > 100) this.clickHistory.shift();
  }

  /**
   * Get element coordinates
   */
  getElementCoordinates(element) {
    const rect = element.getBoundingClientRect();
    return {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2
    };
  }
}

/**
 * Mouse movement and click simulator
 */
class MouseSimulator {
  constructor(profile) {
    this.profile = profile;
    this.currentPosition = { x: 0, y: 0 };
  }

  /**
   * Generate natural bezier curve for mouse movement
   */
  generateBezierPath(start, end) {
    const distance = Math.sqrt(
      Math.pow(end.x - start.x, 2) + 
      Math.pow(end.y - start.y, 2)
    );
    
    // More control points for longer distances
    const numControlPoints = Math.min(3, Math.floor(distance / 200));
    const controlPoints = [];
    
    for (let i = 0; i < numControlPoints; i++) {
      const t = (i + 1) / (numControlPoints + 1);
      
      // Add curve with some randomness
      const perpendicular = {
        x: -(end.y - start.y) / distance,
        y: (end.x - start.x) / distance
      };
      
      const deviation = (Math.random() - 0.5) * distance * 0.2;
      
      controlPoints.push({
        x: start.x + (end.x - start.x) * t + perpendicular.x * deviation,
        y: start.y + (end.y - start.y) * t + perpendicular.y * deviation
      });
    }
    
    return { start, end, controlPoints };
  }

  /**
   * Calculate point on bezier curve
   */
  calculateBezierPoint(path, t) {
    const points = [path.start, ...path.controlPoints, path.end];
    
    while (points.length > 1) {
      const newPoints = [];
      for (let i = 0; i < points.length - 1; i++) {
        newPoints.push({
          x: points[i].x + (points[i + 1].x - points[i].x) * t,
          y: points[i].y + (points[i + 1].y - points[i].y) * t
        });
      }
      points = newPoints;
    }
    
    return points[0];
  }

  /**
   * Move mouse to element with natural movement
   */
  async moveToElement(element) {
    const target = this.getTargetPoint(element);
    await this.moveTo(target);
  }

  /**
   * Get target point on element with human inaccuracy
   */
  getTargetPoint(element) {
    const rect = element.getBoundingClientRect();
    
    // Add human inaccuracy
    const accuracy = this.profile.clickAccuracy;
    const offsetX = (Math.random() - 0.5) * rect.width * (1 - accuracy);
    const offsetY = (Math.random() - 0.5) * rect.height * (1 - accuracy);
    
    return {
      x: rect.left + rect.width / 2 + offsetX,
      y: rect.top + rect.height / 2 + offsetY
    };
  }

  /**
   * Move mouse to specific point
   */
  async moveTo(target) {
    const path = this.generateBezierPath(this.currentPosition, target);
    const distance = Math.sqrt(
      Math.pow(target.x - this.currentPosition.x, 2) + 
      Math.pow(target.y - this.currentPosition.y, 2)
    );
    
    // Calculate duration based on distance and speed
    const baseDuration = (distance / this.profile.mouseSpeed) * 1000;
    const duration = baseDuration * (0.8 + Math.random() * 0.4);
    
    const steps = Math.max(20, Math.floor(distance / 5));
    const stepDuration = duration / steps;
    
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      
      // Add acceleration curve
      const easedT = this.easeInOutCubic(t);
      
      // Calculate position on curve
      const point = this.calculateBezierPoint(path, easedT);
      
      // Add micro jitter for realism
      point.x += (Math.random() - 0.5) * 2;
      point.y += (Math.random() - 0.5) * 2;
      
      // Dispatch mouse move event
      this.dispatchMouseEvent('mousemove', point);
      
      this.currentPosition = point;
      
      await new Promise(resolve => setTimeout(resolve, stepDuration));
    }
    
    this.currentPosition = target;
  }

  /**
   * Easing function for natural acceleration
   */
  easeInOutCubic(t) {
    return t < 0.5 
      ? 4 * t * t * t 
      : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  /**
   * Click element with human-like behavior
   */
  async clickElement(element) {
    const rect = element.getBoundingClientRect();
    
    // Check if we might miss
    if (Math.random() > this.profile.clickAccuracy) {
      // Simulate miss
      const missPoint = {
        x: rect.left + Math.random() * rect.width,
        y: rect.top - 5 - Math.random() * 10
      };
      
      await this.moveTo(missPoint);
      this.dispatchMouseEvent('mousedown', missPoint);
      await new Promise(resolve => setTimeout(resolve, 50));
      this.dispatchMouseEvent('mouseup', missPoint);
      
      // Retry after realizing mistake
      await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 300));
      await this.moveToElement(element);
    }
    
    // Perform actual click
    const point = this.currentPosition;
    
    // Mouse down
    this.dispatchMouseEvent('mousedown', point);
    
    // Hold duration
    await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 100));
    
    // Slight movement while pressed (human tremor)
    if (Math.random() > 0.7) {
      point.x += (Math.random() - 0.5) * 2;
      point.y += (Math.random() - 0.5) * 2;
      this.dispatchMouseEvent('mousemove', point);
    }
    
    // Mouse up
    this.dispatchMouseEvent('mouseup', point);
    
    // Click event
    this.dispatchMouseEvent('click', point);
    
    // Focus element
    if (element.focus) {
      element.focus();
    }
  }

  /**
   * Dispatch realistic mouse event
   */
  dispatchMouseEvent(type, point) {
    const event = new MouseEvent(type, {
      view: window,
      bubbles: true,
      cancelable: true,
      clientX: point.x,
      clientY: point.y,
      screenX: point.x + window.screenX,
      screenY: point.y + window.screenY,
      button: 0,
      buttons: type === 'mousedown' ? 1 : 0,
      relatedTarget: null,
      movementX: 0,
      movementY: 0
    });
    
    // Find element at point
    const element = document.elementFromPoint(point.x, point.y);
    if (element) {
      element.dispatchEvent(event);
    } else {
      document.dispatchEvent(event);
    }
  }
}

/**
 * Keyboard input simulator
 */
class KeyboardSimulator {
  constructor(profile) {
    this.profile = profile;
    this.capsLockOn = false;
    this.shiftPressed = false;
  }

  /**
   * Type text with human-like patterns
   */
  async typeText(text, element) {
    element.focus();
    
    // Clear existing text if needed
    if (element.value) {
      await this.selectAll(element);
      await this.deleteSelection(element);
    }
    
    const words = text.split(' ');
    
    for (let wordIndex = 0; wordIndex < words.length; wordIndex++) {
      const word = words[wordIndex];
      
      // Thinking pause before some words
      if (Math.random() < this.profile.thinkingPauseChance) {
        await new Promise(resolve => 
          setTimeout(resolve, 500 + Math.random() * 1500)
        );
      }
      
      // Type the word
      for (let charIndex = 0; charIndex < word.length; charIndex++) {
        const char = word[charIndex];
        
        // Simulate typo
        if (Math.random() < this.profile.typoRate) {
          const typo = this.generateTypo(char);
          await this.typeCharacter(typo, element);
          
          // Realize mistake after a moment
          await new Promise(resolve => 
            setTimeout(resolve, 100 + Math.random() * 300)
          );
          
          // Backspace
          await this.pressKey('Backspace', element);
        }
        
        // Type correct character
        await this.typeCharacter(char, element);
        
        // Variable typing speed
        const baseDelay = 60000 / (this.profile.typingSpeed * 5);
        const variation = baseDelay * (0.5 + Math.random());
        await new Promise(resolve => setTimeout(resolve, variation));
      }
      
      // Add space between words
      if (wordIndex < words.length - 1) {
        await this.typeCharacter(' ', element);
        
        // Pause between words
        await new Promise(resolve => 
          setTimeout(resolve, this.profile.pauseBetweenWords * (0.5 + Math.random()))
        );
      }
    }
  }

  /**
   * Generate realistic typo
   */
  generateTypo(char) {
    // Adjacent keys on QWERTY keyboard
    const adjacentKeys = {
      'a': ['q', 'w', 's', 'z'],
      'b': ['v', 'g', 'h', 'n'],
      'c': ['x', 'd', 'f', 'v'],
      'd': ['s', 'e', 'r', 'f', 'c', 'x'],
      'e': ['w', 'r', 'd', 's'],
      'f': ['d', 'r', 't', 'g', 'v', 'c'],
      'g': ['f', 't', 'y', 'h', 'b', 'v'],
      'h': ['g', 'y', 'u', 'j', 'n', 'b'],
      'i': ['u', 'o', 'k', 'j'],
      'j': ['h', 'u', 'i', 'k', 'm', 'n'],
      'k': ['j', 'i', 'o', 'l', 'm'],
      'l': ['k', 'o', 'p', ';'],
      'm': ['n', 'j', 'k', ','],
      'n': ['b', 'h', 'j', 'm'],
      'o': ['i', 'p', 'l', 'k'],
      'p': ['o', '[', ';', 'l'],
      'q': ['w', 'a'],
      'r': ['e', 't', 'f', 'd'],
      's': ['a', 'w', 'e', 'd', 'x', 'z'],
      't': ['r', 'y', 'g', 'f'],
      'u': ['y', 'i', 'j', 'h'],
      'v': ['c', 'f', 'g', 'b'],
      'w': ['q', 'e', 's', 'a'],
      'x': ['z', 's', 'd', 'c'],
      'y': ['t', 'u', 'h', 'g'],
      'z': ['a', 's', 'x']
    };
    
    const lowerChar = char.toLowerCase();
    const adjacent = adjacentKeys[lowerChar];
    
    if (adjacent && adjacent.length > 0) {
      const typo = adjacent[Math.floor(Math.random() * adjacent.length)];
      return char === lowerChar ? typo : typo.toUpperCase();
    }
    
    return char;
  }

  /**
   * Type a single character
   */
  async typeCharacter(char, element) {
    const needsShift = this.needsShiftKey(char);
    
    if (needsShift && !this.shiftPressed) {
      await this.pressKey('Shift', element, true);
      this.shiftPressed = true;
    }
    
    await this.pressKey(char, element);
    
    if (needsShift && this.shiftPressed) {
      await this.releaseKey('Shift', element);
      this.shiftPressed = false;
    }
    
    // Update input value
    const currentValue = element.value || '';
    element.value = currentValue + char;
    
    // Trigger input event
    element.dispatchEvent(new Event('input', { bubbles: true }));
  }

  /**
   * Check if character needs shift key
   */
  needsShiftKey(char) {
    return char !== char.toLowerCase() || 
           '!@#$%^&*()_+{}|:"<>?~'.includes(char);
  }

  /**
   * Press a key
   */
  async pressKey(key, element, holdDown = false) {
    const keyCode = this.getKeyCode(key);
    
    const keydownEvent = new KeyboardEvent('keydown', {
      key: key,
      code: `Key${key.toUpperCase()}`,
      keyCode: keyCode,
      which: keyCode,
      shiftKey: this.shiftPressed,
      bubbles: true,
      cancelable: true
    });
    
    element.dispatchEvent(keydownEvent);
    
    if (!holdDown) {
      // Key press duration
      await new Promise(resolve => 
        setTimeout(resolve, 30 + Math.random() * 50)
      );
      
      await this.releaseKey(key, element);
    }
  }

  /**
   * Release a key
   */
  async releaseKey(key, element) {
    const keyCode = this.getKeyCode(key);
    
    const keyupEvent = new KeyboardEvent('keyup', {
      key: key,
      code: `Key${key.toUpperCase()}`,
      keyCode: keyCode,
      which: keyCode,
      shiftKey: this.shiftPressed,
      bubbles: true,
      cancelable: true
    });
    
    element.dispatchEvent(keyupEvent);
  }

  /**
   * Get key code for character
   */
  getKeyCode(key) {
    const keyCodes = {
      'Backspace': 8,
      'Tab': 9,
      'Enter': 13,
      'Shift': 16,
      'Control': 17,
      'Alt': 18,
      'Escape': 27,
      ' ': 32,
      'Delete': 46
    };
    
    return keyCodes[key] || key.toUpperCase().charCodeAt(0);
  }

  /**
   * Select all text
   */
  async selectAll(element) {
    element.select();
    
    // Simulate Ctrl+A
    await this.pressKey('Control', element, true);
    await this.pressKey('a', element);
    await this.releaseKey('Control', element);
  }

  /**
   * Delete selected text
   */
  async deleteSelection(element) {
    await this.pressKey('Delete', element);
    element.value = '';
  }
}

/**
 * Scroll behavior simulator
 */
class ScrollSimulator {
  constructor(profile) {
    this.profile = profile;
    this.currentScrollY = window.scrollY;
  }

  /**
   * Simulate reading with natural scroll
   */
  async simulateReading(duration = 5000) {
    const startTime = Date.now();
    const contentHeight = document.body.scrollHeight - window.innerHeight;
    
    while (Date.now() - startTime < duration) {
      // Determine scroll amount based on reading speed
      const wordsVisible = this.estimateVisibleWords();
      const readTime = (wordsVisible / this.profile.readingSpeed) * 60000;
      
      await new Promise(resolve => setTimeout(resolve, readTime));
      
      // Scroll down
      const scrollAmount = 100 + Math.random() * 200;
      await this.smoothScroll(scrollAmount);
      
      // Occasional pause (re-reading)
      if (Math.random() < this.profile.scrollPauseChance) {
        await new Promise(resolve => 
          setTimeout(resolve, 1000 + Math.random() * 2000)
        );
        
        // Sometimes scroll back up
        if (Math.random() < 0.3) {
          await this.smoothScroll(-scrollAmount / 2);
        }
      }
      
      // Check if reached bottom
      if (window.scrollY + window.innerHeight >= contentHeight) {
        break;
      }
    }
  }

  /**
   * Estimate visible words on screen
   */
  estimateVisibleWords() {
    const viewportHeight = window.innerHeight;
    const averageLineHeight = 20;
    const averageWordsPerLine = 10;
    
    const visibleLines = viewportHeight / averageLineHeight;
    return visibleLines * averageWordsPerLine;
  }

  /**
   * Smooth scroll to position
   */
  async smoothScroll(distance) {
    const steps = 20;
    const stepDistance = distance / steps;
    const stepDuration = 20;
    
    for (let i = 0; i < steps; i++) {
      const t = i / steps;
      const eased = this.easeInOutQuad(t);
      const currentStep = stepDistance * eased;
      
      window.scrollBy(0, currentStep);
      
      // Dispatch scroll event
      window.dispatchEvent(new Event('scroll', { bubbles: true }));
      
      await new Promise(resolve => setTimeout(resolve, stepDuration));
    }
    
    this.currentScrollY = window.scrollY;
  }

  /**
   * Easing function for smooth scroll
   */
  easeInOutQuad(t) {
    return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
  }

  /**
   * Simulate mouse wheel scroll
   */
  async wheelScroll(deltaY) {
    const event = new WheelEvent('wheel', {
      deltaY: deltaY,
      deltaMode: WheelEvent.DOM_DELTA_PIXEL,
      bubbles: true,
      cancelable: true
    });
    
    document.dispatchEvent(event);
    window.scrollBy(0, deltaY);
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = HumanBehaviorSimulator;
} else if (typeof window !== 'undefined') {
  window.HumanBehaviorSimulator = HumanBehaviorSimulator;
}