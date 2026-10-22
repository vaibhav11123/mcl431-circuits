"""Promote an ingest draft to a local proposal/ folder — never into locks."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml


def promote_bundle(ingest_dir: Path) -> tuple[int, str]:
    """Write ``proposal/`` under an ingest bundle. Returns (exit_code, message)."""
    ingest_dir = ingest_dir.resolve()
    if not ingest_dir.is_dir():
        return 1, f"ingest dir not found: {ingest_dir}"

    quarantine = ingest_dir / "quarantine.txt"
    if quarantine.is_file():
        return 4, f"refused: quarantined bundle ({quarantine})"

    draft_path = ingest_dir / "draft.yaml"
    manifest_path = ingest_dir / "manifest.yaml"
    if not draft_path.is_file():
        return 1, f"missing draft.yaml in {ingest_dir}"
    if not manifest_path.is_file():
        return 1, f"missing manifest.yaml in {ingest_dir}"

    draft: dict[str, Any] = yaml.safe_load(draft_path.read_text()) or {}
    manifest: dict[str, Any] = yaml.safe_load(manifest_path.read_text()) or {}

    diff_path = ingest_dir / "diff.txt"
    rules_path = ingest_dir / "rules.check.txt"
    incomplete = False
    if diff_path.is_file():
        diff_text = diff_path.read_text()
        if "ok=False" in diff_text or "missing" in diff_text.lower():
            # Locked row with misses → incomplete proposal, still written.
            if "status=locked" in diff_text and "ok=False" in diff_text:
                incomplete = True

    proposal = ingest_dir / "proposal"
    if proposal.exists():
        shutil.rmtree(proposal)
    proposal.mkdir(parents=True)

    excerpt = {
        "kind": draft.get("kind"),
        "source": draft.get("source"),
        "pages": draft.get("pages"),
        "index_matches": draft.get("index_matches") or [],
        "questions": [
            {
                "part": q.get("part"),
                "identifiers": q.get("identifiers"),
                "sequence_tokens": q.get("sequence_tokens"),
                "domain_guess": q.get("domain_guess"),
            }
            for q in (draft.get("questions") or [])
        ],
        "rules_check": draft.get("rules_check"),
    }
    (proposal / "draft.excerpt.yaml").write_text(
        yaml.safe_dump(excerpt, sort_keys=False)
    )

    lines = [
        "# Ingest promote proposal (PolyWiki-style)",
        "",
        "This folder is a REVIEW ARTIFACT only.",
        "Do NOT auto-copy into exams/transcribed/ or lecture/atlas.yaml.",
        "",
        f"ingest_dir: {ingest_dir}",
        f"source: {draft.get('source')}",
        f"kind: {draft.get('kind')}",
        f"manifest_sha256: {manifest.get('sha256') or manifest.get('source_sha256')}",
        f"status: {'incomplete' if incomplete else 'ready_for_human'}",
        "",
        "## Next human steps",
        "1. Compare document.md / draft.yaml to the page image or PDF.",
        "2. Copy identifiers, tables, quantities, and sequence tokens by hand.",
        "3. Never invent atlas ids from figure bboxes.",
        "",
    ]
    if diff_path.is_file():
        lines.append("## diff.txt (exam lock subset)")
        lines.append("```")
        lines.append(diff_path.read_text().rstrip())
        lines.append("```")
        lines.append("")
    if rules_path.is_file():
        lines.append("## rules.check.txt")
        lines.append("```")
        lines.append(rules_path.read_text().rstrip())
        lines.append("```")
        lines.append("")

    (proposal / "checklist.txt").write_text("\n".join(lines) + "\n")
    return 0, f"wrote {proposal}"


def main(root: Path, paths: list[Path]) -> int:
    import sys

    if not paths:
        print(
            "usage: python -m circuit promote <exams/ingest/stem|lecture/ingest/stem>",
            file=sys.stderr,
        )
        return 1
    code = 0
    for raw in paths:
        p = Path(raw)
        if not p.is_absolute():
            cand = (root / p).resolve()
            p = cand if cand.exists() else p.resolve()
        ec, msg = promote_bundle(p)
        print(msg)
        if ec != 0:
            code = ec
    return code
