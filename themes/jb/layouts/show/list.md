# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ . }}
{{ end }}
{{ with .OutputFormats.Get "llms" }}Episode index for this show: [llms.txt]({{ .Permalink }})
{{ end }}
{{ with site.GetPage (printf "/show/%s/subscribe" .Params.show) }}
{{ with .Params.rss }}RSS feed: [{{ . }}]({{ . }})
{{ end }}{{ end }}

{{ partial "llms-body.md" . }}
