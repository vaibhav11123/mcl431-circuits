#!/usr/bin/env node
/** Reproduce T14: Pyodide 314 draw_yaml of the ISO example.
 *  PYODIDE_PACKAGE=/path/to/pyodide npm package directory
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const YAML = `meta:
  title: ISO two-cylinder 5/2 sequence
  domain: pneumatic_plus_electrical
  patterns: [ep_dac_5_2, sequence_double_solenoid]
sequence:
  - { action: 1A+, label: hold strip }
  - { action: 2A+, label: feed }
  - { action: 2A-, label: retract feed }
  - { action: 1A-, label: release }
power: { pumps: [], tank: "" }
cylinders:
  1A: { dcv: 1V, sensors: [1B1, 1B2] }
  2A: { dcv: 2V, sensors: [2B1, 2B2] }
motors: {}
valves:
  1V: { type: dcv_5_2_double_solenoid, solenoids: [1Y1, 1Y2] }
  2V: { type: dcv_5_2_double_solenoid, solenoids: [2Y1, 2Y2] }
sensors: [1B1, 1B2, 2B1, 2B2]
electrical: { convention: lecture, paths: [] }
`;

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const pkg = process.env.PYODIDE_PACKAGE || "/tmp/pyodide-run/package";
const { loadPyodide } = await import(
  createRequire(import.meta.url).resolve(join(pkg, "pyodide.mjs"))
);
const pyodide = await loadPyodide({ indexURL: pkg.endsWith("/") ? pkg : pkg + "/" });
console.log("pyodide loaded");
await pyodide.loadPackage("micropip");
const micropip = pyodide.pyimport("micropip");
await micropip.install(["pydantic", "pyyaml"]);
await pyodide.runPythonAsync("import pydantic, yaml");
console.log("import pydantic, yaml");
const zip = new Uint8Array(readFileSync(join(root, "web/circuit-iso.zip")));
pyodide.unpackArchive(zip, "zip");
pyodide.FS.writeFile("/tmp/iso.yaml", YAML);
const svg = await pyodide.runPythonAsync(`
from circuit.service import draw_yaml
from circuit.ir.from_spec import compile_report
from circuit.spec import CircuitSpec
from pathlib import Path
text = Path("/tmp/iso.yaml").read_text()
out = draw_yaml(text)
sheet = (out.get("sheets") or {}).get("pneumatic") or ""
spec = CircuitSpec.from_yaml("/tmp/iso.yaml")
print("graph", compile_report(spec)["graph_sha256"])
print("ok", out.get("ok"))
sheet
`);
console.log("has_svg", String(svg).includes("<svg"));
console.log("has_1V", String(svg).includes("1V"));
