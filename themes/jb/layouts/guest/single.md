# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Params.username }}Username: {{ . }}
{{ end }}
{{ with .Params.bio }}{{ . }}
{{ end }}
{{- with .Params.homepage }}
Homepage: {{ . }}
{{- end }}
{{- with .Params.twitter }}
Twitter: {{ . }}
{{- end }}
{{- with .Params.linkedin }}
LinkedIn: {{ . }}
{{- end }}
{{- with .Params.instagram }}
Instagram: {{ . }}
{{- end }}
{{- with .Params.youtube }}
YouTube: {{ . }}
{{- end }}

Episodes: [{{ .Params.username }} on hosts]({{ .Site.BaseURL }}hosts/{{ .Params.username }}/index.md)
