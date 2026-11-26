# End-to-end cases (human + agent)

Agent-runnable locally. Human-only in ChatGPT/Claude after a public HTTPS URL exists.

| ID | Surface | Prompt / input | Expected |
| --- | --- | --- | --- |
| E1 | CLI | `python -m circuit draw examples/iso_sequence/circuit.yaml` | exit 0, SVGs under `output/` |
| E2 | CLI | YAML with `magic_valve` | exit 1, `That symbol is not in the pack.` |
| E3 | CLI | comment `simulate pressure drop` | refuse physics |
| E4 | MCP stdio | `list_symbols` | ids include `dcv_5_2_double_solenoid` |
| E5 | MCP stdio | `draw_spec` ISO YAML | image content |
| E6 | MCP stdio | `get_sheet` without YAML | error: full spec YAML |
| E7 | Workspace | open `web/index.html`, Example, Generate | pneumatic SVG, no Fly request |
| E8 | TIMER | `benchmarks/sequencebench/cases/case_15.yaml` | verify PASS, `T1` on electrical |
| E9 | Cascade | `meta.method: cascade` on ISO example | PASS, `G1` on pneumatic |
| E10 | Deadlock | START-only `1Y1` | verify FAIL, not PASS |
| E11 | Bench 300 | `python -m circuit bench --suite 300` | n=300, accepted_error_rate 0 |
| E12 | Bench LLM | `python -m circuit bench --suite llm` | paid_api_calls 0 |

ChatGPT/Claude: run E1–E6 against the public `/mcp` URL after hosting. Do not treat local stdio success as directory eligibility.
