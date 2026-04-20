# Unified Test Automation Framework

An **AI-assisted, unified automation framework** for both **API** and **UI** testing, built with Python and pytest.

---

## Features

| Capability | Technology |
|---|---|
| **API testing** | `requests` + fluent assertions |
| **UI testing** | Playwright page-object model |
| **AI test generation** | OpenAI GPT (optional) |
| **AI test analysis** | OpenAI GPT (optional, fallback to rule-based) |
| **Reporting** | pytest-html, pytest-json-report |
| **Data generation** | Faker |
| **Configuration** | YAML + `.env` overrides |
| **Retry / resilience** | urllib3 Retry adapter |
| **Parallel execution** | pytest-xdist |

---

## Project Structure

```
Unified_test_automation/
├── config/
│   └── config.yaml              # Main configuration
├── framework/
│   ├── api/
│   │   ├── client.py            # Session-based HTTP client
│   │   ├── assertions.py        # Fluent assertion builder
│   │   └── models.py            # APIResponse / RequestSpec
│   ├── ui/
│   │   ├── driver.py            # Playwright BrowserManager
│   │   └── page.py              # BasePage object model
│   ├── ai/
│   │   ├── generator.py         # AI test-code generator
│   │   └── analyzer.py          # AI test-result analyzer
│   └── utils/
│       ├── config.py            # Config singleton
│       ├── logger.py            # Structured logging
│       └── data_provider.py     # Faker-backed test data
├── tests/
│   ├── conftest.py              # Shared pytest fixtures
│   ├── api/
│   │   └── test_jsonplaceholder.py   # Sample API tests
│   ├── ui/
│   │   └── test_example_site.py      # Sample UI tests
│   └── test_framework_units.py       # Unit tests (no network)
├── reports/                     # Generated at runtime
├── .env.example                 # Environment variable template
├── pyproject.toml               # pytest configuration
└── requirements.txt
```

---

## Quick Start

### 1. Clone and set up a virtual environment

```bash
git clone https://github.com/divyaganapathi/Unified_test_automation.git
cd Unified_test_automation
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright browsers (for UI tests)

```bash
playwright install chromium      # or: playwright install   (all browsers)
```

### 4. Configure environment variables (optional)

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY, API_BASE_URL, etc.
```

---

## Running Tests

### All tests

```bash
pytest
```

### Unit tests only (no network required)

```bash
pytest tests/test_framework_units.py -v
```

### API tests only

```bash
pytest tests/api/ -v -m api
```

### UI tests only

```bash
pytest tests/ui/ -v -m ui
```

### Smoke tests

```bash
pytest -m smoke -v
```

### With HTML report

```bash
pytest --html=reports/report.html --self-contained-html
```

### With JSON report (for AI analysis)

```bash
pytest --json-report --json-report-file=reports/report.json
```

### Parallel execution (4 workers)

```bash
pytest -n 4
```

---

## Configuration

All settings live in `config/config.yaml`.  
Any value can be overridden with an environment variable (see `.env.example`).

Key settings:

```yaml
api:
  base_url: https://jsonplaceholder.typicode.com
  timeout: 30

ui:
  base_url: https://example.com
  browser: chromium   # chromium | firefox | webkit
  headless: true

ai:
  model: gpt-4o-mini
  enabled: true       # set false to disable without errors
```

---

## Writing Tests

### API test

```python
import pytest
from framework.api import APIClient, APIAssertions

@pytest.mark.api
def test_get_user(api_client: APIClient) -> None:
    response = api_client.get("/users/1")
    (
        APIAssertions(response)
        .status(200)
        .has_key("id", "name", "email")
        .key_equals("id", 1)
        .response_time_under(2000)
    )
```

### UI test (page-object model)

```python
import pytest
from framework.ui.page import BasePage
from playwright.sync_api import Page

class LoginPage(BasePage):
    URL = "/login"

    def login(self, username: str, password: str) -> None:
        self.page.get_by_label("Username").fill(username)
        self.page.get_by_label("Password").fill(password)
        self.page.get_by_role("button", name="Login").click()

@pytest.mark.ui
def test_successful_login(page: Page) -> None:
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("admin", "secret")
    login_page.assert_url_contains("/dashboard")
```

### AI test generation

```python
from framework.ai import TestGenerator

gen = TestGenerator()  # requires OPENAI_API_KEY in .env

# Generate API tests from a description
code = gen.generate_api_tests(
    "POST /orders accepts {userId, items[], total} and returns 201 with {orderId}"
)
print(code)

# Generate UI tests
code = gen.generate_ui_tests("Search page: enter query, press Enter, see results list")
print(code)
```

### AI test analysis

```python
from framework.ai import TestAnalyzer

analyzer = TestAnalyzer()

# Analyze a pytest JSON report
summary = analyzer.analyze("reports/report.json")
print(summary)
```

---

## AI Features

AI features require an **OpenAI API key**.  
Without the key the framework works fully — AI features silently return empty strings / rule-based summaries.

Set the key in your `.env`:

```
OPENAI_API_KEY=sk-...
```

### What AI can do

* **Test generation** — Describe an endpoint or page in plain English and get ready-to-run pytest functions.
* **Failure analysis** — Feed it a JSON report and get a plain-English diagnosis with root causes and next steps.

---

## Markers

| Marker | Usage |
|---|---|
| `@pytest.mark.api` | API tests |
| `@pytest.mark.ui` | UI tests |
| `@pytest.mark.smoke` | Critical smoke tests |
| `@pytest.mark.regression` | Full regression suite |
| `@pytest.mark.slow` | Long-running tests |

---

## License

MIT
