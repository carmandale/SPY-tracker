#!/usr/bin/env node

/**
 * Generate app icons for PWA manifest
 * Creates simple colored squares as placeholders
 */

import fs from 'fs';
import path from 'path';

const publicDir = path.join(process.cwd(), 'public');
const iconsDir = path.join(publicDir, 'icons');

// Create icons directory
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

// SVG template for app icon
const createIconSVG = size =>
  `
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="${size}" height="${size}" fill="#006072"/>
  <rect x="${size * 0.15}" y="${size * 0.15}" width="${size * 0.7}" height="${size * 0.7}" fill="#0B0D12" rx="${size * 0.1}"/>
  <text x="${size * 0.5}" y="${size * 0.6}" text-anchor="middle" fill="#E8ECF2" font-family="Arial, sans-serif" font-size="${size * 0.25}" font-weight="bold">SPY</text>
</svg>
`.trim();

// Create icons for different sizes
const iconSizes = [192, 512];

iconSizes.forEach(size => {
  const svgContent = createIconSVG(size);
  const iconPath = path.join(iconsDir, `icon-${size}x${size}.svg`);

  fs.writeFileSync(iconPath, svgContent);
  console.log(`✅ Created ${iconPath}`);
});

// Create maskable icon (same design but with safe zone)
const createMaskableIconSVG = size =>
  `
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="${size}" height="${size}" fill="#006072"/>
  <rect x="${size * 0.2}" y="${size * 0.2}" width="${size * 0.6}" height="${size * 0.6}" fill="#0B0D12" rx="${size * 0.08}"/>
  <text x="${size * 0.5}" y="${size * 0.58}" text-anchor="middle" fill="#E8ECF2" font-family="Arial, sans-serif" font-size="${size * 0.2}" font-weight="bold">SPY</text>
</svg>
`.trim();

// Create maskable icon
const maskableIconPath = path.join(iconsDir, 'icon-512x512-maskable.svg');
fs.writeFileSync(maskableIconPath, createMaskableIconSVG(512));
console.log(`✅ Created maskable icon: ${maskableIconPath}`);

console.log('\n🎉 App icons generated successfully!');
console.log('Note: SVG icons are used as placeholders. For production, convert to PNG format.');
