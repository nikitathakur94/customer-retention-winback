MODE ?= dev
PY = .venv/bin/python
.PHONY: setup doctor download demo reproduce dashboard test-fast test-integration presentation
setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install uv
	UV_CACHE_DIR=.cache/uv .venv/bin/uv sync --frozen

doctor download presentation:
	$(PY) -m retention.cli $@ --mode $(MODE)
demo:
	$(PY) -m retention.cli reproduce --mode dev
reproduce:
	$(PY) -m retention.cli reproduce --mode $(MODE)
dashboard:
	$(PY) -m streamlit run app/Home.py --server.address 127.0.0.1 --server.port 8501

test-fast:
	$(PY) -m pytest tests/unit tests/ui -q
test-integration:
	RETENTION_MODE=$(MODE) $(PY) -m pytest tests/integration -q
