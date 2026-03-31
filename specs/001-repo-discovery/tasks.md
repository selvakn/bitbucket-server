# Tasks: Repository and Project Discovery

**Input**: Design documents from `/specs/001-repo-discovery/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Update API reference documentation with the new endpoints before implementation begins.

- [x] T001 Add project and repository endpoint documentation (list projects, list repos, get repo, get default branch, search repos) to references/api_endpoints.md

---

## Phase 2: User Story 1 - List All Projects (Priority: P1) 🎯 MVP

**Goal**: Enable users to list all accessible projects on a BitBucket Server instance in a single command.

**Independent Test**: Run `python3 scripts/bitbucket_api.py list-projects` and verify it returns a JSON array of projects with key, name, and description fields. Pagination should be handled transparently.

### Implementation for User Story 1

- [x] T002 [US1] Add `list_projects` method to `BitBucketClient` class in scripts/bitbucket_api.py — calls `GET /projects` via `_get_paginated`, returns all accessible projects
- [x] T003 [US1] Add `list-projects` argparse subparser (no required arguments) and dispatch branch in scripts/bitbucket_api.py — outputs result via `output_json`

**Checkpoint**: `python3 scripts/bitbucket_api.py list-projects` should return a JSON array of all accessible projects.

---

## Phase 3: User Story 2 - List Repositories Within a Project (Priority: P1)

**Goal**: Enable users to list all repositories within a specified project.

**Independent Test**: Run `python3 scripts/bitbucket_api.py list-repos --project PROJ` and verify it returns a JSON array of repositories with slug, name, description, and clone URLs. Verify error handling for invalid project keys.

### Implementation for User Story 2

- [x] T004 [US2] Add `list_repositories` method to `BitBucketClient` class in scripts/bitbucket_api.py — takes `project` param, calls `GET /projects/{projectKey}/repos` via `_get_paginated`
- [x] T005 [US2] Add `list-repos` argparse subparser (requires `--project`/`-p`) and dispatch branch in scripts/bitbucket_api.py — outputs result via `output_json`

**Checkpoint**: `python3 scripts/bitbucket_api.py list-repos --project PROJ` should return a JSON array of all repositories in the specified project.

---

## Phase 4: User Story 3 - Get Repository Details (Priority: P2)

**Goal**: Enable users to view detailed information about a specific repository including its default branch and clone URLs.

**Independent Test**: Run `python3 scripts/bitbucket_api.py get-repo --project PROJ --repo my-repo` and verify it returns a single JSON object with full repository metadata plus `defaultBranch` field. Verify graceful handling when default branch endpoint fails (empty repo).

### Implementation for User Story 3

- [x] T006 [US3] Add `get_repository` method to `BitBucketClient` class in scripts/bitbucket_api.py — calls `GET /projects/{projectKey}/repos/{repositorySlug}` for repo metadata, then `GET .../default-branch` for default branch info; merges results into a single dict with `defaultBranch` key; catches errors on default-branch call and sets `defaultBranch` to `null` if it fails
- [x] T007 [US3] Add `get-repo` argparse subparser (requires `--project`/`-p` and `--repo`/`-r`) and dispatch branch in scripts/bitbucket_api.py — outputs result via `output_json`

**Checkpoint**: `python3 scripts/bitbucket_api.py get-repo --project PROJ --repo my-repo` should return a single JSON object with repository details and default branch.

---

## Phase 5: User Story 4 - Search Repositories Across Projects (Priority: P3)

**Goal**: Enable users to find repositories by name across all accessible projects without needing to know which project a repo belongs to.

**Independent Test**: Run `python3 scripts/bitbucket_api.py search-repos --name payment` and verify it returns a JSON array of matching repositories with project context. Verify empty search returns `[]`. Verify results span multiple projects.

### Implementation for User Story 4

- [x] T008 [US4] Add `search_repositories` method to `BitBucketClient` class in scripts/bitbucket_api.py — takes `name` param, calls `GET /repos` with `name` query parameter via `_get_paginated`
- [x] T009 [US4] Add `search-repos` argparse subparser (requires `--name`/`-n`) and dispatch branch in scripts/bitbucket_api.py — outputs result via `output_json`

**Checkpoint**: `python3 scripts/bitbucket_api.py search-repos --name payment` should return a JSON array of matching repositories across all projects.

---

## Phase 6: Polish & Documentation

**Purpose**: Update skill documentation so the coding agent and users know about the new discovery commands.

- [x] T010 [P] Update SKILL.md with a new "Discovery Commands" section documenting `list-projects`, `list-repos`, `get-repo`, and `search-repos` commands with usage examples and argument tables
- [x] T011 [P] Update README.md with discovery command examples in the "Available Commands" and usage sections

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **User Stories (Phases 2–5)**: All depend on Phase 1 (reference docs)
  - All four stories can proceed sequentially in priority order (recommended)
  - US1 and US2 could proceed in parallel since they modify different sections of the same file
- **Polish (Phase 6)**: Depends on all user story phases being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories — standalone `list_projects` + `list-projects`
- **User Story 2 (P1)**: No dependencies on other stories — standalone `list_repositories` + `list-repos`
- **User Story 3 (P2)**: No dependencies on other stories — standalone `get_repository` + `get-repo`
- **User Story 4 (P3)**: No dependencies on other stories — standalone `search_repositories` + `search-repos`

### Within Each User Story

- Client method (T00x) before argparse/dispatch (T00x+1)
- Each story adds ~25 lines to `scripts/bitbucket_api.py`

### Parallel Opportunities

- T010 and T011 (documentation) can run in parallel with each other
- Within each user story, the method and subparser tasks are sequential (same file, subparser depends on method existing)
- Across user stories, parallelism is possible since each adds independent code blocks, but since all modify the same file, sequential execution is recommended to avoid merge conflicts

---

## Parallel Example: Phase 6

```bash
# Documentation updates can run in parallel (different files):
Task T010: "Update SKILL.md with discovery command documentation"
Task T011: "Update README.md with discovery command examples"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: User Story 1 — List Projects (T002, T003)
3. **STOP and VALIDATE**: Run `list-projects` and verify output
4. Already delivering value — users can see the project landscape

### Incremental Delivery

1. Setup → reference docs ready
2. Add User Story 1 (list-projects) → Test → **MVP!**
3. Add User Story 2 (list-repos) → Test → projects + repos discoverable
4. Add User Story 3 (get-repo) → Test → full repo details with default branch
5. Add User Story 4 (search-repos) → Test → cross-project search
6. Polish → documentation complete
7. Each story adds value without breaking previous stories

---

## Notes

- All four commands reuse existing `_get_paginated`, `_request`, `output_json`, and auth infrastructure — no new dependencies
- No test tasks included (no test framework in the current repo; testing is manual)
- All code changes are in a single file (`scripts/bitbucket_api.py`) — sequential execution within each story recommended
- The `get-repo` command (US3) is the most complex due to the two-call pattern (repo metadata + default branch) with error handling
- Commit after each completed user story for clean incremental delivery
