# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ . }}
{{ end }}
- Show: [{{ .Params.show_name }}]({{ .Site.BaseURL }}show/{{ .Params.show_slug }}/)
- Episode: {{ .Params.episode }}
- Date: {{ .Date.Format "2006-01-02" }}
{{ with .Params.hosts }}- Hosts: {{ delimit . ", " }}
{{ end }}{{ with .Params.guests }}- Guests: {{ delimit . ", " }}
{{ end }}{{ with .Params.podcast_duration }}- Duration: {{ . }}
{{ end }}{{ with .Params.podcast_file }}- Audio: {{ . }}
{{ end }}{{ with .Params.youtube_link }}- YouTube: {{ . }}
{{ end }}
{{ partial "llms-body.md" . }}
