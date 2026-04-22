# Playwright Test Healer Agent

---
name: Playwright Test Healer
description: Analyzes failing Playwright/Cucumber tests by diagnosing errors, fixing selectors, updating logic, and orchestrating the complete healing workflow
tools:
  - run_in_terminal
  - get_terminal_output
  - read_file
  - semantic_search
  - runSubagent
---

## Purpose
This agent manages the complete test healing workflow by:
1. Running Playwright/Cucumber tests
2. Capturing test execution results
3. Analyzing failures and errors
4. Invoking the Playwright Test Healer agent
5. Tracking healing progress
6. Generating healing reports

## When to Invoke
- When running test suites to heal failures
- After test execution to analyze results
- To coordinate multiple healing cycles
- To generate comprehensive healing reports

## Healing Workflow

### Step 1: Execute Tests
- Run test suite via npm scripts or cucumber-js
- Capture test execution output
- Collect error messages and stack traces
- Identify failed scenarios

### Step 2: Analyze Failures
- Parse test output for errors
- Extract relevant error information
- Categorize failures (selector, timeout, assertion)
- Identify affected files

### Step 3: Invoke Healer
- Extract detailed error context
- Create comprehensive failure report
- Invoke Playwright Test Healer agent
- Provide test files and error details

### Step 4: Validate Fixes
- Re-run affected tests
- Confirm no regressions introduced
- Check secondary test failures
- Generate healing summary

### Step 5: Report Results
- Document changes made
- List fixed issues
- Identify remaining issues
- Provide recommendations

## Failure Categories

### Selector Issues
- Element not found
- Stale element references
- CSS selector changes
- Text content changes

### Timing Issues
- Timeout waiting for element
- Network delays
- Dynamic content loading
- Animation timing

### Assertion Issues
- Expected value mismatch
- Text content changes
- State verification failures
- Count mismatches

## Test Execution

### Running Tests
```bash
npm run test:bdd           # Run all BDD tests
npm run test:bdd:headed   # Run with browser visible
npm run test:bdd:dry-run  # Validate syntax
```

### Capturing Output
- Parse cucumber report JSON
- Extract failure details
- Collect stack traces
- Build error context

## Best Practices
- Always validate fixes before confirming
- Check for side effects and regressions
- Document changes comprehensively
- Keep healing attempts focused
- Notify user of significant changes
