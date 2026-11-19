{{ $person := site.GetPage (printf "/people/%s" .Data.Term) }}# {{ with $person }}{{ .Title }}{{ else }}{{ .Title }}{{ end }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ . }}
{{ end }}
{{ if $person }}{{ partial "person-details.md" $person }}
{{ end }}
{{ range .Pages }}- [{{ .Title }}]({{ .Permalink }}index.md)
{{ end }}
