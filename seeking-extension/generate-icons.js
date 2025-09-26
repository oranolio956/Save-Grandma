// Simple script to generate placeholder icons using Canvas API
// Run this in a browser console or Node.js with canvas package

const sizes = [16, 48, 128];

function generateIcon(size) {
  // This creates a simple SVG icon as a data URL
  const svg = `
    <svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="${size}" height="${size}" rx="${size/8}" fill="url(#grad)"/>
      <text x="50%" y="50%" text-anchor="middle" dy=".3em" 
            font-family="Arial, sans-serif" 
            font-size="${size * 0.4}px" 
            font-weight="bold" 
            fill="white">S</text>
    </svg>
  `;
  
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

// Instructions for creating icons
console.log(`
To create icon files:

1. Create simple PNG icons manually or use an online tool
2. Or use this SVG data in your HTML for testing:

Icon 16x16:
${generateIcon(16)}

Icon 48x48:
${generateIcon(48)}

Icon 128x128:
${generateIcon(128)}

You can convert these to PNG using an online converter or image editor.
`);