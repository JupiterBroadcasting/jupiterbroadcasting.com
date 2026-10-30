# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ . }}
{{ end }}
Episode index for this show: [llms.txt](/show/{{ .File.ContentBaseName }}/llms.txt)

{{ partial "llms-body.html" . }}
