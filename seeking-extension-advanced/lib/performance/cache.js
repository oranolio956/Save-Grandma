/**
 * Complete High-Performance Caching System
 * Full implementation with LRU, TTL, and intelligent eviction
 */

class PerformanceCache {
  constructor(options = {}) {
    this.maxSize = options.maxSize || 1000;
    this.maxMemory = options.maxMemory || 50 * 1024 * 1024; // 50MB
    this.defaultTTL = options.defaultTTL || 3600000; // 1 hour
    
    this.cache = new Map();
    this.metadata = new Map();
    this.accessOrder = [];
    this.memoryUsage = 0;
    
    this.stats = {
      hits: 0,
      misses: 0,
      evictions: 0,
      sets: 0,
      deletes: 0,
      memoryPeak: 0
    };

    this.initializeCleanupTimer();
  }

  /**
   * Calculate size of JavaScript object in bytes
   */
  getObjectSize(obj) {
    let size = 0;
    
    if (obj === null || obj === undefined) {
      return 4;
    }
    
    switch (typeof obj) {
      case 'boolean':
        size = 4;
        break;
      case 'number':
        size = 8;
        break;
      case 'string':
        size = 2 * obj.length;
        break;
      case 'object':
        if (obj instanceof ArrayBuffer) {
          size = obj.byteLength;
        } else if (obj instanceof Array) {
          for (let item of obj) {
            size += this.getObjectSize(item);
          }
        } else {
          for (let key in obj) {
            if (obj.hasOwnProperty(key)) {
              size += 2 * key.length;
              size += this.getObjectSize(obj[key]);
            }
          }
        }
        break;
    }
    
    return size;
  }

  /**
   * Set value in cache with metadata
   */
  set(key, value, options = {}) {
    const ttl = options.ttl || this.defaultTTL;
    const priority = options.priority || 0;
    const tags = options.tags || [];
    
    // Calculate memory size
    const size = this.getObjectSize(value);
    
    // Check memory limit
    if (this.memoryUsage + size > this.maxMemory) {
      this.evictByMemory(size);
    }
    
    // Check size limit
    if (this.cache.size >= this.maxSize) {
      this.evictLRU();
    }
    
    // Remove old entry if exists
    if (this.cache.has(key)) {
      this.delete(key);
    }
    
    // Store value and metadata
    this.cache.set(key, value);
    this.metadata.set(key, {
      size: size,
      timestamp: Date.now(),
      expiry: Date.now() + ttl,
      hits: 0,
      priority: priority,
      tags: tags,
      lastAccess: Date.now()
    });
    
    // Update access order
    this.updateAccessOrder(key);
    
    // Update memory usage
    this.memoryUsage += size;
    if (this.memoryUsage > this.stats.memoryPeak) {
      this.stats.memoryPeak = this.memoryUsage;
    }
    
    this.stats.sets++;
    
    return true;
  }

  /**
   * Get value from cache
   */
  get(key) {
    if (!this.cache.has(key)) {
      this.stats.misses++;
      return null;
    }
    
    const metadata = this.metadata.get(key);
    
    // Check expiry
    if (Date.now() > metadata.expiry) {
      this.delete(key);
      this.stats.misses++;
      return null;
    }
    
    // Update metadata
    metadata.hits++;
    metadata.lastAccess = Date.now();
    
    // Update access order
    this.updateAccessOrder(key);
    
    this.stats.hits++;
    
    return this.cache.get(key);
  }

  /**
   * Delete entry from cache
   */
  delete(key) {
    if (!this.cache.has(key)) {
      return false;
    }
    
    const metadata = this.metadata.get(key);
    
    // Update memory usage
    this.memoryUsage -= metadata.size;
    
    // Remove from cache and metadata
    this.cache.delete(key);
    this.metadata.delete(key);
    
    // Remove from access order
    const index = this.accessOrder.indexOf(key);
    if (index > -1) {
      this.accessOrder.splice(index, 1);
    }
    
    this.stats.deletes++;
    
    return true;
  }

  /**
   * Update access order for LRU
   */
  updateAccessOrder(key) {
    const index = this.accessOrder.indexOf(key);
    if (index > -1) {
      this.accessOrder.splice(index, 1);
    }
    this.accessOrder.push(key);
  }

  /**
   * Evict least recently used item
   */
  evictLRU() {
    if (this.accessOrder.length === 0) {
      return;
    }
    
    // Find least recently used item with lowest priority
    let evictKey = null;
    let lowestScore = Infinity;
    
    for (let i = 0; i < Math.min(10, this.accessOrder.length); i++) {
      const key = this.accessOrder[i];
      const metadata = this.metadata.get(key);
      
      // Calculate eviction score (lower = more likely to evict)
      const age = Date.now() - metadata.lastAccess;
      const score = (metadata.hits * metadata.priority * 1000) / (age + 1);
      
      if (score < lowestScore) {
        lowestScore = score;
        evictKey = key;
      }
    }
    
    if (evictKey) {
      this.delete(evictKey);
      this.stats.evictions++;
    }
  }

  /**
   * Evict items to free up memory
   */
  evictByMemory(requiredSize) {
    const candidates = [];
    
    // Collect eviction candidates
    for (const [key, metadata] of this.metadata.entries()) {
      candidates.push({
        key: key,
        score: this.calculateEvictionScore(metadata),
        size: metadata.size
      });
    }
    
    // Sort by eviction score (lower = evict first)
    candidates.sort((a, b) => a.score - b.score);
    
    let freedMemory = 0;
    for (const candidate of candidates) {
      if (freedMemory >= requiredSize) {
        break;
      }
      
      this.delete(candidate.key);
      freedMemory += candidate.size;
      this.stats.evictions++;
    }
  }

  /**
   * Calculate eviction score for an item
   */
  calculateEvictionScore(metadata) {
    const age = Date.now() - metadata.timestamp;
    const recency = Date.now() - metadata.lastAccess;
    const timeToExpiry = metadata.expiry - Date.now();
    
    // Higher score = keep in cache
    return (metadata.hits * metadata.priority * timeToExpiry) / 
           (age * recency * metadata.size + 1);
  }

  /**
   * Clear all cache entries
   */
  clear() {
    this.cache.clear();
    this.metadata.clear();
    this.accessOrder = [];
    this.memoryUsage = 0;
  }

  /**
   * Get cache statistics
   */
  getStats() {
    const hitRate = this.stats.hits / (this.stats.hits + this.stats.misses) || 0;
    
    return {
      ...this.stats,
      hitRate: (hitRate * 100).toFixed(2) + '%',
      size: this.cache.size,
      memoryUsage: this.formatBytes(this.memoryUsage),
      memoryPeak: this.formatBytes(this.stats.memoryPeak),
      averageSize: this.formatBytes(this.memoryUsage / this.cache.size || 0)
    };
  }

  /**
   * Format bytes to human readable
   */
  formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Initialize cleanup timer
   */
  initializeCleanupTimer() {
    setInterval(() => {
      this.cleanup();
    }, 60000); // Run every minute
  }

  /**
   * Clean up expired entries
   */
  cleanup() {
    const now = Date.now();
    const keysToDelete = [];
    
    for (const [key, metadata] of this.metadata.entries()) {
      if (now > metadata.expiry) {
        keysToDelete.push(key);
      }
    }
    
    for (const key of keysToDelete) {
      this.delete(key);
    }
  }

  /**
   * Get entries by tag
   */
  getByTag(tag) {
    const results = [];
    
    for (const [key, metadata] of this.metadata.entries()) {
      if (metadata.tags.includes(tag)) {
        const value = this.get(key);
        if (value !== null) {
          results.push({ key, value });
        }
      }
    }
    
    return results;
  }

  /**
   * Invalidate entries by tag
   */
  invalidateByTag(tag) {
    const keysToDelete = [];
    
    for (const [key, metadata] of this.metadata.entries()) {
      if (metadata.tags.includes(tag)) {
        keysToDelete.push(key);
      }
    }
    
    for (const key of keysToDelete) {
      this.delete(key);
    }
    
    return keysToDelete.length;
  }

  /**
   * Warm up cache with preloaded data
   */
  warmUp(entries) {
    for (const { key, value, options } of entries) {
      this.set(key, value, options);
    }
  }

  /**
   * Export cache state for persistence
   */
  export() {
    const entries = [];
    
    for (const [key, value] of this.cache.entries()) {
      const metadata = this.metadata.get(key);
      entries.push({
        key,
        value,
        metadata
      });
    }
    
    return {
      entries,
      stats: this.stats,
      timestamp: Date.now()
    };
  }

  /**
   * Import cache state from persistence
   */
  import(data) {
    this.clear();
    
    const now = Date.now();
    
    for (const { key, value, metadata } of data.entries) {
      // Adjust expiry based on time passed
      const timePassed = now - data.timestamp;
      const newExpiry = metadata.expiry - timePassed;
      
      if (newExpiry > now) {
        this.set(key, value, {
          ttl: newExpiry - now,
          priority: metadata.priority,
          tags: metadata.tags
        });
        
        // Restore hit count
        const restoredMetadata = this.metadata.get(key);
        if (restoredMetadata) {
          restoredMetadata.hits = metadata.hits;
        }
      }
    }
    
    // Restore stats
    if (data.stats) {
      this.stats = { ...this.stats, ...data.stats };
    }
  }
}

// Specialized DOM cache for element references
class DOMCache extends PerformanceCache {
  constructor(options = {}) {
    super(options);
    this.observedElements = new WeakMap();
    this.setupMutationObserver();
  }

  /**
   * Cache DOM element with automatic invalidation
   */
  setElement(selector, element, options = {}) {
    if (!element || !element.isConnected) {
      return false;
    }
    
    // Store selector as key, element reference as value
    this.set(selector, {
      element: element,
      selector: selector,
      timestamp: Date.now()
    }, options);
    
    // Setup observation for changes
    this.observeElement(element, selector);
    
    return true;
  }

  /**
   * Get cached DOM element
   */
  getElement(selector) {
    const cached = this.get(selector);
    
    if (!cached) {
      // Try to find element
      const element = document.querySelector(selector);
      if (element) {
        this.setElement(selector, element);
        return element;
      }
      return null;
    }
    
    // Validate element is still in DOM
    if (cached.element && cached.element.isConnected) {
      return cached.element;
    }
    
    // Element removed from DOM, invalidate cache
    this.delete(selector);
    
    // Try to find element again
    const element = document.querySelector(selector);
    if (element) {
      this.setElement(selector, element);
      return element;
    }
    
    return null;
  }

  /**
   * Setup mutation observer for automatic cache invalidation
   */
  setupMutationObserver() {
    this.observer = new MutationObserver((mutations) => {
      const invalidatedSelectors = new Set();
      
      for (const mutation of mutations) {
        // Check if any cached elements were removed
        for (const node of mutation.removedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            this.checkRemovedElement(node, invalidatedSelectors);
          }
        }
      }
      
      // Invalidate affected cache entries
      for (const selector of invalidatedSelectors) {
        this.delete(selector);
      }
    });
    
    // Start observing
    if (document.body) {
      this.observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    }
  }

  /**
   * Check if removed element affects cache
   */
  checkRemovedElement(element, invalidatedSelectors) {
    for (const [selector, cached] of this.cache.entries()) {
      if (cached.element === element || element.contains(cached.element)) {
        invalidatedSelectors.add(selector);
      }
    }
  }

  /**
   * Observe element for changes
   */
  observeElement(element, selector) {
    if (this.observedElements.has(element)) {
      return;
    }
    
    const observer = new MutationObserver(() => {
      // Element changed, invalidate cache
      this.delete(selector);
    });
    
    observer.observe(element, {
      attributes: true,
      characterData: true,
      childList: true
    });
    
    this.observedElements.set(element, observer);
  }

  /**
   * Clean up observers
   */
  destroy() {
    if (this.observer) {
      this.observer.disconnect();
    }
    
    this.clear();
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { PerformanceCache, DOMCache };
} else if (typeof window !== 'undefined') {
  window.PerformanceCache = PerformanceCache;
  window.DOMCache = DOMCache;
}