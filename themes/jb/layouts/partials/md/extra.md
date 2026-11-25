{{- /* What a page renders from front matter, data or child pages, as markdown; the JSON twins carry the same facts */ -}}
{{- if .Params.plan_groups -}}
{{ partial "membership/body.md" . }}
{{- else if and (eq .Type "sponsors") .IsSection -}}
{{ partial "sponsor/body.md" . }}
{{- else if and (eq .Type "picks") .IsPage -}}
{{ partial "picks/body.md" . }}
{{- else if and (eq .Section "community") .IsPage -}}
{{ with .Params.direct_link }}Link: {{ . }}{{ end }}
{{- else if and (eq .Section "community") .IsSection -}}
{{ range .Pages }}- [{{ .Title }}]({{ partial "markdown-url.html" . }}){{ with .Params.direct_link }} ({{ . }}){{ end }}{{ with .Description }}: {{ . }}{{ end }}
{{ end }}
{{- else if and .File (eq .File.BaseFileName "subscribe") -}}
{{ with .Params.rss }}RSS: {{ . }}
{{ end }}{{ range $app, $url := .Params.direct_links }}- {{ $app }}: {{ $url }}
{{ end }}
{{- else if eq .Type "calendar" -}}
iCalendar: {{ site.Params.calendar.rss }}
{{- else if and (eq .Section "live") .IsSection -}}
- Audio stream: {{ site.Params.live.audio_url }}
- Video stream: {{ site.Params.live.video_url }}

Latest episodes:
{{ range first 3 (where site.RegularPages "Type" "episode").ByDate.Reverse }}- [{{ .Title }}]({{ partial "markdown-url.html" . }})
{{ end }}
{{- else if and (eq .Section "people") .IsSection -}}
{{ range (where site.RegularPages "Section" "people").ByTitle }}- [{{ .Title }}]({{ partial "markdown-url.html" . }}) ({{ .Type }}{{ if .Params.is_archived }}, archived{{ end }})
{{ end }}
{{- else if and (eq .Section "show") .IsSection (eq .RelPermalink "/show/") -}}
{{ $shows := partial "json/shows.html" true }}{{ range slice (dict "title" "Active shows" "active" true) (dict "title" "Archived shows" "active" false) }}{{ $title := .title }}{{ $want := .active }}## {{ $title }}

{{ range $shows }}{{ if eq (.active | default false) $want }}- [{{ .name }}]({{ .markdown_url }}): {{ .episode_count }} episodes{{ with .description }}. {{ . }}{{ end }}
{{ end }}{{ end }}
{{ end }}
{{- else if and (eq .Section "archive") .IsSection -}}
{{ range partial "json/shows.html" false }}- [{{ .name }}]({{ .markdown_url }}): {{ .episode_count }} episodes{{ with .description }}. {{ . }}{{ end }}
{{ end }}
{{- end -}}
