import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_demo_notebooks_are_valid_and_synchronised():
    paths = [
        ROOT / "demo_rest_api.ipynb",
        ROOT / "notebooks" / "demo_rest_api.ipynb",
    ]
    contents = [path.read_text(encoding="utf-8") for path in paths]
    assert contents[0] == contents[1]

    notebook = json.loads(contents[0])
    assert notebook["nbformat"] == 4

    code = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )
    assert "LOGINOM_CHECK_URL" in code
    assert "CheckUserId" in code
    assert "GetUserHistory" in code
    assert "GIGA_KEY" in code
