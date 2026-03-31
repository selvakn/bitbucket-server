# Contract: Test Structure

**Branch**: `002-api-integration-tests` | **Date**: 2026-03-31

## File Layout

```
tests/
├── conftest.py              # Shared fixtures
├── test_discovery.py        # Discovery command tests (US-1)
└── test_pull_requests.py    # PR read command tests (US-2)
```

## conftest.py — Shared Fixtures

### `load_env` (session, autouse)

Loads `.env` file using `python-dotenv` before any test runs. Session-scoped so it runs exactly once.

### `client` (session)

Returns a `BitBucketClient` instance. Session-scoped to reuse the HTTP session. Depends on `load_env` (via autouse ordering).

**Error behavior**: If credentials are missing, `BitBucketClient.__init__` raises `EnvironmentError` with a message listing the missing variables. This causes the entire test session to fail immediately with a clear message.

### `test_config` (session)

Returns a dict with test target identifiers read from environment:

```python
{
    "project_key": str,  # from TEST_PROJECT_KEY
    "repo_slug": str,    # from TEST_REPO_SLUG
    "pr_id": int,        # from TEST_PR_ID
}
```

**Error behavior**: If any test target variable is missing, calls `pytest.skip()` with a message listing the missing variables. This skips all dependent tests rather than failing them.

## test_discovery.py — Discovery Tests

### `test_list_projects(client)`

- Calls `client.list_projects()`
- Asserts result is a non-empty list
- Asserts each item has `key` (str) and `name` (str)

### `test_list_repositories(client, test_config)`

- Calls `client.list_repositories(test_config["project_key"])`
- Asserts result is a list (may be empty if project has no repos, but configured project should have at least one)
- Asserts each item has `slug` (str), `name` (str), and nested `project.key`

### `test_get_repository(client, test_config)`

- Calls `client.get_repository(test_config["project_key"], test_config["repo_slug"])`
- Asserts result is a dict with `slug`, `name`, `links`
- Asserts `slug` matches `test_config["repo_slug"]`
- Asserts `defaultBranch` key exists (value may be dict or None)

### `test_search_repositories(client, test_config)`

- Calls `client.search_repositories(test_config["repo_slug"])`
- Asserts result is a list
- Asserts at least one result has a `slug` matching `test_config["repo_slug"]`

## test_pull_requests.py — PR Read Tests

### `test_list_pull_requests(client, test_config)`

- Calls `client.list_pull_requests(test_config["project_key"], test_config["repo_slug"], state="ALL")`
- Asserts result is a list (use `state="ALL"` to ensure the configured PR appears regardless of its state)
- Asserts each item has `id` (int), `title` (str), `state` (str)

### `test_get_pull_request(client, test_config)`

- Calls `client.get_pull_request(test_config["project_key"], test_config["repo_slug"], test_config["pr_id"])`
- Asserts result is a dict with `id`, `title`, `state`, `author`, `fromRef`, `toRef`
- Asserts `result["id"]` equals `test_config["pr_id"]`

### `test_get_diff(client, test_config)`

- Calls `client.get_diff(test_config["project_key"], test_config["repo_slug"], test_config["pr_id"])`
- Asserts result is a dict with `diffs` key
- Asserts `diffs` is a list

### `test_get_comments(client, test_config)`

- Calls `client.get_comments(test_config["project_key"], test_config["repo_slug"], test_config["pr_id"])`
- Asserts result is a list
- If non-empty, asserts each item has `id` (int), `text` (str), `author` (str)

### `test_get_tasks(client, test_config)`

- Calls `client.get_tasks(test_config["project_key"], test_config["repo_slug"], test_config["pr_id"])`
- Asserts result is a list
- If non-empty, asserts each item has `id` (int), `text` (str), `state` (str)

## Assertion Strategy

All tests follow these principles:

1. **Structure over values**: Assert field presence and types, not exact values (live server data is unpredictable)
2. **Smoke checks with known data**: Where the test config provides a known value (repo slug, PR ID), assert it appears in the response
3. **Graceful empty collections**: For `get_comments` and `get_tasks`, assert the result is a list but don't require it to be non-empty (the configured PR may not have comments or tasks)
4. **No mutations**: Tests only call read methods — no POST, PUT, or DELETE operations
