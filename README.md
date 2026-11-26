# Sequence Circuit

Verification-oriented compiler for AI-generated engineering systems.

The language model is **untrusted**. It may propose a YAML circuit spec. A deterministic compiler decides whether that spec is allowed to become a sheet. A pretty drawing that fails eval is not returned.

This is not an AI circuit generator. The compiler has authority over correctness.

## Three commands

```bash
pip install -e ".[dev]"
python -m circuit draw examples/iso_sequence/circuit.yaml
python -m circuit verify examples/iso_sequence/circuit.yaml
```

Workspace (editable sheets, download pack, sequence explorer): [`web/`](web/). Use from ChatGPT or Claude **or open the workspace**.

MCP (optional): `python -m circuit.mcp_server --http`

## Related work

- FluidSIM — commercial simulator. We do not export `.ct`.
- FluidPyPLC (GPL) — **do not copy**. Cascade here is `meta.method: cascade` plus extra `dcv_5_2` valves.
- spec2schematic, Weave, CADPilot/CADX — model-written geometry. We are stricter: the model never writes geometry.
- Alive2 — independent src vs tgt check. Our analog is `spec_trace` vs `env_trace` (sensors from modeled actuators), not SMT, not CompCert.

## Three load-bearing decisions

1. Fail-closed `draw_yaml` and CLI `draw`: eval/verify fail → no sheet. `--unverified` watermarks.
2. Independent translation validation (T36), not a second call to the synthesizer.
3. Public ISO pack is vector + two Wikimedia CC-BY 5/2 and 5/3 rasters. Lecture PNG never ships in the public SVG.

Refused work: physics simulation, FluidSIM, OAuth, hosted LLM, lecture-PDF ingest on the public pack.

Eval failures are listed in `output/*/eval.json`. `circuit verify` writes `verify.json` with `physics: not_evaluated` for checks that were not run.
