module.exports = {
  default: {
    require: [
      '**/step-definitions/**/*.ts',
      'hooks/**/*.ts'
    ],
    requireModule: ['tsx/cjs'],
    format: [
      'progress-bar',
      'html:test_automation/cucumber-report.html',
      'json:test_automation/cucumber-report.json',
      'junit:test_automation/cucumber-report.xml'
    ],
    formatOptions: {
      snippetInterface: 'async-await'
    },
    parallel: 1,
    retry: 0,
    dryRun: false,
    strict: true,
    timeout: 60000,
    paths: ['**/features/**/*.feature'],
    publish: false
  }
};
