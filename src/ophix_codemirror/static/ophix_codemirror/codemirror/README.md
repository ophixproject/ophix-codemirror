# CodeMirror vendored static files

This directory must be populated with CodeMirror assets before the
editor widgets will function.  The server will start without them —
affected fields fall back to plain textareas.

## Required files

```
codemirror.min.js
codemirror.min.css
theme/
    default.min.css
mode/
    javascript.min.js   (JSON and JavaScript)
    yaml.min.js
    xml.min.js
    properties.min.js   (INI and .env files)
    toml.min.js
```

## Download URLs (CodeMirror 5.65.x)

```
https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js
https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css
https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/default.min.css
https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/javascript/javascript.min.js
https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/yaml/yaml.min.js
https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/xml/xml.min.js
https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/properties/properties.min.js
https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/toml/toml.min.js
```

## Adding a new mode

1. Download the mode JS file from the CDN above
2. Place it in mode/
3. Add it to CODEMIRROR_MODE_FILES in ophix_codemirror/widgets.py
4. Release a new version of ophix-codemirror
