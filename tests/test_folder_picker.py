import subprocess
import sys

from cloth_store.services.folder_picker import pick_folder


def test_mac_picker_returns_the_chosen_folder(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(sys, "platform", "darwin")
    seen: dict[str, str] = {}

    def fake_run(args, **_kwargs):
        seen["script"] = args[2]

        class Result:
            returncode = 0
            stdout = f"{tmp_path}/\n"

        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)
    start = tmp_path / 'say "hi"'
    start.mkdir()

    assert pick_folder(str(start)) == str(tmp_path)
    assert 'say \\"hi\\"' in seen["script"]
    assert "choose folder" in seen["script"]


def test_closing_the_picker_keeps_the_current_folder(monkeypatch) -> None:
    monkeypatch.setattr(sys, "platform", "darwin")

    def fake_run(*_args, **_kwargs):
        class Result:
            returncode = 1
            stdout = ""

        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert pick_folder("/tmp") is None
