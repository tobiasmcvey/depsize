import subprocess
import json

def test_poetry_show_json_schema():
    """
    Tests the poetry show json schema 

    Assumes you are running from a poetry project
    """
    res = subprocess.run(["poetry", "show", "--json"], capture_output=True, text=True)
    assert res.returncode == 0, f"Poetry show failed: {res.stderr}"
    data = json.loads(res.stdout)
    assert isinstance(data, list)
    for pkg in data:
        assert "name" in pkg
        assert "version" in pkg
