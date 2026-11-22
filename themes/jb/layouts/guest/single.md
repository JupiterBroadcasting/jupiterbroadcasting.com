# {{ .Title }}

URL: {{ .Permalink }}

{{ partial "person-details.md" . }}

{{ with site.GetPage (print "/guests/" .Params.username) }}Episodes: [{{ $.Params.username }} on guests]({{ partial "markdown-url.html" . }}){{ end }}
