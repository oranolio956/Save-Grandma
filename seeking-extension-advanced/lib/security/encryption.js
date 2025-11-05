/**
 * Complete AES-256-GCM Encryption Implementation
 * No placeholders - fully functional encryption system
 */

class SecureStorage {
  constructor() {
    this.algorithm = 'AES-GCM';
    this.keyLength = 256;
    this.saltLength = 32;
    this.ivLength = 16;
    this.tagLength = 128;
    this.iterations = 100000;
    this.masterKey = null;
  }

  /**
   * Generate cryptographically secure random bytes
   */
  generateRandomBytes(length) {
    return crypto.getRandomValues(new Uint8Array(length));
  }

  /**
   * Convert ArrayBuffer to Base64
   */
  arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Convert Base64 to ArrayBuffer
   */
  base64ToArrayBuffer(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }

  /**
   * Derive encryption key from password using PBKDF2
   */
  async deriveKey(password, salt) {
    const encoder = new TextEncoder();
    const passwordBuffer = encoder.encode(password);
    
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      passwordBuffer,
      { name: 'PBKDF2' },
      false,
      ['deriveBits', 'deriveKey']
    );

    const key = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: salt,
        iterations: this.iterations,
        hash: 'SHA-256'
      },
      keyMaterial,
      {
        name: this.algorithm,
        length: this.keyLength
      },
      true,
      ['encrypt', 'decrypt']
    );

    return key;
  }

  /**
   * Get or create master key for encryption
   */
  async getOrCreateMasterKey() {
    if (this.masterKey) {
      return this.masterKey;
    }

    try {
      // Try to retrieve existing key from chrome.storage
      const stored = await chrome.storage.local.get(['encryptionKey', 'salt']);
      
      if (stored.encryptionKey && stored.salt) {
        // Reconstruct key from stored data
        const salt = new Uint8Array(stored.salt);
        const keyData = await crypto.subtle.importKey(
          'raw',
          new Uint8Array(stored.encryptionKey),
          { name: this.algorithm, length: this.keyLength },
          true,
          ['encrypt', 'decrypt']
        );
        this.masterKey = keyData;
        return keyData;
      }
    } catch (error) {
      console.log('No existing key found, generating new one');
    }

    // Generate new key
    const key = await crypto.subtle.generateKey(
      {
        name: this.algorithm,
        length: this.keyLength
      },
      true,
      ['encrypt', 'decrypt']
    );

    // Export and store key
    const exportedKey = await crypto.subtle.exportKey('raw', key);
    const keyArray = Array.from(new Uint8Array(exportedKey));
    
    await chrome.storage.local.set({
      encryptionKey: keyArray,
      salt: Array.from(this.generateRandomBytes(this.saltLength))
    });

    this.masterKey = key;
    return key;
  }

  /**
   * Encrypt data with AES-256-GCM
   */
  async encrypt(data) {
    const key = await this.getOrCreateMasterKey();
    const iv = this.generateRandomBytes(this.ivLength);
    
    const encoder = new TextEncoder();
    const encodedData = encoder.encode(JSON.stringify(data));

    const encryptedData = await crypto.subtle.encrypt(
      {
        name: this.algorithm,
        iv: iv,
        tagLength: this.tagLength
      },
      key,
      encodedData
    );

    // Combine IV and encrypted data for storage
    const combined = new Uint8Array(iv.length + encryptedData.byteLength);
    combined.set(iv, 0);
    combined.set(new Uint8Array(encryptedData), iv.length);

    return this.arrayBufferToBase64(combined.buffer);
  }

  /**
   * Decrypt data with AES-256-GCM
   */
  async decrypt(encryptedString) {
    const key = await this.getOrCreateMasterKey();
    const combined = new Uint8Array(this.base64ToArrayBuffer(encryptedString));
    
    // Extract IV and encrypted data
    const iv = combined.slice(0, this.ivLength);
    const encryptedData = combined.slice(this.ivLength);

    const decryptedData = await crypto.subtle.decrypt(
      {
        name: this.algorithm,
        iv: iv,
        tagLength: this.tagLength
      },
      key,
      encryptedData
    );

    const decoder = new TextDecoder();
    const jsonString = decoder.decode(decryptedData);
    return JSON.parse(jsonString);
  }

  /**
   * Secure storage operations
   */
  async secureSet(key, value) {
    const encrypted = await this.encrypt(value);
    await chrome.storage.local.set({
      [`encrypted_${key}`]: encrypted
    });
  }

  async secureGet(key) {
    const result = await chrome.storage.local.get([`encrypted_${key}`]);
    const encrypted = result[`encrypted_${key}`];
    
    if (!encrypted) {
      return null;
    }

    return await this.decrypt(encrypted);
  }

  async secureRemove(key) {
    await chrome.storage.local.remove([`encrypted_${key}`]);
  }

  async secureClear() {
    const items = await chrome.storage.local.get(null);
    const encryptedKeys = Object.keys(items).filter(k => k.startsWith('encrypted_'));
    await chrome.storage.local.remove(encryptedKeys);
  }

  /**
   * Hash sensitive data with SHA-256
   */
  async hash(data) {
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    return this.arrayBufferToBase64(hashBuffer);
  }

  /**
   * Generate secure random token
   */
  generateSecureToken(length = 32) {
    const bytes = this.generateRandomBytes(length);
    return this.arrayBufferToBase64(bytes.buffer);
  }

  /**
   * Time-based One-Time Password (TOTP) implementation
   */
  async generateTOTP(secret, timeStep = 30) {
    const time = Math.floor(Date.now() / 1000 / timeStep);
    const timeBuffer = new ArrayBuffer(8);
    const timeView = new DataView(timeBuffer);
    timeView.setUint32(4, time, false);

    const keyBuffer = this.base64ToArrayBuffer(secret);
    const key = await crypto.subtle.importKey(
      'raw',
      keyBuffer,
      { name: 'HMAC', hash: 'SHA-1' },
      false,
      ['sign']
    );

    const signature = await crypto.subtle.sign('HMAC', key, timeBuffer);
    const signatureArray = new Uint8Array(signature);
    
    const offset = signatureArray[signatureArray.length - 1] & 0xf;
    const binary = 
      ((signatureArray[offset] & 0x7f) << 24) |
      ((signatureArray[offset + 1] & 0xff) << 16) |
      ((signatureArray[offset + 2] & 0xff) << 8) |
      (signatureArray[offset + 3] & 0xff);
    
    const otp = binary % 1000000;
    return otp.toString().padStart(6, '0');
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SecureStorage;
} else if (typeof window !== 'undefined') {
  window.SecureStorage = SecureStorage;
}