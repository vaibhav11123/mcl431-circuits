# Distribution record

Started 2026-11-26 IST. Zero mandatory spend. Directory login is human-only.

| Channel | Status | How |
| --- | --- | --- |
| GitHub `main` | this release | merge compiler + PYQ corpus |
| CLI / PyPI-local | go | `pip install -e ".[dev]"` |
| Static workspace | go | serve `web/` or GitHub Pages |
| GitHub Pages | enable in repo Settings → Pages → GitHub Actions | workflow `.github/workflows/pages.yml` |
| Cursor / Claude Desktop stdio MCP | go | `plugin/mcp.stdio.json` |
| Loopback HTTP MCP | go | `python -m circuit.mcp_server --http` |
| Plugin ZIP | go | `python scripts/pack_plugin.py` → `dist/sequence-circuit-plugin.zip` |
| ChatGPT directory | **blocked** | needs public HTTPS + your login. Copy: `plugin/SUBMISSION.md` |
| Claude directory | **blocked** | needs public HTTPS + paid Claude plan (you). Custom connector is URL-only |
| Fly.io | SKIPPED_OPTIONAL | not deployed |
| PyPI | not this release | no package publish |
| Twitter/X, LinkedIn | copy in `docs/marketing.md` | you post |
| Demo recording | [release mp4](https://github.com/vaibhav11123/mcl431-circuits/releases/download/v0.1.0-distribution/sequence-circuit-workspace-demo.mp4); GIF on README | `docs/release-assets/sequence-circuit-workspace-demo.mp4` + `workspace-demo.gif` |

## GitHub topics to add (Settings → General, or `gh repo edit`)

`iso-1219`, `pneumatics`, `compilers`, `mcp`, `verification`, `electropneumatics`, `hydraulics`

Existing: `electropneumatics`, `hydraulics`, `iit-delhi`, `iso-1219`, `mcl431`, `pyq`.

## GitHub About

Verification-oriented compiler for AI-generated engineering systems.

Homepage (after Pages is on): `https://vaibhav11123.github.io/mcl431-circuits/`

## Checklist you still own

1. Merge/push is done by the agent when you asked to land on `main`.
2. Enable GitHub Pages (Actions source) if you want a public workspace URL.
3. Host `/mcp` on hardware you already have **only if** you want directory listing.
4. ChatGPT / Claude login and submit — [HUMAN_ACTIONS_REQUIRED.md](../HUMAN_ACTIONS_REQUIRED.md).
5. Post the launch copy. Do not say Fly or directory-listed.
