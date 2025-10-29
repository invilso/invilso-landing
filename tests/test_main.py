from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


def _load_main_module():
    module_path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib.util.spec_from_file_location("main", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load main module for testing.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_invokes_uvicorn(monkeypatch):
    captured: dict[str, object] = {}

    stub = types.SimpleNamespace()

    def fake_run(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs

    stub.run = fake_run
    monkeypatch.setitem(sys.modules, "uvicorn", stub)

    main = _load_main_module()
    main.run()

    assert captured["args"] == ("main:app",)
    assert captured["kwargs"] == {"host": "0.0.0.0", "port": 8000, "reload": True}
