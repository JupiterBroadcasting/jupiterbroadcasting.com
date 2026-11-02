# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ . }}
{{ end }}
{{ if eq .Kind "term" }}
{{ with site.GetPage (printf "/people/%s" .Title) }}{{ partial "person-details.md" . }}
{{ end }}
{{ range .Pages }}- [{{ .Title }}]({{ .Permalink }}index.md)
{{ end }}
{{ else }}
{{ range .Pages }}- [{{ .Title }}]({{ .Permalink }}index.md)
{{ end }}
{{ end }}