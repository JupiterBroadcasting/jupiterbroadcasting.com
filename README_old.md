# Jupiter Broadcasting MVP

Build with Hugo and deployed with Github Actions

Demo: https://jb.codefighters.net

https://github.com/JupiterBroadcasting/jupiterbroadcasting.com/discussions/8#discussioncomment-2731384

## Features

* Static Site using Hugo
* Complete publishing workflow using Github and Github Actions
* Template using SCSS (without node dependencies using Hugo extended)
* only Vanilla JS is used (single files with concat workflow)
* Highly configurable with config.toml and config folder
* Hosts (via data folder and frontmatter)
* Video player
* HTML5 audio player
* Multishow capable
* Tags (via frontmatter)
* Guests (via data folder and frontmatter)
* Sponsors (via data folder and frontmatter)

## ToDo

* RSS feed generation
* Search Function (probably Lunr)
* Contact Form (?)
* adding more content
* write better docs

## Setup

### Using Hugo binary

Install Hugo: https://gohugo.io/getting-started/installing/

Start the development Server (rebuild on every filesystem change)

`hugo server -D`

### Using Docker

To build and run the docker image:
`make run`

### run for different Site

`hugo server -D --config config.coderradio.toml`

to clean the module config

`hugo mod clean --all`


build

`hugo -D --config config.coderradio.toml`

Hugo issue currently regarding overlapping mounts

https://github.com/gohugoio/hugo/issues/7123

so for now only subdirectories work

## Deployment

Deployment is done with Github Actions, see workflow file in `.github/workflows/main.yml`
At the moment it is only triggered when something in the `main` branch is changing, but it can also be set up to run at certain times.
This would also enable scheduled publishing, since Hugo per default only build pages which have set `date` in frontmatter to <= `now`


## Fireside Scraper

The [fireside-scraper](./fireside-scraper/) is based on [JB Show Notes](https://github.com/selfhostedshow/show-notes) that was written by [ironicbadger](https://github.com/ironicbadger).

It goes over all the JB firside shows and scrapes the episodes into the format that is expected by hugo for each episode (using [this template](./fireside-scraper/src/templates/episode.md.j2)).

Besides the episodes it also scrapes and creates the json files for:

- sponsors
- hosts
- guests (every host is symlinked into the [guests dir](./data/guests/) since a host of one show, could be a guest on an episode of a different show)

There are makefile commands that should me used to run it.

### Run the scraper

The command below would build, and start up the container which would save all the data into `scraped-data` dir.

```
make scrape
```

The files are organised in the same way as the files in the root project. This makes it very trivial to just copy the contents of `scraped-data` over to the root dir of the repo to include all the scraped content. And it can be done with:

```
make scrape-copy
```

or you could just run the following to scrape and copy over the root dir all at once:

```
make scrape-full
```

### Configuring the scraper

Configure the scraper by modifying this [config.yml file](./fireside-scraper/src/config.yml)

## Credits

- I took parts of the functionality from the Castanet Theme: https://github.com/mattstratton/castanet
Mainly the RSS feed generation and managing of hosts / guests.

- [ironicbadger](https://github.com/ironicbadger) and [JB Show Notes](https://github.com/selfhostedshow/show-notes) project which was used as the base for the `fireside-scraper`

Time spend so far: 13h
