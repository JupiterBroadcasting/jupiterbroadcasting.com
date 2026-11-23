Picks from JB Shows, please feel free to make a PR to submit past picks.
{{ range hugo.Data.picks }}
- [{{ .title }}]({{ .url }}){{ with .license }} ({{ . }}){{ end }}{{ with .description }}: {{ . }}{{ end }}
{{- with partial "picks/episodes.html" . }}
  - Picked on:{{ range $i, $e := . }}{{ if $i }},{{ end }} [{{ $e.show_name }} {{ $e.episode }}]({{ strings.TrimSuffix "/" $e.url }}.md){{ end }}
{{- end }}
{{- end }}
