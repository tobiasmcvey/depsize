import subprocess
import json

def test_conda_list_json_schema():
    """
    Tests the conda list json schema

    Assumes you are running from a conda project
    """
    res = subprocess.run(["conda", "list", "--json"], capture_output=True, text=True)
    assert res.returncode == 0, f"Conda list failed: {res.stderr}"
    data = json.loads(res.stdout)
    assert isinstance(data, list)
    for pkg in data:
        assert "name" in pkg
        assert "version" in pkg
