# JSON API

Static JSON generated at build time for every show and episode. No auth, no server; plain GETs.

## URLs

| Level | URL | Content |
|---|---|---|
| Episode list | `/show/<slug>/episodes.json` | All episodes of a show, newest first |
| Show | `/show/<slug>/show.json` | One show |
| Episode | `/show/<slug>/<slug>.json` | One episode; the slug is the lowercase episode slug, usually the episode number (`693.json`, or `t-0.json` for special episodes) |

Navigation: `episodes.json` entries carry `json_url` -> episode JSON -> its `show.json_url` -> show JSON.
Show JSON links back to `episodes.json` via `episodes_url` and to its newest episode via `latest_episode.json_url`.

URLs in the payloads follow the site `baseURL` (absolute on production).

## Versioning

`schema_version` is an integer present on episode and show records. Additive changes (new fields) keep it at `1`; consumers must ignore unknown fields. Removing or renaming a field, or changing a type, bumps it.

## Omission rules

- Array fields are always present, as `[]` when empty.
- Fields that are null or absent in the source are omitted at every depth (including inside chapters and transcripts), never emitted as `null`.
- Dates are RFC 3339 (`2026-11-16T05:29:00Z`).

## Episode (`<NNNN>.json`)

Always present unless noted "omitted when absent".

| Field | Type | Presence |
|---|---|---|
| `schema_version` | integer (`1`) | always |
| `type` | string (`"episode"`) | always |
| `url` | string | always |
| `markdown_url` | string | always |
| `show` | object: `slug`, `name`, `url`, `json_url`, `markdown_url`, `llms_url` | always |
| `episode` | integer, or string for special episodes (e.g. `"T-0"`) | always |
| `title` | string | always |
| `description` | string | omitted when absent |
| `date` | string (RFC 3339) | always |
| `header_image` | string | omitted when absent |
| `tags` | array of string | always |
| `hosts` | array of `{slug, name, url}` | always |
| `guests` | array of `{slug, name, url}` | always |
| `sponsors` | array of `{shortname, name, url, description}` | always |
| `audio` | object: `url`, `bytes` (integer), `duration` (`HH:MM:SS`) | omitted when absent |
| `audio_alt_url` | string | omitted when absent |
| `audio_ogg_url` | string | omitted when absent |
| `video` | object: `url`, `hd_url`, `mobile_url` | omitted when absent |
| `youtube_url` | string | omitted when absent |
| `chapters` | array of chapter objects (`startTime`, `title`, `img`, `url`, ...), passed through as stored | omitted when absent |
| `transcripts` | array of `{type, url}`, passed through as stored | omitted when absent |

Keys inside `audio` and `video` are omitted individually when absent. Host and guest entries are resolved to names and their people-page URL. Sponsor entries carry the sponsor's name and description and `url`, the sponsor's own link (not a page on this site). An entry whose people or sponsor page does not exist carries only `slug` (or `shortname`). `chapters` items follow the [Podcasting 2.0 chapters format](https://github.com/Podcastindex-org/podcast-namespace/blob/main/chapters/jsonChapters.md).

## Show (`show.json`)

| Field | Type | Presence |
|---|---|---|
| `schema_version` | integer (`1`) | always |
| `type` | string (`"show"`) | always |
| `slug` | string | always |
| `name` | string | always |
| `description` | string | omitted when absent |
| `active` | boolean | always |
| `url` | string | always |
| `markdown_url` | string | always |
| `episodes_url` | string (`episodes.json`) | always |
| `llms_url` | string | omitted when the show has none |
| `header_image` | string | omitted when absent |
| `hosts` | array of `{slug, name, url}` | always |
| `links` | object `{name: url}`, `{}` when the show has none | always |
| `podverse_url` | string (`https://podverse.fm/podcast/<id>`) | omitted when absent |
| `episode_count` | integer | always |
| `latest_episode` | object: `episode`, `title`, `date`, `url`, `json_url` | omitted when the show has no episodes |
| `numbered_episodes` | object: `first`, `last` (integers), `missing` (array of integers, omitted when none) | omitted when the show has no numbered episodes |
| `special_episodes` | array of `{episode, title, date, url, json_url}`, oldest first | always |

## `episodes.json`

Pre-existing format; the only change is a new `json_url` on each entry pointing at that episode's JSON. Top level: `show`, `title`, `count`, `episodes`. Each entry: `slug`, `episode`, `title`, `hosts`, `guests`, `duration`, `date`, `url`, `json_url`, `transcripts`. It does not carry `schema_version`.

## Examples

List a show's episodes and take the newest episode's JSON URL:

```sh
curl -s https://jupiterbroadcasting.com/show/linux-unplugged/episodes.json | jq -r '.episodes[0].json_url'
```

Show metadata and latest episode:

```sh
curl -s https://jupiterbroadcasting.com/show/linux-unplugged/show.json | jq '{name, episode_count, latest: .latest_episode.json_url}'
```

One episode: title, audio URL and host names:

```sh
curl -s https://jupiterbroadcasting.com/show/linux-unplugged/0693.json | jq '{title, audio: .audio.url, hosts: [.hosts[].name]}'
```

## Finding every episode of a show

Numbered episodes `first` through `last` each live at `/show/<slug>/<n>.json`, except the numbers listed in `missing`. Numbering does not always start at 1 (Coder Radio, Linux Action News and Self-Hosted start at 0) and can have gaps (Jupiter Extras). Episodes without a number (`T-0`, `p01`, `hurricanehelene`) are not covered by that range; each has an entry in `special_episodes` with its own `json_url`. `episode_count` counts both kinds.
