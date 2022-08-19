const { defineConfig } = require("cypress");

module.exports = defineConfig({
  video: false,
  env: {
    'BASE_URL': 'http://localhost:1313'
  },
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
