# {{ .Title }}

URL: {{ .Permalink }}
{{ with .Description }}> {{ replaceRE `(?m)^> $` ">" (replaceRE `[ \t]*\r?\n` "\n> " (trim . " \t\r\n")) }}
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

{{ range . }}{{ with index hugo.Data.sponsors . }}- [{{ .title }}]({{ .link }}){{ with .description }}: {{ . }}{{ end }}
{{ end }}{{ end }}
{{ end }}
{{/* only newlines are trimmed from the left: the first list item's indent must match the rest or Markdown nests them */ -}}
{{ with strings.TrimRight "\n\r\t " (strings.TrimLeft "\r\n" (replaceRE `\A(?:\s*(?:#{1,6}\s*|\*\*)Episode Links(?:\*\*)?:?[ \t]*(?:\n|\z))+` "" (strings.TrimLeft "\r\n" (partial "llms-body.md" .)))) }}## Show Notes

{{ . }}
{{ end }}