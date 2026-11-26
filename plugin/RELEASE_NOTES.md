# Sequence Circuit 0.1.0 — plugin notes

Not submitted. Do not treat this file as a directory listing.

## What the reviewer should see

A YAML sequence becomes ISO/L8 sheets only if `draw_yaml` / `verify` passes. Failures return English, not a pretty wrong drawing.

## Package

```bash
python scripts/pack_plugin.py
# dist/sequence-circuit-plugin.zip
```

Replace `https://REPLACE_ON_DEPLOY` in `plugin.json` and `mcp.json` **before** you zip for a directory upload. If the placeholder is still there, do not submit.

## Not in this ZIP

Lecture PDFs, PYQ scans, Fly tokens, LLM API keys.
