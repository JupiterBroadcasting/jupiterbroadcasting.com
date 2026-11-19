# {{ .Title }}

URL: {{ .Permalink }}

{{ partial "person-details.md" . }}

Episodes: [{{ .Params.username }} on guests]({{ .Site.BaseURL }}guests/{{ .Params.username }}/index.md)
