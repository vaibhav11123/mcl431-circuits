# Distribution record

Started 2026-11-26 IST. Zero mandatory spend. Directory login is human-only.

| Channel | Status | How |
| --- | --- | --- |
| GitHub `main` | this release | merge compiler + PYQ corpus |
| CLI / PyPI-local | go | `pip install -e ".[dev]"` |
| Static workspace | go | serve `web/` or GitHub Pages |
| GitHub Pages | **live** `https://vaibhav11123.github.io/mcl431-circuits/` | Actions source; workflow `.github/workflows/pages.yml` |
| Cursor / Claude Desktop stdio MCP | go | `plugin/mcp.stdio.json` |
| Loopback HTTP MCP | go | `python -m circuit.mcp_server --http` |
| Plugin ZIP | go | `python scripts/pack_plugin.py` → `dist/sequence-circuit-plugin.zip` |
| Personal HTTPS MCP (zero-spend) | **live while laptop + tunnel up** | Cloudflare Worker `https://sequence-circuit-mcp.sequence-circuit.workers.dev` → named Tunnel → local `:8080`. Not always-on. |
| ChatGPT directory | **blocked** | needs **always-on** public HTTPS + your login. Personal workers.dev is for DEVELOPMENT only. Copy: `plugin/SUBMISSION.md` |
| Claude directory | **blocked** | needs always-on public HTTPS + paid Claude plan (you). Custom connector is URL-only |
| Fly.io | SKIPPED_OPTIONAL | not deployed |
| PyPI | not this release | no package publish |
| Twitter/X, LinkedIn | copy in `docs/marketing.md` | GitHub Release `v0.1.0-distribution` posted; X/LinkedIn still need your login |
| Demo recording | [release mp4](https://github.com/vaibhav11123/mcl431-circuits/releases/download/v0.1.0-distribution/sequence-circuit-workspace-demo.mp4); GIF on README | `docs/release-assets/sequence-circuit-workspace-demo.mp4` + `workspace-demo.gif` |

## GitHub About / topics

Set via `gh` when landing a release: description `Verification-oriented compiler for AI-generated engineering systems.`, homepage `https://vaibhav11123.github.io/mcl431-circuits/`, topics include `iso-1219`, `pneumatics`, `compilers`, `mcp`, `verification`, `electropneumatics`, `hydraulics`, `iit-delhi`, `mcl431`, `pyq`.

## Checklist you still own

1. ~~Merge/push / Pages~~ done.
2. ChatGPT custom MCP (DEVELOPMENT) with workers.dev URL — your login; delete/recreate if stuck on loca.lt.
3. Always-on `/mcp` **only if** you want directory listing — not the laptop tunnel.
4. Directory submit / Claude paid directory — [HUMAN_ACTIONS_REQUIRED.md](ops/HUMAN_ACTIONS_REQUIRED.md).
5. Post the launch copy. Do not say Fly or directory-listed.
