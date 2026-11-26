"""The test job runs on ubuntu-latest with only what ci.yml installs.

A test that launches a host binary (rg, git, qlmanage) fails there with
FileNotFoundError. This contract fails in-process first: the only implicit
executable is the Python interpreter. Any other string-literal executable
must be named in .github/workflows/ci.yml.
"""

from __future__ import annotations

import ast
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"

# binary -> token that must appear in ci.yml (package or binary name)
ALLOWED_HOST_BINS: dict[str, str] = {}

_PROCESS_ATTRS = {
    "run",
    "call",
    "check_call",
    "check_output",
    "Popen",
    "getoutput",
    "getstatusoutput",
    "system",
    "popen",
}


def _is_process_call(node: ast.Call) -> bool:
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr in _PROCESS_ATTRS
    if isinstance(func, ast.Name):
        return func.id in {"system", "popen"}
    return False


def _literal_executable(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        token = node.value.split()[0]
        return token or None
    if isinstance(node, (ast.List, ast.Tuple)) and node.elts:
        first = node.elts[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    return None


def _host_bins(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[tuple[int, str]] = []

    class Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:
            if _is_process_call(node) and node.args:
                exe = _literal_executable(node.args[0])
                if exe:
                    found.append((node.lineno, exe))
            self.generic_visit(node)

    Visitor().visit(tree)
    return found


def test_tests_only_launch_declared_host_bins() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    offenders: list[str] = []
    for path in sorted(TESTS.glob("test_*.py")):
        for lineno, exe in _host_bins(path):
            token = ALLOWED_HOST_BINS.get(exe)
            if token is None:
                offenders.append(
                    f"{path.name}:{lineno} launches {exe!r}. "
                    "Call sys.executable, or add the binary to ALLOWED_HOST_BINS and ci.yml."
                )
                continue
            if token not in workflow:
                offenders.append(
                    f"{path.name}:{lineno} launches {exe!r} but ci.yml does not mention {token!r}."
                )
    assert offenders == []


def test_actions_runner_installs_svg_backend() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "librsvg2-bin" in workflow
    if os.environ.get("GITHUB_ACTIONS") == "true":
        assert shutil.which("rsvg-convert"), "Install librsvg2-bin before pytest"
