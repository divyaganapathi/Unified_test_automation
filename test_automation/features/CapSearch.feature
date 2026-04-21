Feature: Capco Search Functionality
  As a user
  I want to search for content on Capco website
  So that I can find relevant information
  @search
  Scenario Outline: Search for News & Events and validate results
    Given I navigate to Capco homepage
    And I accept all cookies
    When I click the search button
    Then I enter search text "<Search_text>"
    And I click submit search button
    And I should see "<no_of_results>" for "<Search_text>"
    And search results count should match "/api/Search/ResultList" API response for "<Search_text>"
    And I validate the search results contain expected keywords for "<Search_text>"

  Examples:
  |Search_text|no_of_results|
  |News & Events|2 results|

  @search-api-failue
  Scenario Outline: Search for News & Events and validate API failure handling
    Given I navigate to Capco homepage
    And I accept all cookies
    When I click the search button
    And I enter search text "<Search_text>"
    And I intercept the "/api/Search/ResultList" API to fail
    And I click submit search button
    And I should see "No results" heading

  Examples:
  |Search_text|
  |News & Events|


  @careers
  Scenario Outline: Search for SDET role in careers with location filter and validate against API
    Given I navigate to Capco homepage
    And I accept all cookies
    When I click on the careers dropdown in top right
    And I select career search from the dropdown
    And I search for "<Role>" position in "<Location>" location
    Then I should see "<ExpectedCount>" career search results

  Examples:
  |Role|Location|ExpectedCount|
  |sdet|UK - London|2|
