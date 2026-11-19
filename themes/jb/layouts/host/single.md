# {{ .Title }}

URL: {{ .Permalink }}

{{ partial "person-details.md" . }}

Episodes: [{{ .Params.username }} on hosts]({{ .Site.BaseURL }}hosts/{{ .Params.username }}/index.md)
