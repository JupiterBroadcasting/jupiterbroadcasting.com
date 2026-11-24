# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ . }}
{{ end }}
{{- $eps := where .Pages "Type" "episode" -}}
{{- $summary := partial "show-episode-summary.html" . }}
- Status: {{ if .Params.active }}active{{ else }}archived{{ end }}
- Episodes: {{ len $eps }}
{{ with .Params.hosts }}- Hosts: {{ range $i, $h := . }}{{ if $i }}, {{ end }}{{ partial "person-md-link.html" $h }}{{ end }}
{{ end }}
{{- with site.GetPage (printf "/show/%s/subscribe" .Params.show) }}{{ with .Params.rss }}- RSS feed: [{{ . }}]({{ . }})
{{ end }}{{ end }}
{{- with .Params.podverse_podcast_id }}{{ $u := print "https://podverse.fm/podcast/" . }}- Podverse: [{{ $u }}]({{ $u }})
{{ end }}
{{- with .OutputFormats.Get "llms" }}- Episode index: [llms.txt]({{ .Permalink }})
{{ end }}
{{- with .OutputFormats.Get "episodes" }}- Every episode: [episodes.json]({{ .Permalink }})
{{ end }}
{{- with .Params.links }}
## Links

{{ range $name, $link := . }}{{ with $link.url }}- {{ $name }}: {{ cond (hasPrefix . "/") (absURL .) . }}
{{ end }}{{ end }}{{ end }}
## Episodes

{{ with $summary.numbered -}}
- Numbered episodes: {{ .first }} to {{ .last }}, at `{{ $.Permalink }}<number>.md`
{{ with .missing }}- Missing numbers: {{ delimit . ", " }}
{{ end }}{{ end }}
{{- range first 1 $eps.ByDate.Reverse }}- Latest episode: {{ .Params.episode }} · {{ .Date.Format "2006-01-02" }} · [{{ trim .Title " " }}]({{ partial "markdown-url.html" . }})
{{ end }}
{{- with $summary.special }}- Special episodes (not plain numbers):
{{ range . }}  - {{ .Params.episode }} · {{ .Date.Format "2006-01-02" }} · [{{ trim .Title " " }}]({{ partial "markdown-url.html" . }})
{{ end }}{{ end }}
{{/* the description already sits in the blockquote above, so About keeps only what follows it */ -}}
{{ with trim (strings.TrimPrefix (trim $.Description " \t\r\n") (trim (replaceRE `<br\s*/?>` "" (partial "llms-body.md" .)) " \t\r\n")) " \t\r\n" }}## About

{{ . }}
{{ end }}