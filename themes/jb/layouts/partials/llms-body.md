{{- /* Markdown body of a page with front matter stripped.
       JSON content pages: .RawContent is already body-only.
       TOML (+++) and YAML (---) pages: strip the front matter block.
       {{< ref "/x" >}} shortcodes are not rendered in .RawContent, so they become absolute URLs.
       Pages whose content lives in front matter or data append it (membership plans, sponsors, picks).
       .md extension: no HTML escaping of the output. */ -}}
{{- $raw := .RawContent -}}
{{- $raw = replaceRE `(?s)\A\+\+\+.*?\n\+\+\+` "" $raw -}}
{{- $raw = replaceRE `(?s)\A---.*?\n---` "" $raw -}}
{{- $raw = replaceRE `\{\{<\s*ref\s+"/?([^"]*?)/?"\s*>\}\}` (print (strings.TrimSuffix "/" site.BaseURL) "/$1/") $raw -}}
{{- $raw -}}
{{- if .Params.plan_groups }}
{{ partial "membership/body.md" . }}
{{- else if and (eq .Type "sponsors") .IsSection }}
{{ partial "sponsor/body.md" . }}
{{- else if and (eq .Type "picks") .IsPage }}
{{ partial "picks/body.md" . }}
{{- end -}}
