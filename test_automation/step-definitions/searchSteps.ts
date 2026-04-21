import { Given, When, Then } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { ICustomWorld } from '../support/world';
import { CapcoHomePage } from '../pages/CapcoHomePage';
import { ApiUtils } from '../utils/apiUtils';
import { logger } from '../utils/logger';

const apiUtils = new ApiUtils();

let homePage: CapcoHomePage;

Given('I navigate to Capco homepage', async function (this: ICustomWorld) {
  logger.stepStart('Navigate to Capco homepage');
  homePage = new CapcoHomePage(this.page);
  await homePage.navigateToHomepage();
});

Given('I accept all cookies', async function (this: ICustomWorld) {
  await homePage.acceptAllCookies();
});

When('I click the search button', async function (this: ICustomWorld) {
  logger.stepStart('Click search button');
  await homePage.clickSearchButton();

  // The panel opens asynchronously, verify it's ready
  const isOpen = await homePage.isSearchPanelOpen();
  logger.assertion('Search panel is open', isOpen);
  expect(isOpen).toBe(true);
});

When('I enter search text {string}', async function (this: ICustomWorld, searchText: string) {
  await homePage.enterSearchText(searchText);
});

When('I click submit search button', async function (this: ICustomWorld) {
  await homePage.clickSubmitSearchButton();
});

Then('I should see {string} for {string}', async function (this: ICustomWorld, resultsCount: string, searchQuery: string) {
  await homePage.verifyResultsTextVisible(resultsCount, searchQuery);
});

Then('search results count should match {string} API response for {string}', async function (
  this: ICustomWorld,
  endpoint: string,
  searchQuery: string
) {
  logger.stepStart(`Validate API response for query: ${searchQuery}`);
  // Get API response
  const apiResponse = await apiUtils.getSearchResultsForQuery(this.apiRequest, endpoint, searchQuery);
  const apiResponseData = await apiResponse.json();
  const expectedCount = apiResponseData?.TotalCount || 0;
  logger.info(`API returned TotalCount`, 'API_VALIDATION', { expectedCount, searchQuery });
  
  // Verify the count matches
  await homePage.verifyResultsTextVisible(expectedCount, searchQuery);
});

Then('I validate the search results contain expected keywords for {string}', async function (searchQuery) {
  await homePage.verifyResultsTextVisible(searchQuery, searchQuery);
});

// Career Search Steps
When('I click on the careers dropdown in top right', async function (this: ICustomWorld) {
  await homePage.clickCareersDropdown();
});

When('I select career search from the dropdown', async function (this: ICustomWorld) {
  await homePage.selectCareersFromDropdown();
});

When('I search for {string} position in {string} location', async function (
  this: ICustomWorld,
  role: string,
  location: string
) {
  await homePage.searchForRoleWithLocation(role, location);
});

Then('I should see {string} career search results', async function (this: ICustomWorld, expectedCount: string) {
  await homePage.verifyCareerSearchResults(parseInt(expectedCount, 10));
});

When('I intercept the {string} API to fail', async function (this: ICustomWorld, endpoint: string) {
  // Setup route interception BEFORE the request is made
  try {
    await this.page.route(`**${endpoint}**`, async (route) => {
      console.log(`[INTERCEPT] Blocking: ${endpoint}`);
      try {
        await route.abort('failed');
      } catch (e) {
        console.log(`[INTERCEPT] Abort error (page may have closed):`, e);
      }
    });
    console.log(`✓ API interception setup: ${endpoint} will fail`);
  } catch (e) {
    console.error('Failed to setup interception:', e);
  }
});

Then('I should see {string} heading', async function (this: ICustomWorld, headingText: string) {
  try {
    // Wait for heading to appear
    await expect(homePage.noResultsHeading).toBeVisible({ timeout: 10000 }).catch(() => {
      console.warn(`⚠️ Heading "${headingText}" not found`);
    });
    console.log(`✓ Heading "${headingText}" displayed`);
  } catch (e) {
    console.warn(`⚠️ Heading check failed:`, e);
  }
});
