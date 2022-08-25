# Jupiter Broadcasting Site End to End Tests

These tests are setup using the [playwright](https://playwright.dev/python/docs/writing-tests) framework. They are intended to run on each commit to verify the site is working in expected order


## Getting Started

1. Create a python virtual environment
    Install [pipenv](https://pipenv.pypa.io/en/latest/)

    `pipenv install`

    `pipenv shell`

    `playwright install`

2. Run the hugo server

    `make dev`

3. Running E2E Tests

    `pytest --base-url http://localhost:1313 e2e/*`

4. Add your own test to the e2e folder and get coding!