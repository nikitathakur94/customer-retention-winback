# Working handoff (finalization in progress)

Project root: retention_winback_codex_kit/project. Current local full run: artifacts/full-v1.

Verified core commands: make doctor; .venv/bin/python -m retention.cli reports --mode full; RETENTION_MODE=full .venv/bin/python -m pytest tests/integration -q; .venv/bin/python -m streamlit run app/Home.py --server.address 127.0.0.1 --server.port 8501 --server.headless true.

The app is local at http://127.0.0.1:8501. Open Overview, then Risk model, Customer explorer and Win-back studio. Read docs/learning/START_HERE.md, local reports/sql_workbook.md, and local traces/worked_customer.md.

Core full-data stages have executed; deck/PDF and notebook execution are still being finalized. STATUS.md records completion honestly. Raw and derived customer records are ignored by Git. No outreach has occurred.
