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

---

## Lets Be Efficient!

Top priority is to hopefully avoid using anyone's time/effort - including yours! - on items that may eventually not be used. We want to spend time/effort on things that get implemented! 
Thus it's good practice to get consult first on a new grand idea you may have, and obtain context on the greater vision before beginning work to make sure you can implement in the way that ends up best for all the moving pieces. Often these discussion end up very, very fascinating and land us in elegant solutions we could not have predicted.

## Discussions via Matrix

Our base of operations for group discussions on this project: [Jupiter Web Site on Matrix](https://matrix.to/#/#jupiterweb:jupiterbroadcasting.com)


## FAQ:

### I want to help, what should I work on?

* 🚀 The current focus and priority is on [Milestone 1.0](https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/milestone/1)
* 📝 You can submit an idea or a feature by opening an [issue](https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/issues).
  * _Please do a quick search prior - maybe a relevant issue already exists_ 😉
* 💡 When you feel inspired about a particular issue or feature, please propose your implementation idea/strategy for approval via  comments, which indicates you are dedicated to solving this issue, thus avoiding duplication of effort.
* 💪 If you have a particular skillset, feel free to focus there.
* 🚩 Some tickets are specifically [labeled](https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/labels) _"low priority"_, but others are so far of fairly equal importance. Anytime there is something clearly urgent, the _"urgent"_ tag will be used.


### How do I assign an issue to myself?

* 🔑 The key is to communicate enough to avoid unnecessary duplication of efforts, which has already happened unfortunately
* 🗨 Comment on an issue to signal your intentions and interest. The important thing is to communicate your intention and progress so we can help you find success. And, as we've seen already: it seems like when there's movement on a ticket we all get inspired aswell. Progress is wonderfully contagious! ✨

### What is the Pull-Request (PR) etiquette?

* 💻 Don't be shy of creating a Work-In-Progress (WIP) PR. This is a great way to geat some feedback and maybe some direction on your work.
  * ✅ Create a markdown checklist to indicate what's done and what's still missing ([see this example](https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/pull/112))
* ⚙ If you're closing a specific issue I encourage you to use [Github's closing keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword) to automatically close the issue once it the PR is merged.
* 🚮 Feel free to delete your feature branch after it has been merged via the PR. There’s a button handy on the GitHub interface, and worst case they can be reverted easily.


### What is the stack used for the site?

* [Hugo](https://gohugo.io/) - static site generator
* [Bulma](https://bulma.io/) - frontend framework for UI componenets

### I don't see a package.json file, why don't you use npm/yarn?

* There was a deliberate choice not to integrate npm/yarn.
* It makes it easier to start contributing - all that's required is the Hugo binary.
* The goal is to clean the site simple and fast - this means having as little dependecies as possible.
* The third-party libraries are saved directly into the repo.
* All this is subject to change if there would be a good reason for it.

### How do I style my UI components?

* Please try to use [Bulma](https://bulma.io/) as much as possible for all your frontend needs. It has a great documentation and is easy to grasp quickly. You can probably achieve everythin you need using the Bulma CSS classes.
* If you end up not finding what you need there, or need to build somethin on top of Bulma, your CSS (technically SASS) would go into this [directory](themes/jb/assets/css). 
  * Please try and follow the existing structure as an example.

---

Other than that - have fun! 🐧
