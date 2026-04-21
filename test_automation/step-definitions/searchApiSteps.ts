// ===== API CONTRACT TEST STEPS =====
import { validateSearchSchema, validateArticleFields, getTotalCount, getArticles } from '../utils/schemas/Response/searchResponseSchema';
import { Given, Then } from '@cucumber/cucumber';
import { expect,APIRequestContext } from '@playwright/test';
import { ICustomWorld } from '../support/world'; 
import  dotenv from 'dotenv';
import { ApiUtils } from '../utils/apiUtils';

// Load environment variables
dotenv.config();

// ✅ Create an instance - this initializes BaseURL from env variables
const apiUtils = new ApiUtils();        

let apiResponse: any;
let apiResponseData: any;
let requestUrl: string;
let queryParams: Record<string, string> = {};

Given('I make a GET request to {string} with query parameters:', async function (
  this: ICustomWorld,
  endpoint: string,
  dataTable: any
) {
  // Convert data table to parameters
  queryParams = {};
  const rows = dataTable.rowsHash();
  Object.entries(rows).forEach(([key, value]) => {
    queryParams[key] = value as string;
  });

  // // Build URL with query parameters
  // const baseUrl = process.env.CAPCO_BASE_URL;
  // const params = new URLSearchParams(queryParams);
  // requestUrl = `${baseUrl}${endpoint}?${params.toString()}`;

  // console.log(`[API] GET ${requestUrl}`);

  try {
    apiResponse = await apiUtils.getSearchResultsForQuery(this.apiRequest!, endpoint, queryParams.searchQuery || '', parseInt(queryParams.itemsPerPage || '8'));
    apiResponseData = await apiResponse.json();
    console.log(`[API] Response received. TotalCount: ${apiResponseData.TotalCount}, Articles: ${apiResponseData.Articles?.length || 0}`);
  } catch (error) {
    console.error(`[API] Request failed:`, error);
    throw error;
  }
});

Then('the response status should be {int}', async function (expectedStatus: number) {
  if (!apiResponse) {
    throw new Error('No API response available. Did you make a GET request first?');
  }

  const actualStatus = apiResponse.status();
  console.log(`[API] Status Code: ${actualStatus}`);

  expect(actualStatus).toBe(expectedStatus);
});

Then('the response should match the search results schema', async function () {
  if (!apiResponseData) {
    throw new Error('No API response data available');
  }

  const validation = validateSearchSchema(apiResponseData);

  if (!validation.valid) {
    console.error('[API] Schema validation errors:');
    validation.errors.forEach((err) => console.error(`  - ${err}`));
    throw new Error(`Schema validation failed:\n${validation.errors.join('\n')}`);
  }

  console.log('[API] ✓ Response matches search articles schema');
});

Then('the response should contain {int} items in the results', async function (expectedCount: number) {
  if (!apiResponseData) {
    throw new Error('No API response data available');
  }

  const articles = getArticles(apiResponseData);
  const actualCount = articles.length;

  console.log(`[API] Expected ${expectedCount} items, got ${actualCount}`);
  expect(actualCount).toBe(expectedCount);
});

Then('each result should have required fields:', async function (dataTable: any) {
  if (!apiResponseData) {
    throw new Error('No API response data available');
  }

  const requiredFields = dataTable.raw().flat();
  const articles = getArticles(apiResponseData);

  const validation = validateArticleFields(articles, requiredFields);

  if (!validation.valid) {
    console.error(`[API] Field validation errors for required fields [${requiredFields.join(', ')}]:`);
    validation.errors.forEach((err) => console.error(`  - ${err}`));
    throw new Error(`Field validation failed:\n${validation.errors.join('\n')}`);
  }

  console.log(`[API] ✓ All ${articles.length} articles have required fields: [${requiredFields.join(', ')}]`);
});

Then('the response TotalCount should be {int}', async function (expectedCount: number) {
  if (!apiResponseData) {
    throw new Error('No API response data available');
  }

  const actualCount = getTotalCount(apiResponseData);
  console.log(`[API] TotalCount: ${actualCount}`);

  expect(actualCount).toBe(expectedCount);
});

Then('the response should contain an error message', async function () {
  if (!apiResponseData) {
    throw new Error('No API response data available');
  }

  const hasError = apiResponseData.error || apiResponseData.message || apiResponseData.Error;
  expect(hasError).toBeTruthy();
  console.log(`[API] ✓ Error response present`);
});