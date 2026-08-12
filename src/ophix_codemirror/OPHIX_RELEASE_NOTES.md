# Ophix Codemirror Release Notes

## Unreleased

- Django dependency split by `python_version` marker: `Django>=4.2,<6.0` on Python < 3.12,
  `Django>=4.2` (no upper bound) on Python >= 3.12. Django 6.0 itself requires Python 3.12+;
  this makes the "Python 3.10/3.11 + Django 6" combination structurally unreachable via pip's
  resolver instead of failing at runtime, while still allowing 3.10/3.11 hosts to run on
  Django 5.2. `requires-python` is unchanged (`>=3.10` remains the true floor).

## 2026.06.05.01

- Dark mode support: CodeMirror editor now reskins to a dark colour scheme when the admin dark mode toggle is active (`[data-theme="dark"]`).

## 2026.05.26.01

- Added `OPHIX_RELEASE_NOTES.md` for release notes delivery.
