import { APIRequestContext, APIResponse } from '@playwright/test';
import dotenv from 'dotenv';
import { logger } from './logger';    

// Load environment variables
dotenv.config();

export class ApiUtils {
  private BaseURL = process.env.CAPCO_BASE_URL;

  /**
   * Get search results from Capco API
   * @param apiContext - Playwright APIRequestContext
   * @param endpoint - API endpoint to call (e.g., "/api/Search/ResultList")
   * @param searchQuery - Search query string
   * @param itemsPerPage - Number of items per page (default: 8)
   * @returns Search results with apiResponse object containing TotalCount and Articles array
   */
  async getSearchResultsForQuery(
    apiContext: APIRequestContext,
    endpoint: string,
    searchQuery: string,
    itemsPerPage: number = 8
  ): Promise<APIResponse> {
    try {
      const url = `${this.BaseURL}${endpoint}?searchQuery=${encodeURIComponent(searchQuery)}&itemsPerPage=${itemsPerPage}`;
      const response = await apiContext.get(url);

      if (!response.ok()) {
        throw new Error(`API failed with status ${response.status()}`);
      }
      return response;
    } catch (error) {
      logger.error(`Failed to get search results for query: ${searchQuery}`, 'API', error);
      throw error;
    }
  }
}

