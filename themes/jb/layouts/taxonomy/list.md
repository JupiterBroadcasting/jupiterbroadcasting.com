# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ . }}
{{ end }}
{{- range .Pages }}
- [{{ .Title }}]({{ .Permalink }}index.md)
{{- end }}
