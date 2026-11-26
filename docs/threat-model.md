# Threat model

Assets: compiler authority, ISO pack isolation, chat PNG, YAML submitted to MCP.

Adversaries: a host LLM that invents symbols; a client that skips `draw_yaml`; a pack that tries to load lecture crops; a prompt that asks for FluidSIM `.ct` or a pressure simulator.

Trust boundary: `service.draw_yaml` and CLI `draw` (without `--unverified`). The model is an untrusted frontend. Sheets exist only after validate, eval, and — for the ISO pack — `verify_spec` PASS.

Not in scope: physical machine safety, hosted LLM, OAuth, accounts.

| ID | Threat | Control | Status if skipped |
| --- | --- | --- | --- |
| T-LLM | Pretty sheet from a wrong ladder | Fail-closed draw; planted dual-solenoid | FAIL |
| T-CLI | `python -m circuit draw` bypass | CLI draw calls `draw_yaml` | FAIL |
| T-UNV | Operator force-emits | `--unverified` watermark | not a PASS |
| T-PACK | ISO SVG embeds lecture PNG | `Glyph.path` refuses `lecture/crops` | FileNotFoundError |
| T-YAML | 256KiB bomb | `MAX_YAML_BYTES` | spec too large |
| T-DEPTH | nested YAML | `MAX_YAML_DEPTH` 24 | spec too deep |
| T-LIMIT | huge machines | 8 cylinders / 32 steps / 16 valves | too many |
| T-ZIP | path traversal / bomb | `verify_zip` member and size caps | ValueError |
| T-LOG | YAML in MCP logs | log `ok=` only | — |
| T-PHYS | Treat logical PASS as safety cert | footer + `physics: NOT_EVALUATED` | NOT_EVALUATED |
| T-BOUND | Mutex truncated still green | `INCONCLUSIVE`, never PASS | INCONCLUSIVE |
