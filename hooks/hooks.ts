import { Before, After, BeforeAll, AfterAll,setDefaultTimeout  } from '@cucumber/cucumber';
import { chromium, Browser, BrowserContext, Page } from '@playwright/test';
import { ICustomWorld } from '../test_automation/support/world';

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
});

After(async function (this: ICustomWorld) {
  if (this.page) {
    await this.page.close();
  }
  if (this.context) {
    await this.context.close();
  }
});

AfterAll(async function () {
  if (browser) {
    await browser.close();
  }
});
