import { Before, After, BeforeAll, AfterAll, setDefaultTimeout, Status } from '@cucumber/cucumber';
import { chromium, Browser, BrowserContext, Page } from '@playwright/test';
import { ICustomWorld } from '../support/world';
import { logger } from '../utils/logger';
import path from 'path';
import fs from 'fs';

let browser: Browser;
setDefaultTimeout(60 * 1000);

BeforeAll(async function () {
  browser = await chromium.launch({
    headless: process.env.HEADLESS !== 'false',
  });
});

Before(async function (this: ICustomWorld) {
  const context: BrowserContext = await browser.newContext();
  this.context = context;
  this.page = await context.newPage();
  this.apiRequest = context.request;
  logger.info('Browser context initialized', 'HOOK:Before');
});

After(async function (this: ICustomWorld, scenario: any) {
  // Capture screenshot on failure
  if (scenario.result.status === Status.FAILED && this.page && !this.page.isClosed()) {
    const screenshotDir = './test_automation/__screenshots__/failures';
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const screenshotPath = path.join(screenshotDir, `${scenario.pickle.name}-${timestamp}.png`);
    
    try {
      await this.page.screenshot({ path: screenshotPath, fullPage: true });
      logger.info(`Screenshot captured on failure`, 'HOOK:After', { path: screenshotPath });
      
      // Attach to Cucumber report
      this.attach(fs.readFileSync(screenshotPath), 'image/png');
    } catch (e) {
      logger.error(`Failed to capture screenshot`, 'HOOK:After', e);
    }
  }

  // Safely close page and context
  try {
    if (this.page && !this.page.isClosed()) {
      await this.page.close();
      logger.info('Page closed', 'HOOK:After');
    }
  } catch (e) {
    logger.warn('Page close error', 'HOOK:After', e);
  }

  try {
    if (this.context) {
      await this.context.close();
      logger.info('Context closed', 'HOOK:After');
    }
  } catch (e) {
    logger.warn('Context close error', 'HOOK:After', e);
  }
});

AfterAll(async function () {
  if (browser) {
    await browser.close();
  }
});

