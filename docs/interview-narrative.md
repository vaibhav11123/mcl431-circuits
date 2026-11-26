# Interview opening

Sequence Circuit is not an AI circuit generator. The language model is an untrusted frontend. It may propose a YAML spec. A deterministic compiler decides whether that spec is allowed to become a sheet.

The CS problem is translation validation for a tiny electropneumatic language: independent source (`spec_trace`) versus target (`env_trace`, sensors from modeled actuators). Pretty SVG that fails eval is not returned.

What to clone and run:

```bash
pip install -e ".[dev]"
python -m circuit draw examples/iso_sequence/circuit.yaml
python -m circuit verify examples/iso_sequence/circuit.yaml
python -m circuit bench benchmarks/sequencebench
```

Related work we analogize, not copy: Alive2 (src vs tgt + counterexample), Csmith (well-defined programs + oracle), Hypothesis stateful tests. We do not claim CompCert. We do not ship FluidSIM. We do not copy FluidPyPLC.

The public ISO pack is vectors plus two Wikimedia CC-BY 5/2 and 5/3 rasters. Lecture crops stay in the course pack.
