# AI SRE Copilot

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/sre/main.py`](src/sre/main.py) | HTTP handlers: `POST /investigate` |
| [`src/sre/copilot.py`](src/sre/copilot.py) | Functions: `investigate` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/sre/__init__.py`](src/sre/__init__.py) | Implementation or supporting configuration |
| [`tests/test_sre.py`](tests/test_sre.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn sre.main:app --reload
```

<!-- project-guide:end -->

Level: 15 — AI, DevOps, SRE

Skills: Python, logs, GitOps drift, a hypothesis

An investigation calls list_alerts, read_logs, and check_manifest. OOMKilled with memory at or above 90 names a memory hypothesis. Drift names a GitOps hypothesis. `latest` is refused. `confirmed_root_cause` and `paged` stay false.

```bash
pip install -r requirements.txt
pytest -q
```

## Ops plane

Workspaces, tenant isolation, job approval, and audit live under `/v1`. Production apply is refused. See `docs/ARCHITECTURE.md`.
