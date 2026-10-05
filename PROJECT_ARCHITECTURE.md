# ai-sre-copilot — project architecture

[README](README.md) · [Interview questions and answers](INTERVIEW_QA.md)

## Purpose and scope

An investigation calls list_alerts, read_logs, and check_manifest. OOMKilled with memory at or above 90 names a memory hypothesis. Drift names a GitOps hypothesis. `latest` is refused. `confirmed_root_cause` and `paged` stay false.

This document describes files and symbols in this checkout. Deployment templates and statements in the original overview are distinguished from a verified running environment.

## Component diagram

```mermaid
flowchart LR
    M0["src/sre/__init__.py"]
    M1["src/sre/copilot.py"]
    M2["src/sre/main.py"]
    M3["src/sre/ops.py"]
    M2 -->|imports| M1
    M2 -->|imports| M3
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/sre/main.py`](src/sre/main.py) | HTTP handlers: `POST /investigate` |
| [`src/sre/ops.py`](src/sre/ops.py) | HTTP handlers: `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}` |
| [`src/sre/copilot.py`](src/sre/copilot.py) | Functions: `investigate` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/sre/__init__.py`](src/sre/__init__.py) | Implementation or supporting configuration |
| [`Dockerfile`](Dockerfile) | Container build/service configuration |
| [`Makefile`](Makefile) | Implementation or supporting configuration |
| [`docker-compose.yml`](docker-compose.yml) | Container build/service configuration |
| [`tests/test_ops.py`](tests/test_ops.py) | Executable checks and regression examples |
| [`tests/test_sre.py`](tests/test_sre.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Project explanations or operating notes |

## Existing design and operating guides

These checked-in guides provide the project’s detailed design, operational context, or deployment view:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `POST /investigate` | `post_investigate` | [`src/sre/main.py`](src/sre/main.py#L9) |
| `GET /readyz` | `readyz` | [`src/sre/ops.py`](src/sre/ops.py#L44) |
| `POST /workspaces` | `create_workspace` | [`src/sre/ops.py`](src/sre/ops.py#L49) |
| `GET /workspaces` | `list_workspaces` | [`src/sre/ops.py`](src/sre/ops.py#L66) |
| `POST /workspaces/{workspace_id}/jobs` | `create_job` | [`src/sre/ops.py`](src/sre/ops.py#L73) |
| `GET /jobs/{job_id}` | `get_job` | [`src/sre/ops.py`](src/sre/ops.py#L96) |
| `POST /jobs/{job_id}/approve` | `approve_job` | [`src/sre/ops.py`](src/sre/ops.py#L105) |
| `GET /audit` | `audit` | [`src/sre/ops.py`](src/sre/ops.py#L122) |
| `GET /metrics` | `metrics` | [`src/sre/ops.py`](src/sre/ops.py#L138) |

The table lists literal route decorators found in the inspected Python modules. Router prefixes and middleware can add behavior; check the linked handler and application setup before calling an endpoint.

## Implementation walkthrough

### `investigate(snapshot)`

Source: [`src/sre/copilot.py`](src/sre/copilot.py#L3).

Calls visible in this function: `snapshot.get`, `str`, `str(snapshot.get('image', '')).endswith`.

```python
def investigate(snapshot):
    if str(snapshot.get("image", "")).endswith(":latest"):
        return {"refused": True, "reason": "latest is refused.", "hypothesis": None, "tools": TOOLS, "confirmed_root_cause": False, "paged": False}
    hypothesis = None
    if snapshot.get("reason") == "OOMKilled" and snapshot.get("memory_percent", 0) >= 90:
        hypothesis = "memory-limit"
    elif snapshot.get("drifted"):
        hypothesis = "gitops-drift"
    return {"refused": False, "hypothesis": hypothesis, "tools": TOOLS, "confirmed_root_cause": False, "paged": False}
```

## Validation and failure paths

| Explicit exception | Source |
| --- | --- |
| `HTTPException(status_code=404, detail='workspace not found')` | [`src/sre/ops.py`](src/sre/ops.py#L77) |
| `HTTPException(status_code=404, detail='job not found')` | [`src/sre/ops.py`](src/sre/ops.py#L100) |
| `HTTPException(status_code=404, detail='job not found')` | [`src/sre/ops.py`](src/sre/ops.py#L109) |
| `HTTPException(status_code=403, detail='production apply is disabled in this lab')` | [`src/sre/ops.py`](src/sre/ops.py#L113) |

These are explicit exceptions in the inspected source, rather than a claim that every failure is handled. Follow the calling handler to see whether the exception becomes an HTTP response or propagates.

## Data and state

- [`src/sre/copilot.py`](src/sre/copilot.py) defines module-level containers: `TOOLS`.
- [`src/sre/ops.py`](src/sre/ops.py) defines module-level containers: `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`.

Module-level dictionaries/lists live in a Python process. They can be fixtures or mutable state; inspect writes before treating them as persistent storage. A production extension would need to define persistence and concurrency behavior explicitly.

## Data flow and design decisions

### What is the input-to-output contract of `investigate`

In [`src/sre/copilot.py`](src/sre/copilot.py#L3), `investigate(snapshot)` receives the inputs. The function computes these intermediate values:

- `hypothesis = None`

Its result is defined by:

- `{'refused': False, 'hypothesis': hypothesis, 'tools': TOOLS, 'confirmed_root_cause': False, 'paged': False}`
- `{'refused': True, 'reason': 'latest is refused.', 'hypothesis': None, 'tools': TOOLS, 'confirmed_root_cause': False, 'paged': False}`

### Which decision rules or boundary conditions should an interviewer challenge

The implementation in [`src/sre/copilot.py`](src/sre/copilot.py#L3) branches on:

- `str(snapshot.get('image', '')).endswith(':latest')`
- `snapshot.get('reason') == 'OOMKilled' and snapshot.get('memory_percent', 0) >= 90`
- `snapshot.get('drifted')`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

### What does the operations plane add, and where is its limit

[`src/sre/ops.py`](src/sre/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_ops.py`](tests/test_ops.py), [`tests/test_sre.py`](tests/test_sre.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.
