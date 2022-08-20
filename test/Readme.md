# Jupuiter Brodcasting Site End to End Tests

These tests are setup using the [playwright](https://playwright.dev/python/docs/writing-tests) framework. They are intended to run on each commit to verify the site is working in expected order


## Getting Started

1. Create a python virtual environment

    `python -m venv .jbsite`

    `source ./.jbsite/bin/activate`

    `pip install -r requirements.txt`

    `playwright install`

2. Running E2E Tests

    `pytest --base-url http://localhost:1313 e2e/*`

3. Add your town test to the e2e folder and get coding!