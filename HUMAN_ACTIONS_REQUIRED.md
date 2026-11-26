# Human actions required

The agent must not log in to ChatGPT or Claude, must not install the plugin in those products, and must not submit to either directory.

## Already done in-repo (no login)

- Manifests: `plugin/plugin.json`, `plugin/mcp.json` (`url` still `https://REPLACE_ON_DEPLOY/mcp`)
- Local stdio config: `plugin/mcp.stdio.json`
- Privacy / terms / support markdown and `deploy/static/*.html`
- Review prompts: `plugin/REVIEW.md`, `plugin/GOLDEN_PROMPTS.md`
- Form copy and test cases: `plugin/SUBMISSION.md`
- E2E table: `plugin/E2E_TESTS.md`
- Demo stills: `docs/release-assets/demo-*.png` (and SVG)
- Logo: `plugin/assets/logo.svg`
- MCP tool titles + readOnly/destructive/openWorld hints: `src/circuit/mcp_server.py`

## You must do

### A. Optional public HTTPS (only if you want directory listing)

Use hardware or a tunnel you already have. Do **not** buy Fly for this. See `docs/self-hosting.md`.

1. Run `python -m circuit.mcp_server --http --host 0.0.0.0 --port 8080` behind HTTPS.
2. Serve `/privacy`, `/terms`, `/support` (the process already maps those routes from `deploy/static/`).
3. Put the OpenAI challenge token as **plain text** at `https://<host>/.well-known/openai-apps-challenge`.
4. Replace every `https://REPLACE_ON_DEPLOY` in `plugin/mcp.json` and `plugin/plugin.json` with that origin.
5. `curl -sS https://<host>/health` → `{"ok": true}`.
6. Confirm streamable HTTP at `https://<host>/mcp`.

Until step 4 is a real hostname, **do not submit**.

### B. ChatGPT — login, install, directory (you)

Portal: [Plugins](https://developers.openai.com/plugins) → upload ZIP of `plugin/` → [Submit plugins](https://developers.openai.com/plugins/deploy/submission).

Paste from `plugin/SUBMISSION.md`: display name, short description, five positive and three negative cases, listing URLs.

Skills-only / desktop-only is a different OpenAI path if you refuse to host HTTP. That still needs your verified developer identity. Local MCP is not a directory listing.

### C. Claude — login, custom connector, directory (you)

- Custom connector (no directory review): [Add custom connector](https://claude.ai/customize/connectors) with URL `https://<host>/mcp`.
- Directory: [Submit a connector](https://claude.com/docs/connectors/building/submission). Anthropic currently requires a **paid** Claude plan to submit. Do not purchase from this agent. Free custom-connector use of a URL you already host is separate from directory listing.
- Local `.mcpb` directory submissions are deprecated.

### D. End-to-end with you in the chat client

Run `plugin/E2E_TESTS.md` rows E1–E6 against the public URL. Agent already ran the CLI/MCP in-process equivalents.

### E. Student study (faculty/TA)

`docs/user-study.md` is a protocol. Do not invent completion rates.

## Blocker (evidenced)

Public directory distribution requires a publicly reachable HTTPS MCP service. This repository does not provide one. Local MCP does not establish directory eligibility.
