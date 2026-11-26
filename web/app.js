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
    const r = await fetch("/api/draw", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ yaml: body }),
    });
    data = await r.json();
  } catch (err) {
    validateEl.textContent = "CLI backend offline. Start: python -m circuit.web_server";
    return;
  }
  last = data;
  showSheet();
}

document.getElementById("example").onclick = () => {
  yamlEl.value = EXAMPLE;
  chipsFrom(EXAMPLE);
};
document.getElementById("generate").onclick = generate;
document.getElementById("download").onclick = () => {
  if (!last) return;
  const svg = (last.sheets || {})[tab] || last.card;
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
yamlEl.value = EXAMPLE;
chipsFrom(EXAMPLE);
document.querySelector(".tabs button").classList.add("active");
