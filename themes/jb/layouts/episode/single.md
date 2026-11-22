# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ . }}
{{ end }}
- Show: [{{ .Params.show_name }}]({{ .Site.BaseURL }}show/{{ .Params.show_slug }}/)
- Episode: {{ .Params.episode }}
- Date: {{ .Date.Format "2006-01-02" }}
{{ with .Params.hosts }}- Hosts: {{ range $i, $h := . }}{{ if $i }}, {{ end }}{{ partial "person-md-link.html" $h }}{{ end }}
{{ end }}{{ with .Params.guests }}- Guests: {{ range $i, $g := . }}{{ if $i }}, {{ end }}{{ partial "person-md-link.html" $g }}{{ end }}
{{ end }}{{ with .Params.podcast_duration }}- Duration: {{ . }}
{{ end }}{{ with .Params.podcast_file }}- Audio: {{ . }}
{{ end }}{{ with .Params.youtube_link }}- YouTube: {{ . }}
{{ end }}
{{ with .Params.transcripts }}
## Transcripts

{{ range . }}- [{{ or .type "transcript" }}]({{ .url }})
{{ end }}{{ end }}
{{ with .Params.sponsors }}
## Sponsors

{{ range . }}{{ $sp := index (where (where site.Pages "Section" "sponsors") "Params.shortname" .) 0 }}{{ with $sp }}- [{{ .Title }}]({{ partial "markdown-url.html" . }}){{ with .Description }}: {{ . }}{{ end }}
{{ end }}{{ end }}
{{ end }}
{{ with trim (replaceRE `\A(?:\s*(?:#{1,6}\s*|\*\*)Episode Links(?:\*\*)?:?[ \t]*(?:\n|\z))+` "" (trim (partial "llms-body.md" .) "\n\r\t ")) "\n\r\t " }}## Show Notes

{{ . }}
{{ end }}