@api @search-api
Feature: Search API Contract Validation
  As a QA Engineer
  I want to validate the Search API contract
  So that UI tests have a reliable backend to depend on

  @searchapi-contract
  Scenario Outline: Search API returns valid response schema without optional query parameter
    Given I make a GET request to "/api/Search/ResultList" with query parameters:
      | itemsPerPage | <itemsPerPage> |
    Then the response status should be 200
    And the response should match the search results schema
    And the response should contain <itemsPerPage> items in the results
    And each result should have required fields:
      | Title     |
      | Description       |
      | Date   |
      | LinkUrl  |
      |ImageUrl  |
    Examples:
        | itemsPerPage |
        | 10           |

  @searchapi-with-query
  Scenario Outline: Search API returns valid response with search text query parameter
    Given I make a GET request to "/api/Search/ResultList" with query parameters:
      | itemsPerPage | <itemsPerPage> |
      | searchQuery    | News & Events |
    Then the response status should be 200
    And the response should match the search results schema
    And the response should contain 2 items in the results
    And each result should have required fields:
      | Title     |
      | Description       |
      | Date   |
      | LinkUrl  |
      |ImageUrl  |
  
    Examples:
        | itemsPerPage |
        | 10           |