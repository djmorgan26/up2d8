#!/usr/bin/env node

/**
 * Generate PWA icons from SVG
 * This script creates PNG icons in various sizes for PWA support
 *
 * Note: For production, you should use proper design tools or services like:
 * - https://realfavicongenerator.net/
 * - https://www.pwabuilder.com/imageGenerator
 * - Adobe Photoshop/Illustrator
 *
 * This script creates placeholder icons using sharp (if available)
 */

const fs = require('fs');
const path = require('path');

const ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512];
const ICONS_DIR = path.join(__dirname, '../public/icons');

// Create icons directory if it doesn't exist
if (!fs.existsSync(ICONS_DIR)) {
  fs.mkdirSync(ICONS_DIR, { recursive: true });
  console.log('✅ Created icons directory');
}

// Check if sharp is available
let sharp;
try {
  sharp = require('sharp');
  console.log('✅ sharp library found, generating high-quality icons...');
} catch (error) {
  console.log('⚠️  sharp library not found. Installing...');
  console.log('   Run: npm install --save-dev sharp');
  console.log('   For now, creating placeholder files...');
  sharp = null;
}

const sourceSvg = path.join(__dirname, '../public/icon-light.svg');

if (!fs.existsSync(sourceSvg)) {
  console.error('❌ Source SVG not found at:', sourceSvg);
  console.log('   Creating placeholder icons instead...');
  createPlaceholders();
} else if (sharp) {
  generateIcons();
} else {
  createPlaceholders();
}

async function generateIcons() {
  try {
    for (const size of ICON_SIZES) {
      const outputPath = path.join(ICONS_DIR, `icon-${size}x${size}.png`);

      await sharp(sourceSvg)
        .resize(size, size, {
          fit: 'contain',
          background: { r: 59, g: 130, b: 246, alpha: 1 } // #3B82F6
        })
        .png()
        .toFile(outputPath);

      console.log(`✅ Generated ${size}x${size} icon`);
    }

    console.log('🎉 All icons generated successfully!');
  } catch (error) {
    console.error('❌ Error generating icons:', error.message);
    console.log('   Creating placeholder files instead...');
    createPlaceholders();
  }
}

function createPlaceholders() {
  // Create simple placeholder files
  for (const size of ICON_SIZES) {
    const outputPath = path.join(ICONS_DIR, `icon-${size}x${size}.png`);

    // Create empty file
    fs.writeFileSync(outputPath, '');
    console.log(`📝 Created placeholder for ${size}x${size} icon`);
  }

  console.log('');
  console.log('⚠️  IMPORTANT: Replace placeholder icons with real ones!');
  console.log('   Options:');
  console.log('   1. Install sharp: npm install --save-dev sharp && npm run generate-icons');
  console.log('   2. Use online tools: https://realfavicongenerator.net/');
  console.log('   3. Use PWA Builder: https://www.pwabuilder.com/imageGenerator');
  console.log('');
}
