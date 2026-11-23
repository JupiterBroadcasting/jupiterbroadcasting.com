We have many sponsors we love who support each show, and we hope you'll enjoy them too.
{{ range partial "sponsor/sections.html" . }}
## {{ .title }}

{{ range .sponsors }}{{ with index hugo.Data.sponsors . }}- [{{ .title }}]({{ .link }}){{ with .description }}: {{ . }}{{ end }}
{{ end }}{{ end }}{{ end -}}
