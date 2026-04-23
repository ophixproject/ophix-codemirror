# ophix-codemirror

Vendored CodeMirror editor plugin for [ophix-server-base](https://github.com/ophixproject/ophix-server-base).

Bundles CodeMirror 5 as static assets and provides Django form widgets for use in the
admin interface. Air-gap safe — no CDN dependencies at runtime.

---

## Installation

```bash
pip install ophix-codemirror
```

---

## What this plugin provides

- Vendored CodeMirror 5.65.16 JavaScript and CSS assets
- `JSONCodeMirrorWidget` — JSON editor with fold gutter and auto pretty-print
- `DynamicCodeMirrorWidget` — format-switching editor; switches CodeMirror mode
  based on a format dropdown with `data-codemirror-mode` attributes on each option.
  Used by `ophix-confs` for configuration snippet editing.

---

## Usage

Used automatically by domain plugins that include a content editor in the admin.
`ophix-confs` wires `DynamicCodeMirrorWidget` into its `Configuration` admin form.
Other domains with content fields should use `DynamicCodeMirrorWidget` for any
format-aware text field.

```python
from ophix_codemirror.widgets import DynamicCodeMirrorWidget, JSONCodeMirrorWidget
```

---

## Server

This plugin is part of the [Ophix Project](https://ophix.io) server stack.
