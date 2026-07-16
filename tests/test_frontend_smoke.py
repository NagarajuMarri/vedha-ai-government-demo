"""Static frontend skeleton smoke tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"


def test_landing_page_contains_required_interface_navigation() -> None:
    content = (FRONTEND_ROOT / "index.html").read_text(encoding="utf-8")

    assert "Vedha AI Government Demo" in content
    assert 'href="student/"' in content
    assert 'href="teacher/"' in content
    assert 'href="parent/"' in content
    assert 'href="government/"' in content
    assert 'href="assets/css/styles.css"' in content
    assert 'src="assets/js/main.js"' in content


def test_interface_shells_exist() -> None:
    for interface in ("student", "teacher", "parent", "government"):
        assert (FRONTEND_ROOT / interface / "index.html").is_file()
