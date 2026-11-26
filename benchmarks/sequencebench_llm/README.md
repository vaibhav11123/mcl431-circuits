# SequenceBench-LLM

Fixture “model outputs,” not live API calls.

Each `llm_*.yaml` is a typical generator artifact. `llm_*.prompt.txt` is the prompt that would have produced it. `llm_*.expected.json` is the **compiler** decision.

```bash
python -m circuit bench --suite llm
```

`paid_api_calls` is always 0. Do not wire this harness to OpenAI, Anthropic, or any billed endpoint.
