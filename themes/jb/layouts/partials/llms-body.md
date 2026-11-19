{{- /* Markdown body of a page with front matter stripped.
       JSON content pages: .RawContent is already body-only.
       TOML (+++) and YAML (---) pages: strip the front matter block.
       .md extension: no HTML escaping of the output. */ -}}
{{- $raw := .RawContent -}}
{{- $raw = replaceRE `(?s)\A\+\+\+.*?\n\+\+\+` "" $raw -}}
{{- $raw = replaceRE `(?s)\A---.*?\n---` "" $raw -}}
{{- $raw -}}
