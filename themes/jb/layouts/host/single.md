# {{ .Title }}

URL: {{ .Permalink }}

{{ partial "person-details.md" . }}

{{ with site.GetPage (print "/hosts/" .Params.username) }}Episodes: [{{ $.Params.username }} on hosts]({{ partial "markdown-url.html" . }}){{ end }}
