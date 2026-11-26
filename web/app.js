const EXAMPLE = `meta:
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

const yamlEl = document.getElementById("yaml");
const canvas = document.getElementById("sheet-canvas");
const chips = document.getElementById("chips");
const validateEl = document.getElementById("validate");
let last = null;
let tab = "pneumatic";
let history = [];
let pyodideReady = null;

async function loadCompiler() {
  if (pyodideReady) return pyodideReady;
  pyodideReady = (async () => {
    if (typeof loadPyodide !== "function") throw new Error("no pyodide");
    const pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install(["pydantic", "pyyaml"]);
    const buf = await fetch("./circuit-iso.zip").then((r) => r.arrayBuffer());
    pyodide.unpackArchive(buf, "zip");
    return pyodide;
  })();
  return pyodideReady;
}

async function drawInBrowser(text) {
  const pyodide = await loadCompiler();
  pyodide.FS.writeFile("/tmp/spec.yaml", text);
  const raw = await pyodide.runPythonAsync(`
import json
from pathlib import Path
from circuit.service import draw_yaml
from circuit.ir.from_spec import compile_report
from circuit.spec import CircuitSpec
text = Path("/tmp/spec.yaml").read_text()
out = draw_yaml(text)
out.pop("pack_files", None)
try:
    spec = CircuitSpec.from_yaml("/tmp/spec.yaml")
    out["graph_sha256"] = compile_report(spec)["graph_sha256"]
except Exception:
    pass
json.dumps(out)
`);
  return JSON.parse(raw);
}

function chipsFrom(text) {
  chips.innerHTML = "";
  const m = text.match(/action:\s*([^\s,}]+)/g) || [];
  m.forEach((raw) => {
    const span = document.createElement("span");
    span.className = "sequence-chip";
    span.textContent = raw.replace("action:", "").trim();
    chips.appendChild(span);
  });
}

function showSheet() {
  if (!last) return;
  const sheets = last.sheets || {};
  const map = {
    pneumatic: sheets.pneumatic || last.card,
    electrical: sheets.electrical,
    phase: sheets.phase,
    report: last.report,
    explain: last.explain,
    debug: last.debug,
  };
  const svg = map[tab] || last.card || "";
  canvas.innerHTML = svg;
  validateEl.textContent = last.sentence || "";
}

async function generate() {
  history.push(yamlEl.value);
  const body = yamlEl.value;
  let data;
  try {
    validateEl.textContent = "Compiling in browser…";
    data = await drawInBrowser(body);
  } catch (err) {
    try {
      const r = await fetch("/api/draw", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ yaml: body }),
      });
      data = await r.json();
    } catch (err2) {
      validateEl.textContent =
        "Pyodide compile failed and CLI backend is offline. Run: python -m circuit.web_server";
      return;
    }
  }
  last = data;
  showSheet();
}

document.getElementById("example").onclick = () => {
  yamlEl.value = EXAMPLE;
  chipsFrom(EXAMPLE);
};
document.getElementById("generate").onclick = generate;
document.getElementById("download").onclick = async () => {
  if (!last) return;
  const sheets = last.sheets || {};
  if (window.JSZip && Object.keys(sheets).length) {
    const zip = new JSZip();
    Object.entries(sheets).forEach(([name, body]) => {
      zip.file(name + (String(body).startsWith("<svg") ? ".svg" : ".txt"), body);
    });
    if (last.card) zip.file("card.svg", last.card);
    if (last.report) zip.file("report.svg", last.report);
    const blob = await zip.generateAsync({ type: "blob" });
    const a = document.createElement("a");
    a.download = "circuit-pack.zip";
    a.href = URL.createObjectURL(blob);
    a.click();
    return;
  }
  const svg = sheets[tab] || last.card;
  const a = document.createElement("a");
  a.download = tab + ".svg";
  a.href = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml" }));
  a.click();
};
document.getElementById("downloadYaml").onclick = () => {
  const a = document.createElement("a");
  a.download = "circuit.yaml";
  a.href = URL.createObjectURL(new Blob([yamlEl.value], { type: "text/yaml" }));
  a.click();
};
document.getElementById("save").onclick = () => {
  const key = "sequence-circuit-projects";
  const all = JSON.parse(localStorage.getItem(key) || "[]");
  all.push({ name: "project", yaml: yamlEl.value, savedAt: Date.now() });
  localStorage.setItem(key, JSON.stringify(all));
};
document.getElementById("undo").onclick = () => {
  if (!history.length) return;
  yamlEl.value = history.pop();
  generate();
};
document.querySelectorAll(".tabs button").forEach((b) => {
  b.onclick = () => {
    tab = b.dataset.tab;
    document.querySelectorAll(".tabs button").forEach((x) => x.classList.remove("active"));
    b.classList.add("active");
    showSheet();
  };
});
canvas.addEventListener("click", (event) => {
  const node = event.target.closest("[data-origin]");
  if (node) {
    validateEl.textContent = node.getAttribute("data-origin") || "";
  }
});
yamlEl.value = EXAMPLE;
chipsFrom(EXAMPLE);
document.querySelector(".tabs button").classList.add("active");
