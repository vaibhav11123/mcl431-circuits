# Directory submission copy (agent-prepared, human-submitted)

Do **not** log in, install, or submit from an agent. Directory listing requires a **public HTTPS** MCP origin. Local stdio MCP is not directory-eligible. Skills-only / desktop-only is a separate OpenAI path and still needs a human identity.

Replace `https://REPLACE_ON_DEPLOY` with the origin you actually host. Leave the placeholder if you have not hosted yet — then **do not submit**.

## ChatGPT / OpenAI plugin directory

Source: [Package your plugin](https://developers.openai.com/plugins/build/plugins), [Submit plugins](https://developers.openai.com/plugins/deploy/submission), [Plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines) (checked 2026-11-26).

| Field | Value to paste |
| --- | --- |
| Package ZIP | `python scripts/pack_plugin.py` → `dist/sequence-circuit-plugin.zip` from `plugin/` (plugin.json, mcp.json, skills/, PRIVACY.md, TERMS.md, assets/logo.svg) |
| Display name | Sequence Circuit |
| Short description | Verified ISO circuit compiler |
| Long description | From `plugin.json` `extensions.com.openai.interface.longDescription` |
| Developer name | your verified OpenAI developer identity |
| Category | pick a **currently listed** portal category; `developer-tools` is a draft guess |
| Website | `https://REPLACE_ON_DEPLOY/` |
| Support | `https://REPLACE_ON_DEPLOY/support` |
| Privacy policy | `https://REPLACE_ON_DEPLOY/privacy` |
| Terms | `https://REPLACE_ON_DEPLOY/terms` |
| MCP URL | `https://REPLACE_ON_DEPLOY/mcp` |
| Transport | streamable HTTP |
| Auth | none |
| Domain challenge | plain text at `https://<host>/.well-known/openai-apps-challenge` |
| Video walkthrough | you record after install; not in this repo |
| Reviewer credentials | none — no accounts |

### Positive test cases (exactly five)

1. Scenario: ISO two-cylinder. Prompt: paste `examples/iso_sequence/circuit.yaml`. Tools: `list_symbols`, `draw_spec`. Result: pneumatic PNG, sentence of executed checks.
2. Scenario: natural language. Prompt: `Draw A+ B+ B- A- with two 5/2 valves.` Tools: `list_symbols`, `draw_spec`. Result: sheets, 5/2 assumption on the report.
3. Scenario: TIMER. Prompt: `Clamp, wait 2 seconds, feed, return, unclamp.` Tools: `draw_spec`. Result: electrical sheet includes `T1`.
4. Scenario: missing picture. Prompt: `The chat has no picture. Get the pneumatic sheet.` Tools: `get_sheet` with the same YAML. Result: PNG.
5. Scenario: cascade two. Prompt: `Cascade method for A+ B+ B- A-.` Tools: `draw_spec`. Result: `G1` on the pneumatic sheet.

### Negative test cases (exactly three)

1. Invented id `magic_valve`. Expected: `That symbol is not in the pack.`
2. `Simulate the 4 bar pressure.` Expected: `No pressure physics.`
3. `Export FluidSIM .ct.` Expected: `We do not export FluidSIM .ct files.`

## Claude / Anthropic connectors directory

Source: [Submit a connector](https://claude.com/docs/connectors/building/submission), [Directory vs custom](https://claude.com/docs/connectors/building/directory-vs-custom) (checked 2026-11-26).

- Directory submit needs a paid Claude plan (Pro/Max/Team/Enterprise). Free cannot submit. **Do not buy a plan from this agent.**
- Custom connector: user pastes `https://REPLACE_ON_DEPLOY/mcp` at [Add custom connector](https://claude.ai/customize/connectors). Local `.mcpb` directory listings are deprecated.
- Tool titles and `readOnlyHint` / `destructiveHint` are already on the server.
- Listing: name `Sequence Circuit`, one-liner `Verified ISO circuit compiler`, description from plugin.json, documentation URL, privacy URL, support contact, icon `plugin/assets/logo.svg`.
- Auth: none.
- Test & launch: human must call every tool in Claude before submit.

## Eligibility blocker

Until `https://REPLACE_ON_DEPLOY/mcp` is a stable public HTTPS endpoint that you operate at zero extra spend (existing machine + tunnel, or equivalent), **directory submission is blocked**. CLI, stdio MCP, and the static Pyodide workspace still work.
