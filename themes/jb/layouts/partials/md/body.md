{{- /* Markdown body of a page with front matter stripped.
       JSON content pages: .RawContent is already body-only.
       TOML (+++) and YAML (---) pages: strip the front matter block.
       {{< ref "/x" >}} shortcodes are not rendered in .RawContent, so they become absolute URLs.
       .md extension: no HTML escaping of the output. */ -}}
{{- $raw := .RawContent -}}
{{- $raw = replaceRE `(?s)\A\+\+\+.*?\n\+\+\+` "" $raw -}}
{{- $raw = replaceRE `(?s)\A---.*?\n---` "" $raw -}}
{{- $raw = replaceRE `\{\{<\s*ref\s+"/?([^"]*?)/?"\s*>\}\}` (print (strings.TrimSuffix "/" site.BaseURL) "/$1/") $raw -}}
{{- /* scraped notes carry HTML entities in link titles; Markdown readers see them as literal text */ -}}
{{- range slice (slice "&#x27;" "'") (slice "&#39;" "'") (slice "&quot;" "\"") (slice "&amp;" "&") }}{{ $raw = replace $raw (index . 0) (index . 1) }}{{ end -}}
{{- $raw -}}
