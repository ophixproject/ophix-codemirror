"""
ophix_codemirror.widgets
~~~~~~~~~~~~~~~~~~~~~~~~
Django form widgets backed by the vendored CodeMirror editor.

Three widgets are provided:

CodeMirrorWidget
    Base widget.  The CodeMirror mode is set at construction time and
    does not change.  Use this when the format is always fixed.

JSONCodeMirrorWidget
    Subclass of CodeMirrorWidget pre-configured for JSON: javascript
    syntax highlighting, fold gutter for collapsing objects/arrays, and
    automatic pretty-printing of the value on load.

DynamicCodeMirrorWidget
    The mode switches dynamically when a format dropdown changes.
    Each <option> in the dropdown must carry a ``data-codemirror-mode``
    attribute set by the admin's ``formfield_for_foreignkey`` override.
    Use for fields like ophix-conf's Configuration.content where the
    format is user-selectable.

All widgets require the CodeMirror static files to be present under::

    ophix_codemirror/codemirror/codemirror.min.js
    ophix_codemirror/codemirror/codemirror.min.css
    ophix_codemirror/codemirror/mode/<mode>.min.js   (per mode)

The default theme is embedded in codemirror.min.css — no separate theme file
is required for default styling.

See the README in the static directory for download instructions.
"""

import json

from django import forms
from django.templatetags.static import static as _static
from django.utils.safestring import mark_safe


# ---------------------------------------------------------------------------
# Static base path helper
# ---------------------------------------------------------------------------

_STATIC_PREFIX = "ophix_codemirror/codemirror"


class _CodeMirrorMediaMixin:
    """Mixin that declares the core CodeMirror static file dependencies."""

    class Media:
        css = {
            "all": (
                f"{_STATIC_PREFIX}/codemirror.min.css",
            )
        }
        js = (
            f"{_STATIC_PREFIX}/codemirror.min.js",
        )


# ---------------------------------------------------------------------------
# Base CodeMirror widget
# ---------------------------------------------------------------------------

class CodeMirrorWidget(_CodeMirrorMediaMixin, forms.Textarea):
    """
    Textarea replacement that initialises a CodeMirror editor.

    Parameters
    ----------
    mode
        CodeMirror mode name (e.g. ``"javascript"``, ``"yaml"``, ``"xml"``).
        If None, CodeMirror runs in plain-text mode (no highlighting).
    mode_file
        Relative path under ``ophix_codemirror/codemirror/`` to the mode
        JS file (e.g. ``"mode/javascript.min.js"``).
        If None, no mode file is loaded dynamically (use when the mode JS
        is already declared in the widget's Media class).
    extra_cm_options
        Dict of additional CodeMirror options merged into the editor config.
        Use this in subclasses to enable addons (e.g. foldGutter).
    """

    def __init__(
        self,
        mode: str | None = None,
        mode_file: str | None = None,
        extra_cm_options: dict | None = None,
        *args,
        **kwargs,
    ):
        self.cm_mode = mode
        self.cm_mode_file = mode_file
        self.extra_cm_options = extra_cm_options or {}
        kwargs.setdefault("attrs", {})
        kwargs["attrs"].setdefault("rows", 20)
        kwargs["attrs"].setdefault("style", "font-family: monospace;")
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        textarea_html = super().render(name, value, attrs, renderer)

        static_base = _static('ophix_codemirror/codemirror/')

        cm_options = {
            'lineNumbers': True,
            'matchBrackets': True,
            'indentWithTabs': False,
            'indentUnit': 2,
            'tabSize': 2,
            'lineWrapping': False,
            'theme': 'default',
        }
        cm_options.update(self.extra_cm_options)
        cm_options_json = json.dumps(cm_options)

        mode_js = ""
        if self.cm_mode_file:
            mode_js = (
                f"loadModeFile(staticBase + {json.dumps(self.cm_mode_file)}, "
                f"function() {{ editor.setOption('mode', {json.dumps(self.cm_mode or 'text/plain')}); }});"
            )
        elif self.cm_mode:
            mode_js = f"editor.setOption('mode', {json.dumps(self.cm_mode)});"

        script = f"""
<script>
(function() {{
    var loadedModes = {{}};

    function loadModeFile(src, callback) {{
        if (loadedModes[src]) {{ if (callback) callback(); return; }}
        var s = document.createElement('script');
        s.src = src;
        s.onload = function() {{ loadedModes[src] = true; if (callback) callback(); }};
        document.head.appendChild(s);
    }}

    function initEditor() {{
        var textarea = document.getElementById('id_{name}');
        if (!textarea || textarea._cm) return;

        var staticBase = {json.dumps(static_base)};

        var editor = CodeMirror.fromTextArea(textarea, {cm_options_json});
        textarea._cm = editor;

        editor.on('change', function() {{ editor.save(); }});

        {mode_js}
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initEditor);
    }} else {{
        setTimeout(initEditor, 100);
    }}
}})();
</script>
"""
        return mark_safe(textarea_html + script)


# ---------------------------------------------------------------------------
# JSON widget — syntax highlighting + fold gutter + pretty-print
# ---------------------------------------------------------------------------

class JSONCodeMirrorWidget(CodeMirrorWidget):
    """
    CodeMirror widget for JSONField editing.

    - Syntax highlighting via the javascript mode.
    - Fold gutter: click the margin arrow to collapse any object or array.
    - Value is pretty-printed (2-space indent) on load so compact stored
      JSON is immediately human-readable.
    """

    class Media:
        css = {
            "all": (
                f"{_STATIC_PREFIX}/codemirror.min.css",
                f"{_STATIC_PREFIX}/addon/fold/foldgutter.min.css",
            )
        }
        js = (
            f"{_STATIC_PREFIX}/codemirror.min.js",
            f"{_STATIC_PREFIX}/mode/javascript.min.js",
            f"{_STATIC_PREFIX}/addon/fold/foldcode.min.js",
            f"{_STATIC_PREFIX}/addon/fold/foldgutter.min.js",
            f"{_STATIC_PREFIX}/addon/fold/brace-fold.min.js",
        )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('extra_cm_options', {})
        kwargs['extra_cm_options'].setdefault('foldGutter', True)
        kwargs['extra_cm_options'].setdefault(
            'gutters', ['CodeMirror-linenumbers', 'CodeMirror-foldgutter']
        )
        super().__init__(
            mode="javascript",
            mode_file=None,  # already declared in Media above
            *args,
            **kwargs,
        )

    def render(self, name, value, attrs=None, renderer=None):
        # Pretty-print the JSON before handing to the editor.
        if value not in (None, '', 'null'):
            try:
                parsed = json.loads(value) if isinstance(value, str) else value
                value = json.dumps(parsed, indent=2, ensure_ascii=False)
            except (ValueError, TypeError):
                pass
        return super().render(name, value, attrs, renderer)


# ---------------------------------------------------------------------------
# Dynamic mode widget (for ophix-conf style format dropdowns)
# ---------------------------------------------------------------------------

# Mapping from CodeMirror mode name to mode file path.
# Used by DynamicCodeMirrorWidget's JavaScript to load the correct file
# when the format dropdown changes.
CODEMIRROR_MODE_FILES = {
    "javascript": "mode/javascript.min.js",
    "yaml":       "mode/yaml.min.js",
    "xml":        "mode/xml.min.js",
    "properties": "mode/properties.min.js",
    "toml":       "mode/toml.min.js",
}


class DynamicCodeMirrorWidget(_CodeMirrorMediaMixin, forms.Textarea):
    """
    CodeMirror widget whose mode switches dynamically when a format
    dropdown changes.

    Each <option> in the format dropdown must carry a
    ``data-codemirror-mode`` attribute — set by the admin's
    ``formfield_for_foreignkey`` override.

    The mode file map is passed to JavaScript as a JSON object so the
    correct mode JS file is loaded lazily on first use.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {})
        kwargs["attrs"].setdefault("rows", 20)
        kwargs["attrs"].setdefault("style", "font-family: monospace;")
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        textarea_html = super().render(name, value, attrs, renderer)

        mode_map_json = json.dumps(CODEMIRROR_MODE_FILES)
        static_base = _static('ophix_codemirror/codemirror/')

        script = f"""
<script>
(function() {{
    var modeFiles = {mode_map_json};
    var loadedModes = {{}};

    function loadModeFile(modeFile, callback) {{
        if (loadedModes[modeFile]) {{ if (callback) callback(); return; }}
        var s = document.createElement('script');
        s.src = {json.dumps(static_base)} + modeFile;
        s.onload = function() {{ loadedModes[modeFile] = true; if (callback) callback(); }};
        document.head.appendChild(s);
    }}

    function getSelectedMode() {{
        var sel = document.getElementById('id_format');
        if (!sel) return null;
        var opt = sel.options[sel.selectedIndex];
        return opt ? opt.getAttribute('data-codemirror-mode') : null;
    }}

    function setEditorMode(editor) {{
        var mode = getSelectedMode();
        if (!mode) {{ editor.setOption('mode', 'text/plain'); return; }}
        var modeFile = modeFiles[mode];
        if (modeFile) {{
            loadModeFile(modeFile, function() {{ editor.setOption('mode', mode); }});
        }} else {{
            editor.setOption('mode', mode);
        }}
    }}

    function initEditor() {{
        var textarea = document.getElementById('id_{name}');
        if (!textarea || textarea._cm) return;

        var editor = CodeMirror.fromTextArea(textarea, {{
            lineNumbers: true,
            matchBrackets: true,
            indentWithTabs: false,
            indentUnit: 2,
            tabSize: 2,
            lineWrapping: false,
            theme: 'default',
        }});
        textarea._cm = editor;
        editor.on('change', function() {{ editor.save(); }});

        setEditorMode(editor);

        var formatSelect = document.getElementById('id_format');
        if (formatSelect) {{
            formatSelect.addEventListener('change', function() {{ setEditorMode(editor); }});
        }}
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initEditor);
    }} else {{
        setTimeout(initEditor, 100);
    }}
}})();
</script>
"""
        return mark_safe(textarea_html + script)
