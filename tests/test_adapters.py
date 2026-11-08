from __future__ import annotations

from pathlib import Path
import sys

import pytest

from yini_test.adapters import run_adapter
from yini_test.models import AdapterResult


@pytest.mark.parametrize(
    ("stdout", "error"),
    [
        pytest.param(" \n\t", "no JSON output", id="empty-output"),
        pytest.param('{"name":', "not valid JSON", id="malformed-json"),
        pytest.param(
            'Starting parser\n{"name": "Demo"}', "not valid JSON", id="logging"
        ),
        pytest.param("{}\n{}", "not valid JSON", id="multiple-documents"),
    ],
)
def test_run_adapter_rejects_invalid_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    stdout: str,
    error: str,
) -> None:
    # Arrange.
    input_path = tmp_path / "case.yini"
    monkeypatch.setattr(
        "yini_test.adapters.run_adapter_raw",
        lambda adapter_tokens, input_path, mode: AdapterResult(
            stdout=stdout, stderr="", returncode=0
        ),
    )

    # Act and assert.
    with pytest.raises(RuntimeError, match=error) as exc_info:
        run_adapter([sys.executable], input_path, mode="lenient")

    assert input_path.name in str(exc_info.value)


def test_run_adapter_rejects_nonzero_exit_even_with_valid_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Arrange.
    input_path = tmp_path / "case.yini"
    monkeypatch.setattr(
        "yini_test.adapters.run_adapter_raw",
        lambda adapter_tokens, input_path, mode: AdapterResult(
            stdout='{"name": "Demo"}',
            stderr="Parser failed.",
            returncode=2,
        ),
    )

    # Act and assert.
    with pytest.raises(RuntimeError, match="Adapter failed for valid case") as exc_info:
        run_adapter([sys.executable, "--input", "{input}"], input_path, mode="strict")

    message = str(exc_info.value)
    assert input_path.name in message
    assert f"Command: {sys.executable} --input {input_path}" in message
    assert "Details: Parser failed." in message
