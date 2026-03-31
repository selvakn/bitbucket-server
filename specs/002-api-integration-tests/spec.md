# Feature Specification: API Integration Tests

**Feature Branch**: `002-api-integration-tests`  
**Created**: 2026-03-31  
**Status**: Draft  
**Input**: User description: "implement tests (which exercise the APIs) for the code in bitbucket_api. the bitbucket credentials for running the test can be taken from .env file. Use uv based setup for managing dependencies, etc"

## Clarifications

### Session 2026-03-31

- Q: Should tests assume pre-existing resources or create their own test data? → A: Pre-existing fixtures only. Tests MUST NOT create any resources on the server. Only read-only functionalities are in scope.

## Scope Boundaries

**In scope:**
- Integration tests for all read-only commands (discovery + PR read operations)
- Project setup with uv-based dependency management
- Credential loading from `.env` file
- Test target configuration via `.env` variables (`TEST_PROJECT_KEY`, `TEST_REPO_SLUG`, etc.)

**Out of scope:**
- Write operation tests (`create-pr`, `add-comment`, `reply-comment`, `approve`, `merge`, `decline`)
- Task management command tests (`complete-task`, `complete-tasks`, `reopen-task`, `reopen-tasks`)
- Test data bootstrapping or cleanup (no resource creation on the server)
- CI/CD pipeline integration
- Performance/load testing

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Discovery Command Tests (Priority: P1)

As a developer contributing to this skill, I want to run integration tests that verify the project and repository discovery commands work correctly against a live BitBucket Server instance, so I can confidently make changes without breaking existing functionality.

**Why this priority**: Discovery commands (`list-projects`, `list-repos`, `get-repo`, `search-repos`) are the newest and most likely to change. They are also read-only operations, making them the safest starting point for integration tests with no risk of mutating server state.

**Independent Test**: Can be fully tested by running the discovery test suite against a BitBucket Server instance with at least one project and repository. Delivers confidence that all four discovery commands return correctly structured data.

**Acceptance Scenarios**:

1. **Given** valid BitBucket credentials in the environment, **When** the developer runs the discovery test suite, **Then** all tests pass and verify that listing projects returns a non-empty list with expected fields (key, name).
2. **Given** a known project key, **When** the list-repos test runs, **Then** it returns a list of repositories with expected fields (slug, name, project context).
3. **Given** a known project key and repository slug, **When** the get-repo test runs, **Then** it returns a single repository object with default branch information and clone URLs.
4. **Given** a search term that matches at least one repository, **When** the search-repos test runs, **Then** it returns matching repositories with project context included.

---

### User Story 2 - Run Pull Request Read Tests (Priority: P2)

As a developer, I want integration tests that verify the pull request read operations (listing and getting PR details, diffs, comments, and tasks) work correctly, so I can trust the code review workflow commands.

**Why this priority**: PR read operations are the most frequently used commands and are also read-only (safe to run). They validate the core value proposition of the skill.

**Independent Test**: Can be tested by running the PR read test suite against a BitBucket instance that has at least one open pull request with comments. Verifies listing PRs, getting PR details, retrieving diffs, and reading comments/tasks.

**Acceptance Scenarios**:

1. **Given** a repository with at least one pull request, **When** the list-prs test runs, **Then** it returns a list containing the known PR with expected fields (id, title, state, author).
2. **Given** a known PR ID, **When** the get-pr test runs, **Then** it returns the PR details matching the expected structure.
3. **Given** a known PR ID, **When** the get-diff test runs, **Then** it returns diff data without errors.
4. **Given** a PR with at least one comment, **When** the get-comments test runs, **Then** it returns comments with expected fields (id, text, author).

---

### User Story 3 - Project Setup and Credential Management (Priority: P1)

As a developer setting up the project for the first time, I want the test infrastructure to use a standard dependency manager and load credentials from a `.env` file, so I can get started quickly and keep secrets out of version control.

**Why this priority**: Without proper project setup and credential management, no tests can run. This is a prerequisite for all other stories.

**Independent Test**: Can be tested by installing dependencies and verifying the test runner starts without errors. Credentials loading can be verified by checking that environment variables are populated from the `.env` file.

**Acceptance Scenarios**:

1. **Given** a fresh checkout of the repository, **When** the developer installs dependencies using the project's dependency manager, **Then** all test dependencies are installed and the test runner is available.
2. **Given** a `.env` file with `BITBUCKET_URL`, `BITBUCKET_USER`, and `BITBUCKET_TOKEN`, **When** the test suite starts, **Then** it loads the credentials from the file and uses them for API authentication.
3. **Given** no `.env` file exists, **When** the developer tries to run tests, **Then** the system provides a clear error message indicating which credentials are missing.
4. **Given** a `.env.example` template exists, **When** a new developer clones the repo, **Then** they can copy it to `.env` and fill in their credentials to get started.

---

### Edge Cases

- What happens when the BitBucket Server is unreachable during test runs? Tests should fail with clear connection error messages, not hang indefinitely.
- What happens when credentials in `.env` are invalid or expired? Tests should fail fast with an authentication error, not produce confusing downstream failures.
- What happens when expected test fixtures (projects, repos, PRs) don't exist on the target server? Tests should skip gracefully or provide clear instructions on required server state.
- What happens when required test fixture identifiers (project key, repo slug) are not configured in `.env`? Tests should fail with a clear message listing the missing configuration variables.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The test suite MUST verify all discovery commands (`list-projects`, `list-repos`, `get-repo`, `search-repos`) return correctly structured responses from a live BitBucket Server.
- **FR-002**: The test suite MUST verify all pull request read commands (`list-prs`, `get-pr`, `get-diff`, `get-comments`, `get-tasks`) return correctly structured responses.
- **FR-003**: The test suite MUST use pre-existing server resources only; no tests may create, modify, or delete any resources on the BitBucket Server.
- **FR-004**: The test suite MUST accept test target configuration (project key, repository slug, PR ID) via `.env` variables to make tests portable across BitBucket instances.
- **FR-005**: The test suite MUST load BitBucket Server credentials (`BITBUCKET_URL`, `BITBUCKET_USER`, `BITBUCKET_TOKEN`) from a `.env` file.
- **FR-006**: The project MUST provide a `.env.example` template showing the required credential variables.
- **FR-007**: The `.env` file MUST be excluded from version control.
- **FR-008**: The project MUST use a dependency manager to handle test dependencies, with a single command to install everything needed.
- **FR-009**: The test suite MUST be runnable with a single command after dependencies are installed.
- **FR-010**: Tests MUST provide clear error messages when credentials are missing or invalid.
- **FR-011**: Tests MUST validate response structure (presence of expected fields) not just HTTP success status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the read-only CLI commands (9 commands: `list-projects`, `list-repos`, `get-repo`, `search-repos`, `list-prs`, `get-pr`, `get-diff`, `get-comments`, `get-tasks`) have at least one integration test that exercises the live API.
- **SC-002**: A new developer can go from fresh clone to running tests in under 5 minutes, following documented instructions.
- **SC-003**: The test suite completes a full run (all read-only tests) in under 2 minutes against a responsive BitBucket Server.
- **SC-004**: When any command's API integration is broken, at least one test fails and clearly identifies the failing command.
- **SC-005**: Credentials are never committed to version control; the `.env` file is gitignored.

## Assumptions

- A BitBucket Server instance is available and accessible from the developer's machine for running integration tests.
- The test BitBucket Server instance has at least one project, one repository, and one open pull request that can be used for read-only test verification.
- The developer has valid BitBucket Server credentials with at least read permissions on the target project and repository.
- The `.env` file approach is standard for local development secrets and does not need additional encryption.
- The dependency manager setup (uv) handles both the existing `requests` runtime dependency and test-specific dependencies.
