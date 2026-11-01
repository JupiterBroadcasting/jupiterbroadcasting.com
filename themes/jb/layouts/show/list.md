# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ . }}
{{ end }}
{{ with .OutputFormats.Get "llms" }}Episode index for this show: [llms.txt]({{ .Permalink }})
{{ end }}

{{ partial "llms-body.md" . }}
