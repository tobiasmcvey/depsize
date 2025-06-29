# %%
import shutil
import subprocess

from depsize.depsize import get_pip_packages
# %%
class FakeResult:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.returncode = returncode


def test_uv_installed(monkeypatch):
    """
    Should run 'uv pip list' when uv is found
    """

    def fake_which(cmd):
        return "/usr/local/bin/uv" if cmd == "uv" else None

    def fake_run(cmd, capture_output=True, text=True):
        assert cmd[0] == "uv"
        class FakeResult:
            stdout = '[{"name": "foo", "version": "1.0.0"}]'
        return FakeResult()

    monkeypatch.setattr(shutil, "which", fake_which)
    monkeypatch.setattr(subprocess, "run", fake_run)

    pkgs = get_pip_packages()
    assert isinstance(pkgs, list)
    assert pkgs[0]["name"] == "foo"

def test_pip_installed_if_uv_not_found(monkeypatch):
    """
    Should fallback to 'pip list' if uv is not found
    """

    def fake_which(cmd):
        if cmd == "uv":
            return None
        if cmd == "pip":
            return "/usr/local/bin/pip"
        return None
    
    def fake_run(cmd, capture_output=True, text=True):
        assert cmd[0] == "pip"
        class FakeResult:
            stdout = '[{"name":"bar", "version": "2.0.0."}]'
        return FakeResult()
    
    monkeypatch.setattr(shutil, "which", fake_which)
    monkeypatch.setattr(subprocess, "run", fake_run)

    pkgs = get_pip_packages()
    assert isinstance(pkgs, list)
    assert pkgs[0]["name"] == "bar"

def test_poetry_fallback_message(monkeypatch, capsys):
    """
    Should print an error message if poetry is found but not pip or uv
    """

    def fake_which(cmd):
        if cmd in ["uv", "pip"]:
            return None
        if cmd == "poetry":
            return "/usr/local/bin/poetry"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)

    pkgs = get_pip_packages()
    captured = capsys.readouterr()
    assert "Poetry detected" in captured.out
    assert pkgs == []

def test_conda_fallback_message(monkeypatch, capsys):
    """
    Should print an error message if conda is found but not pip or uv
    """

    def fake_which(cmd):
        if cmd in ["uv", "pip"]:
            return None
        if cmd == "conda":
            return "/usr/local/bin/conda"
        return None

    monkeypatch.setattr(shutil, "which", fake_which)

    pkgs = get_pip_packages()
    captured = capsys.readouterr()
    assert "Conda detected" in captured.out
    assert pkgs == []

def test_nothing_found(monkeypatch, capsys):
    """
    Should print an error if no tool is found
    """

    def fake_which(cmd):
        return None

    monkeypatch.setattr(shutil, "which", fake_which)

    pkgs = get_pip_packages()
    captured = capsys.readouterr()
    assert "No supported package manager found" in captured.out
    assert pkgs == []

def test_invalid_json(monkeypatch, capsys):
    """
    Should handle invalid JSON from subprocess
    """

    def fake_which(cmd):
        if cmd == "uv":
            return "/usr/local/bin/uv"
        return None
    
    def fake_run(cmd, capture_output=True, text=True):
        class FakeResult:
            stdout = "Not JSON"
        return FakeResult()
    
    monkeypatch.setattr(shutil, "which", fake_which)
    monkeypatch.setattr(subprocess, "run", fake_run)

    pkgs = get_pip_packages()
    captured = capsys.readouterr()
    assert "Error parsing JSON output" in captured.out
    assert pkgs == []
