# SequenceBench v0

30 original compiler cases. No lecture PYQs, no paper identifiers, no copies of grinding/emboss goldens.

Methodology: each `cases/*.yaml` has `cases/*.expected.json` with `{decision: accept|reject, reason}`.
`python -m circuit bench benchmarks/sequencebench` scores the **compiler**, not an LLM.

v1 (out of this execution): 300 cases and LLM baselines.
