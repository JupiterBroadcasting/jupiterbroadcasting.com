{{- /* Markdown body (md/body.md), then whatever the page renders from front matter or data (md/extra.md) */ -}}
{{- partial "md/body.md" . -}}
{{- with partial "md/extra.md" . }}
{{ . }}
{{- end -}}
