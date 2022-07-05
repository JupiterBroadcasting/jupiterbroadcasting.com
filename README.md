# JupiterBroadcasting.com, et al. Websites

## Repo here includes issue tracking for:
  * [JupiterBroadcasting.com](https://jupiterbroadcasting.com)
  * [LINUX Unplugged](https://linuxunplugged.com/)
  * [Self-Hosted](https://selfhosted.show/)
  * [Coder Radio](https://coder.show/)
  * [Linux Action News](https://linuxactionnews.com/)
  * [Jupiter Extras](https://extras.show/)
  * [Office Hours](https://www.officehours.hair/)

## New Jupiter Broadcasting Hugo website
* [Discussion on implementation, technologies to consider, etc](https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/discussions/8)
* [Main discussion space for work underway via Matrix](https://matrix.to/#/#jupiterweb:jupiterbroadcasting.com)

---

Built with Hugo and deployed with Github Actions

Demo: https://jupiterbroadcasting.net

### Setup

#### Using Hugo binary

Install Hugo: https://gohugo.io/getting-started/installing/

Start the development Server (rebuilds on every filesystem change)

`hugo server -D`

#### Using Docker

To build and run the docker image:
`make run`

#### run for different Site

`hugo server -D --config config.coderradio.toml`

to clean the module config

`hugo mod clean --all`

build

`hugo -D --config config.coderradio.toml`

Hugo issue currently regarding overlapping mounts

https://github.com/gohugoio/hugo/issues/7123

so for now only subdirectories work

#### Deployment

Deployment is done with Github Actions, see workflow file in `.github/workflows/main.yml`
At the moment it is only triggered when something in the `main` branch is changing, but it can also be set up to run at certain times.
This would also enable scheduled publishing, since Hugo per default only builds pages which have set `date` in frontmatter to <= `now`

### Credits

- I took parts of the functionality from the Castanet Theme: https://github.com/mattstratton/castanet
Mainly the RSS feed generation and managing of hosts / guests.

- [ironicbadger](https://github.com/ironicbadger) and [JB Show Notes](https://github.com/selfhostedshow/show-notes) project which was used as the base for the [show-scraper](https://github.com/JupiterBroadcasting/show-scraper)

## Content Migration and Scraper

We moved the scraper to it's own repository here: https://github.com/JupiterBroadcasting/show-scraper
Much love to https://github.com/kbondarev aka Kiro in Matrix <3!
