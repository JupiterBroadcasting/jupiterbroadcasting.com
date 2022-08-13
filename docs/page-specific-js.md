# How to Add JS for a Page
1. Make JS
2. Add a Hugo variable
3. Import script with Hugo variable
4. ...
5. Debug!

## Make JS
You'll need to modify the theme that's applied to the markdown that Hugo processes in order to add new JS to any pages. First, ask yourself if __everyone__ needs to have this or if it can be added in a partial.

### Ading to a Partial
1. Add your fancy new JS in a file, `fancy.js` in `themes/jb/assets/js`
2. Go find whichever partial your code belongs to, `fancy.html`
3. Add a Hugo reference to the HTML
    ``` go
    {{ $fancy := resources.Get "js/fancy.js" }}
    ```
4. Add a `script` tag for the processed JS
    ``` html
    <script src="{{ $fancy.PermaLink }}"></script>
    ```
5. Call your function
    - You probably know how to do this best!
    ```html
    // Example call for async function
    <script>
        window.onload = () => {
            /**
             * When window loads, call async function. Attach a callback
             * to the Promise resolving, `.then(...)`, and rejecting,
             * `.catch(...)`.
             */
            fancy()
                .then(result => document.getElementById('targetId))
                .catch(error => console.error(error), '')
        }
    </script>
    ```

### Adding to Main
1. Add a function to `themes/jb/assets/js/main.js`
2. Call your function
    - See [above](###adding-to-a-partial), point 5