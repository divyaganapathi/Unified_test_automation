/**
 * Response schema validation for Search API
 * Validates the actual Capco Search API response structure
 */

export const searchArticlesSchema = {
  type: 'object',
  required: ['Articles', 'TotalCount'],
  properties: {
    TotalCount: {
      type: 'number',
      minimum: 0,
      description: 'Total count of articles matching the search query'
    },
    Articles: {
      type: 'array',
      items: {
        type: 'object',
        required: ['Title', 'Description', 'Date', 'LinkUrl','ImageUrl'],
        properties: {
          Title: {
            type: 'string',
            minLength: 1,
            description: 'Article title'
          },
          Description: {
            type: 'string',
            description: 'Article description/summary'
          },
          Date: {
            type: 'string',
            description: 'Formatted date string (e.g., "16 Apr 2026")'
          },
          DateForOrder: {
            type: 'string',
            description: 'Internal date format for sorting'
          },
          Topics: {
            type: 'array',
            items: {
              type: 'string'
            },
            description: 'Array of topic tags'
          },
          ImageUrl: {
            type: 'string',
            description: 'URL to article image or null'
          },
          LinkUrl: {
            type: 'string',
            description: 'URL to the full article (relative or absolute)'
          },
          Author: {
            type: 'string',
            description: 'Author name (can be empty)'
          },
          AuthorImage: {
            type: 'string',
            description: 'Author image URL (can be empty)'
          },
          ReadTime: {
            type: 'string',
            description: 'Estimated read time (e.g., "5 minutes read" or empty)'
          }
        }
      }
    }
  }
};

/**
 * Validate response against search articles schema
 * @param response Response object to validate
 * @returns { valid: boolean; errors: string[] }
 */
export function validateSearchSchema(response: any): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Check top-level structure
  if (typeof response !== 'object' || response === null) {
    errors.push('Response must be an object');
    return { valid: false, errors };
  }

  // Check required top-level fields
  if (!('Articles' in response)) {
    errors.push('Missing required field: Articles');
  }
  if (!('TotalCount' in response)) {
    errors.push('Missing required field: TotalCount');
  }

  // Validate TotalCount is a number
  if (typeof response.TotalCount !== 'number') {
    errors.push(`TotalCount must be a number, got ${typeof response.TotalCount}`);
  }

  // Validate Articles is an array
  if (!Array.isArray(response.Articles)) {
    errors.push(`Articles must be an array, got ${typeof response.Articles}`);
    return { valid: errors.length === 0, errors };
  }

  // Validate each article
  response.Articles.forEach((article: any, index: number) => {
    const articlePath = `Articles[${index}]`;

    // Check required fields
    if (!article.Title || typeof article.Title !== 'string') {
      errors.push(`${articlePath}.Title: Required string field is missing or invalid`);
    }

    if (!article.Description || typeof article.Description !== 'string') {
      errors.push(`${articlePath}.Description: Required string field is missing or invalid`);
    }

    if (!article.Date || typeof article.Date !== 'string') {
      errors.push(`${articlePath}.Date: Required string field is missing or invalid`);
    }

    if (!article.LinkUrl || typeof article.LinkUrl !== 'string') {
      errors.push(`${articlePath}.LinkUrl: Required string field is missing or invalid`);
    }

    // Validate optional fields have correct types
    if (article.ImageUrl && typeof article.ImageUrl !== 'string') {
      errors.push(`${articlePath}.ImageUrl: Must be string`);
    }

    if (!Array.isArray(article.Topics)) {
      errors.push(`${articlePath}.Topics: Must be an array`);
    }

    if (typeof article.Author !== 'string') {
      errors.push(`${articlePath}.Author: Must be a string`);
    }

    if (typeof article.ReadTime !== 'string') {
      errors.push(`${articlePath}.ReadTime: Must be a string`);
    }
  });

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate that each article has specific required fields
 * @param articles Array of articles
 * @param requiredFields Array of field names to check
 * @returns { valid: boolean; errors: string[] }
 */
export function validateArticleFields(
  articles: any[],
  requiredFields: string[]
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  articles.forEach((article, index) => {
    requiredFields.forEach((field) => {
      if (!(field in article)) {
        errors.push(`Articles[${index}]: Missing field "${field}"`);
      } else if (!article[field] && field !== 'Author' && field !== 'AuthorImage' && field !== 'ReadTime') {
        // Allow empty values for Author, AuthorImage, ReadTime
        errors.push(`Articles[${index}].${field}: Field is empty`);
      }
    });
  });

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Get total count from response
 */
export function getTotalCount(response: any): number {
  return response?.TotalCount || 0;
}

/**
 * Get articles from response
 */
export function getArticles(response: any): any[] {
  return response?.Articles || [];
}