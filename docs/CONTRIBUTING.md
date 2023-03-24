**Firstly, thank you for being here! We appreciate you ❤️**

---
## Table of Contents

- [Table of Contents](#table-of-contents)
- [Lets Be Efficient!](#lets-be-efficient)
- [Discussions via Matrix](#discussions-via-matrix)
- [FAQ:](#faq)
  - [I want to help, what should I work on?](#i-want-to-help-what-should-i-work-on)
  - [How do I assign an issue to myself?](#how-do-i-assign-an-issue-to-myself)
  - [What is the Pull-Request (PR) etiquette?](#what-is-the-pull-request-pr-etiquette)
  - [What is the stack used for the site?](#what-is-the-stack-used-for-the-site)
  - [I don't see a package.json file, why don't you use npm/yarn?](#i-dont-see-a-packagejson-file-why-dont-you-use-npmyarn)
  - [How do I style my UI components?](#how-do-i-style-my-ui-components)
  - [How to Add JS for a page]

---

## Let's Be Efficient!

Our top priority is to hopefully avoid wasting anyone's time/effort (including yours!) on items that may eventually not be used. We want to spend time/effort on things that get implemented! 

Here are three steps to being efficient:

* 1️⃣ Obtain context on the **greater vision 🔭** before beginning work to make sure you contribution will be accepted;
* 2️⃣ Get a consultation on that **grand new idea you may have 🤔** before implementing anything to see if it is something that is wanted;
* 3️⃣ Use the advice we give you to ensure that anything you contribute **works well with all the moving pieces🏗**. 

Often these discussions end up very, very fascinating and land us in elegant solutions we could not have predicted.

## Discussions via Matrix

Our base of operations for group discussions on this project is our Matrix chat room: [Jupiter Web Site on Matrix](https://matrix.to/#/#jupiterweb:jupiterbroadcasting.com)


## FAQ:

### I want to help, what should I work on?

**❗ Note:** _Please do a quick search prior to opening an issue - maybe a relevant issue already exists._ 😉

* 🚀 The current focus and priority is on [Milestone 1.0](https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/milestone/1)
* 📝 You can submit an idea or a feature by opening an [issue](https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/issues).
* 💡 When you feel inspired about a particular issue or feature, please propose your implementation idea/strategy for approval via the issue comments, which indicates you are dedicated to solving this issue, thus avoiding duplication of effort.
* 💪 If you have a particular skillset, feel free to focus there.
* 🚩 Some tickets are specifically [labeled](https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/labels) _"low priority"_, but others are so far of fairly equal importance. Any time there is something clearly urgent, the _"urgent"_ tag will be used.


### How do I assign an issue to myself?

* 🔑 The key is to communicate enough to avoid unnecessary duplication of effort, which has already happened, unfortunately.
* 🗨 Comment on an issue to signal your intentions and interest. The important thing is to communicate your intention and progress so we can help you find success. And, as we've seen already, it seems like when there's movement on a ticket we all get inspired. Progress is wonderfully contagious! ✨

### What is the Pull-Request (PR) etiquette?

* 💻 Don't be shy, creating a Work-In-Progress (WIP) PR is a great way to get some feedback and maybe some direction for your work.
* ✅ Create a markdown checklist to indicate what's done and what's still missing ([see this example](https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/pull/112)).
* ⚙ If you are closing a specific issue we encourage you to use [Github's closing keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword) to automatically close the issue once the PR is merged.
* 🚮 Feel free to delete your feature branch after it has been merged via the PR. There’s a handy button on the GitHub interface, and in the worst case they can be reverted easily.
* 🎯 We currently use a `develop` branch as our default, so expect your PRs to target `develop` and not the otherwise standard `main` branch
* 🚀 We've also integrate PR deploy previews for the current `develop` branch - see the Environment section of the repo's main page sidebar. All PRs also get their own unique deploy previews found as a comment under the respective PR.


### What is the stack used for the site?

* [Hugo](https://gohugo.io/) - static site generator
* [Bulma](https://bulma.io/) - frontend framework for UI componenets

### I don't see a package.json file, why don't you use npm/yarn?

* There was a deliberate choice not to integrate npm/yarn.
* It makes it easier to start contributing - all that's required is the Hugo binary.
* The goal is to keep the site simple and fast - this means having as few dependecies as possible.
* The third-party libraries are saved directly into the repo.
* All of this is subject to change if there is a good reason for it.

### How do I style my UI components?

* Please try to use [Bulma](https://bulma.io/) as much as possible for all your frontend needs. It has a great documentation and is easy to grasp quickly. You can probably achieve everything you need using the Bulma CSS classes.
* Try and use the color variables defined in [_variables.sass](./themes/jb/assets/css/_variables.sass)
  * Some of the colors have multiple aliases for convenience.
  * All of these colors have been set-up for use with [Bulma modifiers syntax](https://bulma.io/documentation/overview/modifiers/#docsNav), here are some examples:
    ```
    <button class="button is-primary">is-jb-pink</button>
    <button class="button is-jb-pink">is-jb-pink</button>
    <button class="button is-lup-blue">is-lup-blue</button>
    ```
* If you end up not finding what you need there, or need to build something on top of Bulma, your CSS (technically SASS) would go into this [directory](./themes/jb/assets/css). 
  * Please try and follow the existing structure as an example.

### How to Add JS for a Page

1. Make JS
2. Add a Hugo variable
3. Import script with Hugo variable
4. ...
5. Debug!

#### Make JS

You'll need to modify the theme that's applied to the markdown that Hugo processes in order to add new JS to any pages. First, ask yourself if __everyone__ needs to have this or if it can be added in a partial.

#### Ading to a Partial

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

#### Adding to Main

1. Add a function to `themes/jb/assets/js/main.js`
2. Call your function
    - See [above](###adding-to-a-partial), point 5


---

Other than that - have fun! 🐧

...and don't be shy - [gitmoji.dev](https://gitmoji.dev/) 🌱
