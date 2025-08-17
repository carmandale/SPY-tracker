/**
 * Tests for PWA manifest.json validation and configuration
 */
import { describe, it, expect, beforeEach } from 'vitest';
import fs from 'fs';
import path from 'path';

interface WebAppManifest {
  name: string;
  short_name: string;
  description: string;
  start_url: string;
  scope: string;
  display: string;
  theme_color: string;
  background_color: string;
  orientation: string;
  icons: {
    src: string;
    sizes: string;
    type: string;
    purpose?: string;
  }[];
}

describe('PWA Manifest Configuration', () => {
  let manifest: WebAppManifest;

  beforeEach(() => {
    // Read the manifest.json file from public directory
    const manifestPath = path.join(process.cwd(), 'public', 'manifest.json');

    if (!fs.existsSync(manifestPath)) {
      throw new Error('Manifest file not found');
    }

    const manifestContent = fs.readFileSync(manifestPath, 'utf-8');
    manifest = JSON.parse(manifestContent);
  });

  describe('Required Fields', () => {
    it('should have a name field', () => {
      expect(manifest.name).toBeDefined();
      expect(typeof manifest.name).toBe('string');
      expect(manifest.name.length).toBeGreaterThan(0);
    });

    it('should have a short_name field', () => {
      expect(manifest.short_name).toBeDefined();
      expect(typeof manifest.short_name).toBe('string');
      expect(manifest.short_name.length).toBeGreaterThan(0);
    });

    it('should have a description field', () => {
      expect(manifest.description).toBeDefined();
      expect(typeof manifest.description).toBe('string');
      expect(manifest.description.length).toBeGreaterThan(0);
    });

    it('should have a start_url field', () => {
      expect(manifest.start_url).toBeDefined();
      expect(typeof manifest.start_url).toBe('string');
    });

    it('should have a scope field', () => {
      expect(manifest.scope).toBeDefined();
      expect(typeof manifest.scope).toBe('string');
    });

    it('should have a display mode', () => {
      expect(manifest.display).toBeDefined();
      expect(['standalone', 'fullscreen', 'minimal-ui', 'browser']).toContain(manifest.display);
    });
  });

  describe('SPY Tracker Branding', () => {
    it('should have SPY TA Tracker as the app name', () => {
      expect(manifest.name).toBe('SPY TA Tracker');
    });

    it('should have a short name suitable for home screen', () => {
      expect(manifest.short_name).toBe('SPY Tracker');
      expect(manifest.short_name.length).toBeLessThanOrEqual(12);
    });

    it('should have a trading-focused description', () => {
      expect(manifest.description).toContain('SPY');
      expect(manifest.description.toLowerCase()).toMatch(/track|trading|predict|options/);
    });

    it('should use SPY Tracker theme colors', () => {
      expect(manifest.theme_color).toBe('#0B0D12');
      expect(manifest.background_color).toBe('#0B0D12');
    });
  });

  describe('PWA Configuration', () => {
    it('should use standalone display mode for native app feel', () => {
      expect(manifest.display).toBe('standalone');
    });

    it('should start at root URL', () => {
      expect(manifest.start_url).toBe('/');
    });

    it('should scope to entire app', () => {
      expect(manifest.scope).toBe('/');
    });

    it('should prefer portrait orientation for mobile', () => {
      expect(manifest.orientation).toBe('portrait-primary');
    });
  });

  describe('App Icons', () => {
    it('should have at least one icon', () => {
      expect(manifest.icons).toBeDefined();
      expect(Array.isArray(manifest.icons)).toBe(true);
      expect(manifest.icons.length).toBeGreaterThan(0);
    });

    it('should include required icon sizes', () => {
      const requiredSizes = ['192x192', '512x512'];

      requiredSizes.forEach(size => {
        const hasSize = manifest.icons.some(icon => icon.sizes === size);
        expect(hasSize, `Missing required icon size: ${size}`).toBe(true);
      });
    });

    it('should have PNG format icons', () => {
      manifest.icons.forEach(icon => {
        expect(icon.type).toBe('image/png');
      });
    });

    it('should include maskable icon for adaptive displays', () => {
      const hasMaskableIcon = manifest.icons.some(icon => icon.purpose?.includes('maskable'));
      expect(hasMaskableIcon).toBe(true);
    });

    it('should have valid icon paths', () => {
      manifest.icons.forEach(icon => {
        expect(icon.src).toBeDefined();
        expect(icon.src.startsWith('/')).toBe(true);
        expect(icon.src).toMatch(/\.(png|jpg|jpeg|webp)$/i);
      });
    });

    it('should have icon files that actually exist', () => {
      manifest.icons.forEach(icon => {
        const iconPath = path.join(process.cwd(), 'public', icon.src);
        expect(fs.existsSync(iconPath), `Icon file should exist: ${icon.src}`).toBe(true);

        // Check file is not empty
        const stats = fs.statSync(iconPath);
        expect(stats.size, `Icon file should not be empty: ${icon.src}`).toBeGreaterThan(0);
      });
    });
  });

  describe('Manifest File Access', () => {
    it('should exist in public directory', () => {
      const manifestPath = path.join(process.cwd(), 'public', 'manifest.json');
      expect(fs.existsSync(manifestPath)).toBe(true);
    });

    it('should have valid JSON structure', () => {
      const manifestPath = path.join(process.cwd(), 'public', 'manifest.json');
      const manifestContent = fs.readFileSync(manifestPath, 'utf-8');

      expect(() => JSON.parse(manifestContent)).not.toThrow();
    });

    it('should have correct file size for web delivery', () => {
      const manifestPath = path.join(process.cwd(), 'public', 'manifest.json');
      const stats = fs.statSync(manifestPath);

      // Manifest should be reasonable size (under 10KB)
      expect(stats.size).toBeGreaterThan(0);
      expect(stats.size).toBeLessThan(10 * 1024);
    });
  });
});
