# Changelog

## 0.1.0 — 2026-11-26 IST

Verification-oriented compiler for sequence circuits. The model proposes YAML; the compiler authorizes sheets.

### Compiler

- Fail-closed `draw_yaml` and CLI `draw` (`--unverified` watermarks)
- Independent `spec_trace` vs `env_trace` (discrete TIMER ticks, deadlock FAIL)
- Cascade grouping with electrical step-memory; fluid group-line topology not evaluated
- Pressure waits `UNSUPPORTED`; physics `NOT_EVALUATED`
- SequenceBench v0 (30), SequenceBench-300, SequenceBench-LLM fixtures (no paid APIs)

### Distribution (zero spend)

- CLI + stdio MCP + loopback HTTP MCP
- Static Pyodide workspace in `web/`
- Plugin manifests in `plugin/` (ChatGPT/Claude directory still need a human HTTPS origin)
- Fly.io is SKIPPED_OPTIONAL and is **not** deployed

### Course pack

- MCL 431 lecture goldens and PYQ corpus remain on the lecture pack
- Public ISO pack does not ship lecture crops
