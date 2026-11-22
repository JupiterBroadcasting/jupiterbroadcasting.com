# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ . }}
{{ end }}
{{ range .Pages }}- [{{ .Title }}]({{ partial "markdown-url.html" . }})
{{ end }}
