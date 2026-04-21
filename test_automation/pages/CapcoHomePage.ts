import { Page, Locator, expect } from '@playwright/test';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

export class CapcoHomePage {
  private page: Page;
  private readonly baseURL = process.env.CAPCO_BASE_URL;
  
  // Search locators
  private readonly acceptCookiesButton: Locator;
  private readonly searchButton: Locator;
  private readonly searchInput: Locator;
  private readonly submitSearchButton: Locator;
  private readonly closeSearchButton: Locator;
  private readonly resultsCount: Locator;
 readonly noResultsHeading: Locator; 
  async  getSearchResultsHeading(text: string): Promise<Locator> {
    return this.page.locator('h2', { hasText: text });
  }


  constructor(page: Page) {
    this.page = page;
    this.acceptCookiesButton = page.getByRole('button', { name: /accept.*cookies/i });
    // Use aria-controls to uniquely identify the "Open search" button
    this.searchButton = page.locator('button[aria-controls="js-search-panel"]');
    this.searchInput = page.getByRole('textbox', { name: /search/i });
    this.submitSearchButton = page.getByRole('button', { name: /^submit search$/i });
    // Use specific pattern for "Close search panel" button
    this.closeSearchButton = page.getByRole('button', { name: /close search panel/i });
    this.resultsCount = page.locator('.search-results-count');
    this.noResultsHeading = page.getByRole('heading', { name: 'No results.' }).first();
  }

  async navigateToHomepage(): Promise<void> {
    await this.page.goto(this.baseURL!);
  }

  async acceptAllCookies(): Promise<void> {
    await expect(this.acceptCookiesButton).toBeVisible();
    await this.page.waitForLoadState('networkidle'); // Wait for any animations
    await this.acceptCookiesButton.click();
  }

  async clickSearchButton(): Promise<void> {
    await expect(this.searchButton).toBeVisible();
    await this.searchButton.click();
    // Wait for search panel to open with animation
    await this.page.waitForLoadState('networkidle');
  }

  async isSearchPanelOpen(): Promise<boolean> {
    try {
      // Check if search panel is visible using the id from aria-controls attribute
      const searchPanel = this.page.locator('#js-search-panel');
      await expect(searchPanel).toBeVisible({ timeout: 3000 });
      
      // Verify interactive elements are present in the panel
      await expect(this.searchInput).toBeVisible({ timeout: 2000 });
      await expect(this.submitSearchButton).toBeVisible({ timeout: 2000 });
      return true;
    } catch (error) {
      console.log('Search panel failed to open:', error);
      return false;
    }
  }

  async enterSearchText(searchText: string): Promise<void> {
    await this.searchInput.click();
    await this.searchInput.fill(searchText);
  }

  async clickSubmitSearchButton(): Promise<void> {
    await this.submitSearchButton.click();
  }



  async getDisplayedResultsCount(): Promise<string> {
    const resultText = await this.resultsCount.textContent();
    const match = resultText?.match(/(\d+)\s+results/);
    return match ? match[1] : '0';
  }

  async verifyResultsTextVisible(expectedText: string, searchQuery: string): Promise<void> {
    const searchResultsHeading = await this.getSearchResultsHeading(searchQuery);
    await expect(searchResultsHeading).toContainText(`${expectedText}`);
  }

  // Career Search Methods
  async clickCareersDropdown(): Promise<void> {
    // Click on the main navigation Careers item - use filter for proper locator syntax
    const careersDropdown = this.page.locator('a.m-menu__link.is-desktop').filter({ hasText: 'Careers' });
    await expect(careersDropdown).toBeVisible({ timeout: 5000 });
    await careersDropdown.click();
    // await this.page.waitForTimeout(500); // Wait for dropdown animation
  }

  async selectCareersFromDropdown(): Promise<void> {
    // Click on the Careers Search link - use role-based locator (more robust)
    const careersPageLink = this.page.getByRole('link', { name: /career search|careers/i }).first();
    await expect(careersPageLink).toBeVisible({ timeout: 5000 });
    await careersPageLink.click();
    await this.page.waitForLoadState('networkidle');
  }

  async searchForRoleWithLocation(role: string, location: string): Promise<void> {
    // Fill role search input
    const roleInput = this.page.locator('input[placeholder*="Enter keyword or job ID"]');
    await expect(roleInput).toBeVisible({ timeout: 5000 });
    await roleInput.fill(role);
    const locationDropDown = this.page.locator("div.careers-search__dropdown-list p").filter({ hasText: 'All Locations'   });
    await expect(locationDropDown).toBeVisible({ timeout: 5000 });
    await locationDropDown.click();
    await this.page.locator('ul').getByText(`${location}`, { exact: true }).click();
    await this.page.waitForLoadState('networkidle');
    await this.page.locator('.search-icon').click();
  }

  async getCareerSearchResultsCount(): Promise<string> {
    const resultElement = await this.page.locator(
      'div.careers-search__jobs-list h2 span'
    );
    await this.page.waitForTimeout(5000)
    const resultText = (await resultElement.textContent())?.trim() || '';
    console.log('Career search results text:', resultText);
    return resultText;
  }

  async verifyCareerSearchResults(expectedCount: number): Promise<void> {
    const actualCount = await this.getCareerSearchResultsCount();
    if (parseInt(actualCount) === 0) {
      throw new Error(`No results found. Expected ${expectedCount} results but got 0. Results element may not exist on page.`);
    }
    this.page.pause();
    expect(parseInt(actualCount)).toBe(expectedCount);
  }

}
