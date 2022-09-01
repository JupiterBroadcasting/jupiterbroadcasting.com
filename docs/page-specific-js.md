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
2. Go find whichever partial your code belongs to, `fancy.html`, and put all of the following in a `{{ define "headcontent" }}` hugo block
3. Add a Hugo reference to the HTML

    ``` go
    {{ $fancy := resources.Get "js/fancy.js" }}
    ```

4. Add an in production block, so the JS can be properly minified via hugo

    ```go
    {{ if hugo.IsProduction }}
      {{ $fancy = $fancy | minify | fingerprint }}
    {{ end }}
    ```

5. Add a `script` tag for the processed JS

    ``` html
    <script type="text/javascript" src="{{ $fancy.PermaLink }}" integrity="{{ $fancy.Data.Integrity }}"></script>
    ```

6. Call your function
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

Example below:

```html
{{ define "headcontent" }}
  {{ $fancy := resources.Get "js/fancy.js" }}
  {{ if hugo.IsProduction }}
    {{ $fancy = $fancy | minify | fingerprint }}
  {{ end }}
  <script type="text/javascript" src="{{ $fancy.Permalink }}" integrity="{{ $fancy.Data.Integrity }}"></script>
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
{{ end }}

```

### Adding to Main

1. Add a function to `themes/jb/assets/js/main.js`
2. Call your function
    - See [above](###adding-to-a-partial), point 5
