# Tasks: API Integration Tests

**Input**: Design documents from `/specs/002-api-integration-tests/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/test-structure.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize uv project, declare dependencies, configure credentials template and gitignore

- [x] T001 Initialize uv project — run `uv init` in project root, then edit pyproject.toml to set project name to `bitbucket-server`, description to `BitBucket Server REST API CLI Tool`, and add `[tool.pytest.ini_options]` with `testpaths = ["tests"]`
- [x] T002 Add dependencies — run `uv add requests` (runtime) and `uv add --dev pytest python-dotenv` (dev); verify uv.lock is generated
- [x] T003 [P] Create .env.example at project root with all 6 required variables: `BITBUCKET_URL`, `BITBUCKET_USER`, `BITBUCKET_TOKEN`, `TEST_PROJECT_KEY`, `TEST_REPO_SLUG`, `TEST_PR_ID` — each with a placeholder comment
- [x] T004 [P] Add `.env` entry to .gitignore (file already exists, append to it)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create shared test fixtures that ALL test modules depend on

**⚠️ CRITICAL**: No test implementation can begin until this phase is complete

- [x] T005 Create tests/conftest.py with three session-scoped fixtures: (1) `load_env` — autouse fixture that calls `load_dotenv()` from python-dotenv, (2) `client` — returns a `BitBucketClient` instance (import from `scripts.bitbucket_api`), (3) `test_config` — reads `TEST_PROJECT_KEY`, `TEST_REPO_SLUG`, `TEST_PR_ID` from `os.environ`, calls `pytest.skip()` if any are missing, returns dict with `project_key` (str), `repo_slug` (str), `pr_id` (int). Add `sys.path` insertion for `scripts/` directory so the import works.

**Checkpoint**: Foundation ready — `uv run pytest --collect-only` should discover the conftest without errors

---

## Phase 3: User Story 1 — Discovery Command Tests (Priority: P1) 🎯 MVP

**Goal**: Verify all 4 discovery commands return correctly structured responses from the live API

**Independent Test**: `uv run pytest tests/test_discovery.py -v` — all 4 tests pass against a configured BitBucket Server

### Implementation for User Story 1

- [x] T006 [US1] Implement 4 discovery tests in tests/test_discovery.py per contracts/test-structure.md: (1) `test_list_projects(client)` — asserts non-empty list, each item has `key` (str) and `name` (str); (2) `test_list_repositories(client, test_config)` — calls `list_repositories(project_key)`, asserts list, each item has `slug`, `name`, nested `project["key"]`; (3) `test_get_repository(client, test_config)` — calls `get_repository(project_key, repo_slug)`, asserts dict with `slug` matching config, `name`, `links`, `defaultBranch` key exists; (4) `test_search_repositories(client, test_config)` — calls `search_repositories(repo_slug)`, asserts list with at least one result whose `slug` matches config

**Checkpoint**: `uv run pytest tests/test_discovery.py -v` — 4 tests pass. US1 is independently functional.

---

## Phase 4: User Story 2 — PR Read Tests (Priority: P2)

**Goal**: Verify all 5 PR read commands return correctly structured responses from the live API

**Independent Test**: `uv run pytest tests/test_pull_requests.py -v` — all 5 tests pass against a configured BitBucket Server with an existing PR

### Implementation for User Story 2

- [x] T007 [US2] Implement 5 PR read tests in tests/test_pull_requests.py per contracts/test-structure.md: (1) `test_list_pull_requests(client, test_config)` — calls `list_pull_requests(project_key, repo_slug, state="ALL")`, asserts list, each item has `id` (int), `title` (str), `state` (str); (2) `test_get_pull_request(client, test_config)` — calls `get_pull_request(project_key, repo_slug, pr_id)`, asserts dict with `id` equal to `pr_id`, `title`, `state`, `author`, `fromRef`, `toRef`; (3) `test_get_diff(client, test_config)` — calls `get_diff(project_key, repo_slug, pr_id)`, asserts dict with `diffs` key containing a list; (4) `test_get_comments(client, test_config)` — calls `get_comments(project_key, repo_slug, pr_id)`, asserts list, if non-empty each has `id` (int), `text` (str), `author` (str); (5) `test_get_tasks(client, test_config)` — calls `get_tasks(project_key, repo_slug, pr_id)`, asserts list, if non-empty each has `id` (int), `text` (str), `state` (str)

**Checkpoint**: `uv run pytest -v` — all 9 tests pass. Both US1 and US2 are independently functional.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates to reflect new test infrastructure

- [x] T008 Update README.md — add a `### Running Tests` section under the existing structure with: prerequisites (uv installed, .env configured), setup steps (`cp .env.example .env`, `uv sync`), run command (`uv run pytest`), and a note about required server state (project, repo, and PR must exist)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001, T002 must complete; T003, T004 are independent but should be done) — BLOCKS all test implementation
- **US1 (Phase 3)**: Depends on Foundational (T005) — can start once conftest.py exists
- **US2 (Phase 4)**: Depends on Foundational (T005) — can start in parallel with US1 (different file)
- **Polish (Phase 5)**: Depends on US1 and US2 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 — no dependency on US2
- **User Story 2 (P2)**: Can start after Phase 2 — no dependency on US1

### Within Each User Story

- Single task per story (one test file each) — no intra-story sequencing needed

### Parallel Opportunities

- T003 and T004 can run in parallel (different files, no dependencies)
- T006 (US1) and T007 (US2) can run in parallel after T005 completes (different test files, shared fixtures only)

---

## Parallel Example: User Stories 1 & 2

```text
# After Phase 2 completes, both stories can proceed in parallel:
Task T006: Implement 4 discovery tests in tests/test_discovery.py
Task T007: Implement 5 PR read tests in tests/test_pull_requests.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005)
3. Complete Phase 3: User Story 1 (T006)
4. **STOP and VALIDATE**: `uv run pytest tests/test_discovery.py -v`
5. 4 discovery tests passing = MVP delivered

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (T006) → `uv run pytest tests/test_discovery.py` → 4/9 commands covered (MVP!)
3. Add US2 (T007) → `uv run pytest` → 9/9 commands covered (feature complete)
4. Add Polish (T008) → README updated → ready for other developers

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All tests are read-only — no server mutations
- Tests call `BitBucketClient` methods directly, not CLI subprocess
- Response validation checks structure (field presence, types), not exact values
- Commit after each phase or logical group
