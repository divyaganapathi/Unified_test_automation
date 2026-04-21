# BDD Test Automation Framework

This project implements a BDD (Behavior-Driven Development) testing framework using Cucumber and Playwright.

## Project Structure

```
test_automation/
├── features/              # Cucumber feature files (Gherkin syntax)
│   └── search.feature    # Search functionality scenarios
├── step-definitions/      # Step definitions (glue code)
│   └── searchSteps.ts    # Step implementations for search feature
├── pages/                # Page Object Models (POM)
│   └── CapcoHomePage.ts  # Capco homepage interactions
├── utils/                # Utility classes and helpers
│   └── apiUtils.ts       # API request utilities
├── hooks/                # Cucumber hooks (before/after)
│   └── hooks.ts          # Setup and teardown logic
└── support/              # Support files
    └── world.ts          # Cucumber world (test context)
```

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

## Running Tests

### Run all BDD tests
```bash
npm run test:bdd
```

### Run with HTML report
```bash
npm run test:bdd:report
```

### Dry run (validate scenarios without running)
```bash
npm run test:bdd:dry-run
```

### Debug mode
```bash
npm run test:bdd:debug
```

## Key Components

### Feature Files (`CAPCO/features/`)
- Written in Gherkin language
- Describe user scenarios in plain English
- Can be read by business stakeholders and QA teams

### Step Definitions (`CAPCO/step-definitions/`)
- Implement the steps from feature files
- Connect test scenarios to actual code
- Use Playwright for browser interactions

### Page Objects (`CAPCO/pages/`)
- Encapsulate page interactions and locators
- Provide reusable methods for common actions
- Decouple test logic from UI implementation

### Utils (`CAPCO/utils/`)
- API utilities for backend testing
- Common helper functions
- Shared functionality across tests

### Hooks (`CAPCO/hooks/`)
- Setup and teardown logic
- Initialize browser and context
- Cleanup after test execution

### Configuration (`cucumber.js`)
- Defines test execution settings
- Reporter configurations
- Timeout and retry settings

## Test Flow

1. **Feature Definition**: Write scenarios in `search.feature`
2. **Step Implementation**: Implement steps in `searchSteps.ts`
3. **Page Interactions**: Use page objects from `CapcoHomePage.ts`
4. **API Validation**: Utilize `apiUtils.ts` for API verification
5. **Report Generation**: HTML report generated after test execution

## Current Scenarios

### Search for News & Events
- Navigates to Capco homepage
- Accepts cookies
- Searches for "News & Events"
- Validates search results heading
- Verifies results count
- Compares with API response

## Reports

After running tests, reports are generated in:
- `CAPCO/cucumber-report.html` - HTML report
- `CAPCO/cucumber-report.json` - JSON format
- `CAPCO/cucumber-report.xml` - JUnit XML format

## Environment Variables

- `HEADLESS` - Run browser in headless mode (default: true)
- `APP_URL` - Application URL (default: https://www.capco.com)

## Debugging

To debug tests:
1. Run `npm run test:bdd:debug`
2. Add `await this.page.pause()` in step definitions to pause execution
3. Use Playwright Inspector to interact with the page

## Adding New Scenarios

1. Add feature file in `CAPCO/features/`
2. Create page object in `CAPCO/pages/` if needed
3. Implement steps in `CAPCO/step-definitions/`
4. Run tests with `npm run test:bdd`

## Best Practices

- Keep scenarios focused and independent
- Use page objects to avoid UI locator duplication
- Write descriptive scenario names
- Use API utils for backend validation
- Keep step definitions concise
