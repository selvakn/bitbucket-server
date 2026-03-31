# Implementation Plan: API Integration Tests

**Branch**: `002-api-integration-tests` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-api-integration-tests/spec.md`

## Summary

Add a pytest-based integration test suite that exercises all 9 read-only commands in `scripts/bitbucket_api.py` against a live BitBucket Server instance. Tests use pre-existing server resources (no data creation). Credentials and test target identifiers are loaded from a `.env` file via `python-dotenv`. The project uses `uv` for dependency management with `pyproject.toml` as the single configuration source.

## Technical Context

**Language/Version**: Python 3.11+ (uv default; existing code is 3.6+ compatible)
**Primary Dependencies**: `requests` (existing), `pytest` (test runner), `python-dotenv` (env file loading)
**Storage**: N/A (stateless — all data comes from BitBucket Server API)
**Testing**: pytest with python-dotenv, run via `uv run pytest`
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: CLI tool / coding agent skill
**Performance Goals**: Full read-only test suite completes in under 2 minutes
**Constraints**: Tests are read-only; no server-side resource creation, modification, or deletion
**Scale/Scope**: 9 read-only commands, each with at least one integration test

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution file (`constitution.md`) contains only template placeholders with no ratified principles. No gates are defined; proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/002-api-integration-tests/
├── plan.md              # This file
├── research.md          # Phase 0: uv/pytest/dotenv research
├── data-model.md        # Phase 1: Test configuration model
├── quickstart.md        # Phase 1: Usage quick reference
├── contracts/           # Phase 1: Test structure contracts
│   └── test-structure.md
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
pyproject.toml               # NEW — uv project config, dependencies, pytest settings
.env.example                 # NEW — template for required env vars
.python-version              # NEW — created by uv init

tests/
├── conftest.py              # NEW — shared fixtures (env loading, client, test config)
├── test_discovery.py        # NEW — tests for list-projects, list-repos, get-repo, search-repos
└── test_pull_requests.py    # NEW — tests for list-prs, get-pr, get-diff, get-comments, get-tasks

scripts/
└── bitbucket_api.py         # EXISTING — code under test (no changes)

.gitignore                   # MODIFIED — add .env entry
```

**Structure Decision**: Tests live in a top-level `tests/` directory, separate from the `scripts/` source code. Two test modules organize tests by domain: discovery commands and PR read commands. Shared fixtures (client instantiation, env loading, test target config) live in `conftest.py`. The `pyproject.toml` at root configures uv, pytest, and all dependencies.

## Research Decisions

### R1: Dependency Management — uv with pyproject.toml

- **Decision**: Use `uv init` to bootstrap the project, then `uv add` for dependencies
- **Rationale**: User explicitly requested uv. It manages `pyproject.toml`, `uv.lock`, and virtual environments automatically. `uv run pytest` handles env activation transparently.
- **Dependencies**:
  - Runtime: `requests` (existing, now tracked in pyproject.toml)
  - Dev: `pytest`, `python-dotenv`

### R2: .env Loading — python-dotenv via conftest.py fixture

- **Decision**: Use a session-scoped autouse fixture in `conftest.py` that calls `load_dotenv()` before any test runs
- **Rationale**: Cleanest approach — no extra pytest plugins needed. `python-dotenv` is lightweight and widely used. The fixture runs once per session, loads all variables from `.env`, and makes them available via `os.environ` which `BitBucketClient.__init__` already reads.
- **Alternatives rejected**: `pytest-dotenv` plugin (adds unnecessary dependency for a single fixture), manual `os.environ` manipulation in each test (not DRY).

### R3: Test Architecture — Direct BitBucketClient method calls

- **Decision**: Tests instantiate `BitBucketClient` directly and call its methods, asserting on response structure
- **Rationale**: The tests should exercise the actual API integration path. The client methods are the public interface that the CLI dispatch layer calls. Testing at this level verifies HTTP communication, authentication, pagination, and response parsing — the core value of integration tests.
- **Alternatives rejected**: Subprocess-based CLI testing (adds process overhead, complicates assertion on structured data), mock-based unit tests (doesn't exercise the API, which is the explicit goal).

### R4: Test Configuration — Additional .env variables for test targets

- **Decision**: Require `TEST_PROJECT_KEY`, `TEST_REPO_SLUG`, and `TEST_PR_ID` in `.env` alongside credentials
- **Rationale**: Tests need to know which project/repo/PR to query. Making these configurable via `.env` allows any developer to point tests at their own BitBucket Server instance without code changes. The `conftest.py` fixture validates these are set and skips tests with a clear message if missing.

### R5: Test Structure — Two modules by domain

- **Decision**: `test_discovery.py` (4 tests for discovery commands) and `test_pull_requests.py` (5 tests for PR read commands)
- **Rationale**: Matches the spec's user story grouping (US-1 and US-2). Keeps each file focused. Allows running discovery tests independently of PR tests.

### R6: Response Structure Validation

- **Decision**: Assert presence of expected top-level fields and correct types, not exact values
- **Rationale**: Integration tests against a live server cannot predict exact data. Validating structure (e.g., "each project has `key` and `name` strings") provides confidence that the API contract is upheld without brittleness. Specific values (like checking the configured test project appears in results) are used sparingly as smoke checks.

## Complexity Tracking

No constitution violations. No complexity justification required.
