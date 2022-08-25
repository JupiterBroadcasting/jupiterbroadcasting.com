# Jupiter Broadcasting Site End to End Tests

## Testing Methodology
These tests are setup using the [Playwright](https://playwright.dev/python/docs/writing-tests) framework. They are intended to run on each commit to verify the site is working in expected order.s

These tests exist to make sure code changes to this repository do not break how the site currently function. 

On every commit, these tests will be run against the commited code. The tests will verify that the site is in proper working order with respect to the changes the commiter has changed.

The reason for this is so that one can feel more confient that their changes will not cause issues on site when it is deployed in production. The goal is to catch these issues well before they make it to production thus not causing headaches for anyone maintaining the site.


These tests are written in python using the pytest framework in conjunection with the [playwright](https://playwright.dev/python/docs/writing-tests) framework.

Playwright is a framework which easily allows you so spin up a headless browser and write code to verify specific elements and content on the page exist. 

For example, you can check that the logo on the header nav exists or that a page contains a subtitle with a specific text of "Hello World"

Each file in the `e2e` should contain a test related to a certain page. The file will test for element on that specific page only (ie the home page, or the coder radio show page)

Each method in the test file will load the page its is planning to test 
```
page.goto("/")
```

And then once on that page, the test will grab element on the page by querying the page with a selector. The selector is most commonly a css selector (or xpath) similar to what you would use with `document.querySelector`
```
first_card = page.locator('.card')
```
This creates a variable called first card which contains the dom element that has a classname (ie the '.' selector) of card `<div class='.card'>`

Once there is a variable with an element you can make assertion against the content of that element as to what you expect to be in that element.
```
expect(first_contain).to_contain_text('Hello World')
```

This means we are verifying there is an element on the page that looks like this
```
<div class='card'>Hello World </div>
```

If such an element does exist, the test will passes. Otherwise the test will fail.

You can checkout the playwright documentation for more extensive testing methods. s

## Getting Started

1. Create a python virtual environment
    Install [pipenv](https://pipenv.pypa.io/en/latest/)

    `pipenv install`

    `pipenv shell`

    `playwright install`

2. Run the hugo server

    `make dev`

3. Running E2E Tests (in a new terminal window)
    `make test`

4. Add your own test to the e2e folder and get coding!
