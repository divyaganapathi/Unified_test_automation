# BDD Test Automation Framework

This project implements a comprehensive BDD (Behavior-Driven Development) testing framework using **Cucumber** and **Playwright** for automated UI and API testing.

---

## 📁 Project Structure

```
Playwright/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD pipeline
├── cucumber.cjs                      # Cucumber configuration
├── playwright.config.ts              # Playwright configuration
├── package.json                      # Project dependencies & npm scripts
├── tsconfig.json                     # TypeScript configuration
│
└── test_automation/
    ├── features/                     # Cucumber feature files (Gherkin)
    │   ├── CapSearch.feature        # Search functionality scenarios
    │   └── CapSearchAPI.feature     # Search API contract validation
    │
    ├── step-definitions/             # Step implementations (glue code)
    │   ├── searchSteps.ts           # Search feature steps
    │   └── searchApiSteps.ts        # Search API steps
    │
    ├── pages/                        # Page Object Models (POM)
    │   └── CapcoHomePage.ts         # Capco homepage interactions
    │
    ├── hooks/                        # Cucumber hooks (setup/teardown)
    │   └── hooks.ts                 # Before/After hooks, browser setup
    │
    ├── support/                      # Test context & configuration
    │   └── world.ts                 # Cucumber world object
    │
    ├── utils/                        # Utility functions & helpers
    │   ├── apiUtils.ts              # API request utilities
    │   ├── commonUtils.ts           # Common helper functions
    │   ├── logger.ts                # Logging utilities
    │   └── schemas/
    │       └── Response/
    │           └── searchResponseSchema.ts
    │
    ├── __screenshots__/              # Test failure screenshots
    │   └── failures/                # Screenshots on test failure
    │
    ├── cucumber-report.html         # HTML test report
    ├── cucumber-report.json         # JSON test report
    ├── cucumber-report.xml          # JUnit XML report
    └── .gitignore                   # Ignore rules for test_automation
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** v18.x or higher
- **npm** (comes with Node.js)
- **Git**

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Playwright
```

2. Install dependencies:
```bash
npm install
```

3. Install Playwright browsers:
```bash
npx playwright install --with-deps
```

4. Setup environment variables (if needed):
```bash
cp .env.example .env
# Edit .env with your configuration
```

---

## 🧪 Running Tests

### **Run All Tests**
```bash
npm run test:bdd
```
Executes all Cucumber scenarios (smoke + full tests)

### **Run Only Smoke Tests**
```bash
npm run test:bdd -- --tags @smoke
```
Quick health check tests (2-3 min)

### **Run Specific Feature Tests**
```bash
npm run test:bdd -- --tags @search
npm run test:bdd -- --tags @careers
npm run test:bdd -- --tags @api
```

### **Run Tests Excluding Smoke**
```bash
npm run test:bdd -- --tags "not @smoke"
```
Runs full test suite without re-running smoke tests

### **Run Tests with Specific Tags (Combinations)**
```bash
# Tests with both tags
npm run test:bdd -- --tags "@search and @regression"

# Tests with either tag
npm run test:bdd -- --tags "@search or @api"

# Complex combinations
npm run test:bdd -- --tags "(@search or @api) and not @skip"
```

### **Other Run Commands**

**Run in Headed Mode** (visible browser):
```bash
npm run test:bdd:headed
```

**Generate & Open Report**:
```bash
npm run test:bdd:report
```

**Dry Run** (validate scenarios without execution):
```bash
npm run test:bdd:dry-run
```

**Debug Mode**:
```bash
npm run test:bdd:debug
```

---

## 🏷️ Test Tags

Use tags to organize and run specific tests:

| Tag | Purpose | Duration |
|-----|---------|----------|
| `@smoke` | Critical path tests (fast health check) | 5-10 min |
| `@search` | Search functionality tests | 5-7 min |
| `@api` | API contract validation tests | 3-5 min |
| `@careers` | Career search functionality | 5 min |
| `@regression` | Full regression test suite | 15+ min |
| `@skip` | Skip these scenarios | - |

### Adding Tags to Features

```gherkin
@smoke @search
Scenario: Search for News & Events
  Given I navigate to Capco homepage
  When I click the search button
  Then I should see search results
```

---

## 🔧 Configuration Files

### **cucumber.cjs**
- Defines feature file paths
- Reporter formats (HTML, JSON, JUnit XML)
- Parallel execution settings
- Timeout configuration (60 seconds per step)
- Require paths for steps and hooks

### **playwright.config.ts**
- Browser configurations
- Trace collection settings
- Reporter configurations
- Retry settings

### **hooks.ts**
- Browser and context initialization
- Page default timeouts:
  - Operation timeout: 15 seconds (click, fill, etc.)
  - Navigation timeout: 30 seconds (page.goto)
- Screenshot capture on failures

---

## 📊 Reports

Test reports are generated automatically after execution:

### **HTML Report**
```
test_automation/cucumber-report.html
```
Open in browser to view detailed scenario results, step definitions, and screenshots.

### **JSON Report**
```
test_automation/cucumber-report.json
```
Programmatic access to test data for CI integration.

### **JUnit XML Report**
```
test_automation/cucumber-report.xml
```
Integration with CI/CD tools and dashboards.

### **Screenshots**
Failed test screenshots are saved to:
```
test_automation/__screenshots__/failures/
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/ci.yml`)

**Trigggers:**
- Push to `main` or `develop` branches
- Pull requests against `main` or `develop`

**Pipeline Stages:**

1. **Smoke Tests** (fail-fast)
   ```bash
   npm run test:bdd -- --tags @smoke
   ```
   - Runs first (5-10 min)
   - Blocks full tests if smoke fails

2. **Full Tests** (only if smoke passes)
   ```bash
   npm run test:bdd -- --tags "not @smoke"
   ```
   - Runs complete test suite (15-20 min)

3. **Report Generation & Artifacts**
   - HTML/JSON/XML reports uploaded
   - Screenshots from failures included
   - Artifacts retained for 30 days

4. **PR Comments**
   - Automated test summary posted on PRs
   - Shows pass/fail counts
   - Link to detailed reports

---

## 📝 Writing Tests

### Feature File Example (`CapSearch.feature`)
```gherkin
@smoke @search
Feature: Capco Search Functionality
  As a user
  I want to search for content
  So that I can find relevant information

  Scenario Outline: Search for content and validate results
    Given I navigate to Capco homepage
    And I accept all cookies
    When I click the search button
    And I enter search text "<search_term>"
    And I click submit search button
    Then I should see "<expected_results>"

    Examples:
      | search_term | expected_results |
      | News & Events | 2 results |
```

### Step Definition Example (`searchSteps.ts`)
```typescript
import { Given, When, Then } from '@cucumber/cucumber';
import { CapcoHomePage } from '../pages/CapcoHomePage';

Given('I navigate to Capco homepage', async function (this: ICustomWorld) {
  const homePage = new CapcoHomePage(this.page);
  await homePage.navigateToHomepage();
});

When('I enter search text {string}', async function (this: ICustomWorld, searchText: string) {
  const homePage = new CapcoHomePage(this.page);
  await homePage.enterSearchText(searchText);
});
```

### Page Object Example (`CapcoHomePage.ts`)
```typescript
export class CapcoHomePage {
  private page: Page;
  private acceptCookiesButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.acceptCookiesButton = page.getByRole('button', { name: 'Accept All Cookies' });
  }

  async acceptAllCookies(): Promise<void> {
    const isVisible = await this.acceptCookiesButton.isVisible({ timeout: 5000 });
    if (isVisible) {
      await this.acceptCookiesButton.click();
    }
  }
}
```

---

## ⏱️ Timeouts Configuration

### Timeout Hierarchy (Highest to Lowest Priority)

1. **Per-operation timeout** (highest priority)
   ```typescript
   await button.click({ timeout: 30000 });
   ```

2. **Page default timeout** (15 seconds)
   ```typescript
   page.setDefaultTimeout(15000);  // In hooks.ts
   ```

3. **Navigation timeout** (30 seconds)
   ```typescript
   page.setDefaultNavigationTimeout(30000);
   ```

4. **Cucumber step timeout** (60 seconds - lowest priority)
   ```typescript
   setDefaultTimeout(60 * 1000);  // In hooks.ts
   ```

---

## 🔍 Best Practices

✅ **Do:**
- Use Page Object Model pattern for maintainability
- Add meaningful tags to organize tests
- Run smoke tests before committing
- Write clear, descriptive scenario names
- Use test data in Examples tables
- Capture screenshots on failures
- Keep timeouts reasonable (15-30 seconds)

❌ **Don't:**
- Hardcode URLs, credentials, or test data
- Skip tagging scenarios
- Ignore CI pipeline failures
- Create flaky tests with long arbitrary waits
- Mix UI and API tests in same scenario
- Commit with failing tests

---

## 🐛 Troubleshooting

### Tests Pass Locally but Fail in CI

**Common Causes:**
- Cookie banner not present in CI (already accepted)
- Different system fonts/rendering
- Network conditions or API timeouts

**Solutions:**
- Make cookie handling optional (✅ Already implemented)
- Use explicit waits instead of sleeps
- Increase timeouts for CI (`timeout-minutes: 30` in workflow)

### Browser Won't Close

**Solution:** Check hooks.ts After() block properly closes context and page

### API Validation Fails

**Debug:**
```typescript
console.log('API Response:', apiResponse);
console.log('Expected Schema:', schema);
```

---

## 📚 Documentation

- [Playwright Docs](https://playwright.dev)
- [Cucumber.js Docs](https://github.com/cucumber/cucumber-js)
- [Gherkin Syntax](https://cucumber.io/docs/gherkin/)

---

## 👤 Author & Support

For issues, questions, or suggestions, please create an issue in the repository.

---

## 📄 License

ISC
- Navigates to Capco homepage
- Accepts cookies
- Searches for "News & Events"
- Validates search results heading
- Verifies results count
- Compares with API response

## Reports

After running tests, reports are generated in:
- `test_automation/cucumber-report.html` - HTML report
- `test_automation/cucumber-report.json` - JSON format
- `test_automation/cucumber-report.xml` - JUnit XML format

## Environment Variables

- `HEADLESS` - Run browser in headless mode (default: true)
- `APP_URL` - Application URL (default: https://www.capco.com)

## Debugging

To debug tests:
1. Run `npm run test:bdd:debug`
2. Add `await this.page.pause()` in step definitions to pause execution
3. Use Playwright Inspector to interact with the page

## Adding New Scenarios

1. Add feature file in `test_automation/features/`
2. Create page object in `test_automation/pages/` if needed
3. Implement steps in `test_automation/step-definitions/`
4. Run tests with `npm run test:bdd`

## Best Practices

- Keep scenarios focused and independent
- Use page objects to avoid UI locator duplication
- Write descriptive scenario names
- Use API utils for backend validation
- Keep step definitions concise
