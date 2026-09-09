import pytest
from streamlit.testing.v1 import AppTest
from retention.common import ROOT

PAGES = [
    "Overview",
    "Customer health",
    "Risk model",
    "Customer explorer",
    "Win-back studio",
    "Campaign lab",
    "Data quality and learning",
]


@pytest.mark.parametrize("page", PAGES)
def test_pages(page):
    app = AppTest.from_file(str(ROOT / "app/Home.py")).run(timeout=40)
    app.sidebar.selectbox[0].set_value("dev")
    app.sidebar.radio[0].set_value(page)
    app.run(timeout=40)
    assert not app.exception


def test_empty_audience_and_missing_artifacts(monkeypatch, tmp_path):
    app = AppTest.from_file(str(ROOT / "app/Home.py")).run(timeout=40)
    app.sidebar.selectbox[0].set_value("dev")
    app.sidebar.radio[0].set_value("Win-back studio")
    app.run(timeout=40)
    app.number_input[0].set_value(0).run()
    assert not app.exception
    assert app.metric[0].value == "0"
    monkeypatch.setenv("RETENTION_ARTIFACTS_DIR", str(tmp_path))
    app = AppTest.from_file(str(ROOT / "app/Home.py")).run()
    assert not app.exception and len(app.info) > 0


def test_default_capacity_matches_published_full_audience():
    from retention.common import read, run_dir

    app = AppTest.from_file(str(ROOT / "app/Home.py")).run(timeout=40)
    app.sidebar.radio[0].set_value("Win-back studio").run(timeout=40)
    expected = read(run_dir("full") / "audience_summary.json")[-1]["selected"]
    assert int(app.metric[0].value) == expected
    app.multiselect[0].set_value([]).run()
    assert app.metric[0].value == "0"
    app.sidebar.radio[0].set_value("Customer explorer").run(timeout=40)
    assert app.sidebar.selectbox[1].disabled
    assert any("2020-01-28" in str(c.value) for c in app.caption)
    next(box for box in app.selectbox if box.label == "Anonymous observed buyer").set_value(1).run()
    app.checkbox[0].set_value(True).run()
    assert not app.exception
