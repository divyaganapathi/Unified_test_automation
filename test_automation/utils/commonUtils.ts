import { Page } from '@playwright/test';
import { expect,Locator,APIRequestContext } from '@playwright/test';
import { Eyes, Target } from '@applitools/eyes-playwright';
import path from 'path';
import fs from 'fs';
const { PNG } = require('pngjs');
import pixelmatch from 'pixelmatch';

// Initialize Applitools Eyes
const eyes = new Eyes();

export async function softVisualCheck(page: Page | undefined, name: string) {
  if (!page) {
    console.error('⚠️ Page is undefined for visual check');
    return;
  }

  try {
    // Set API key from environment
    const apiKey = process.env.APPLITOOLS_API_KEY;
    if (!apiKey) {
      console.warn('⚠️ APPLITOOLS_API_KEY not set in .env file');
      return;
    }

    eyes.setApiKey(apiKey);

    // Start visual test
    await eyes.open(page, 'Capco Search Tests', name);

    // Capture visual snapshot
    await eyes.check(name, Target.window());

    // Close eyes
    await eyes.closeAsync();
    
    console.log(`✓ Visual snapshot captured: ${name}`);
  } catch (e) {
    console.error(`✗ Visual check failed for ${name}:`, e);
  }
}
export async function interceptSearchApiToReturnError(page:Page, endpoint: string, errorCode: number, searchQuery: string): Promise<void> {
  const url = `${process.env.BASE_URL}${endpoint}?searchQuery=${encodeURIComponent(searchQuery)}`;
  await page.route(url, (route) => {
    route.fulfill({
      status: errorCode,
      body: JSON.stringify({ error: `Simulated ${errorCode} error for ${searchQuery}` }),
    });
  });
}
/**
 * Playwright visual regression test with baseline, current, and diff screenshots
 * First run creates baseline, subsequent runs compare and generate diffs
 * Saves to: test_automation/__screenshots__/{name}-baseline.png, {name}-current.png, {name}-diff.png
 * Does not fail test on mismatch (soft assertion for Cucumber)
 * 
 * @param page Playwright Page object
 * @param name Snapshot name (e.g., "homepage", "search-results")
 * @param maxDiffPixels Maximum different pixels allowed (default: 100)
 * @param locator Optional Playwright Locator to capture specific element instead of full page
 */



type SoftVisualCheckOptions = {
  maxDiffPixels?: number;
  locator?: Locator;
  snapshotDir?: string;
  threshold?: number;
};

export async function playwrightSoftVisualCheck(
  page: Page | undefined,
  name: string,
  options: SoftVisualCheckOptions = {}
): Promise<void> {
  const {
    maxDiffPixels = 100,
    locator,
    snapshotDir = './test_automation/__screenshots__',
    threshold = 0.2,
  } = options;

  if (!page) {
    console.error('⚠️ Page is undefined for visual check');
    return;
  }

  try {
    if (!fs.existsSync(snapshotDir)) {
      fs.mkdirSync(snapshotDir, { recursive: true });
    }

    const baselinePath = path.join(snapshotDir, `${name}-baseline.png`);
    const currentPath = path.join(snapshotDir, `${name}-current.png`);
    const diffPath = path.join(snapshotDir, `${name}-diff.png`);

    await page.setViewportSize({ width: 1280, height: 720 });
    await page.waitForLoadState('domcontentloaded');
    await page.waitForLoadState('networkidle');

    // Wait for fonts to finish loading
    await page.evaluate(async () => {
      const anyDocument = document as Document & {
        fonts?: { ready: Promise<unknown> };
      };

      if (anyDocument.fonts?.ready) {
        await anyDocument.fonts.ready;
      }
    });

    // Disable motion and hide unstable elements
    await page.addStyleTag({
      content: `
        *,
        *::before,
        *::after {
          animation: none !important;
          transition: none !important;
          caret-color: transparent !important;
          scroll-behavior: auto !important;
        }

        iframe,
        video,
        .cookie-banner,
        .chat-widget,
        .popup,
        .modal,
        .carousel,
        [aria-live="polite"],
        [aria-live="assertive"] {
          visibility: hidden !important;
        }
      `,
    });

    // await page.waitForTimeout(1000);

    // Capture screenshot
    if (locator) {
      await locator.waitFor({ state: 'visible' });
      await locator.screenshot({ path: currentPath });
    } else {
      await page.screenshot({
        path: currentPath,
        fullPage: false,
      });
    }

    console.log(`✓ Current screenshot: ${currentPath}`);

    // First run: create baseline
    if (!fs.existsSync(baselinePath)) {
      fs.copyFileSync(currentPath, baselinePath);
      console.log(`✓ Baseline created: ${baselinePath}`);
      return;
    }

    const baselineImg = PNG.sync.read(fs.readFileSync(baselinePath));
    const currentImg = PNG.sync.read(fs.readFileSync(currentPath));

    // Compare only if dimensions match
    if (
      baselineImg.width !== currentImg.width ||
      baselineImg.height !== currentImg.height
    ) {
      console.warn(`⚠️ Screenshot dimensions changed for ${name}:`);
      console.warn(
        `   Baseline: ${baselineImg.width}x${baselineImg.height} → Current: ${currentImg.width}x${currentImg.height}`
      );
      console.warn('   Skipping pixel comparison. Review current screenshot manually.');
      return;
    }

    const { width, height } = baselineImg;
    const diff = new PNG({ width, height });

    const pixelsChanged = pixelmatch(
      baselineImg.data,
      currentImg.data,
      diff.data,
      width,
      height,
      { threshold }
    );

    if (pixelsChanged > maxDiffPixels) {
      fs.writeFileSync(diffPath, PNG.sync.write(diff));
      const diffPercentage = ((pixelsChanged / (width * height)) * 100).toFixed(2);

      console.warn(`⚠️ Visual difference detected in ${name}:`);
      console.warn(`   Pixels changed: ${pixelsChanged} (${diffPercentage}%)`);
      console.warn(`   Diff saved: ${diffPath}`);
    } else {
      if (fs.existsSync(diffPath)) {
        fs.unlinkSync(diffPath);
      }
      console.log(`✓ Visual match: ${name}`);
    }
  } catch (error) {
    console.error(`✗ Visual check failed for ${name}:`, error);
  }
}
