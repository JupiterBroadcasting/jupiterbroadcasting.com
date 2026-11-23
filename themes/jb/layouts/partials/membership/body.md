{{- range .Params.plan_groups }}
### {{ .title }}
{{ with .description }}{{ . }}
{{ end }}
{{ range .plans }}- [{{ .name }}]({{ .url }}){{ with .description }}: {{ . }}{{ end }}
{{ end }}{{ end }}
### Special Features Available via Memberships
{{ range .Params.perks }}{{ $show := site.GetPage (print "/show/" .show) }}
#### [{{ $show.Title }}]({{ $show.Permalink }})

{{ range .items }}- {{ .name }}{{ with .description }}: {{ . }}{{ end }}
{{ end }}{{ end -}}
