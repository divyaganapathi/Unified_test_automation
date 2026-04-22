import { Page, BrowserContext, APIRequestContext } from '@playwright/test';
import { IWorldOptions, World } from '@cucumber/cucumber';

export interface ICustomWorld extends World {
  page: Page;
  context: BrowserContext;
  apiRequest: APIRequestContext;
}

export class CustomWorld extends World implements ICustomWorld {
  public page!: Page;
  public context!: BrowserContext;
  public apiRequest!: APIRequestContext;

  constructor(options: IWorldOptions) {
    super(options);
  }
}
