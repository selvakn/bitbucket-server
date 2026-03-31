# Research: API Integration Tests

**Branch**: `002-api-integration-tests` | **Date**: 2026-03-31

## uv Project Setup

### Bootstrapping

- `uv init` in an existing directory creates `pyproject.toml`, `.python-version`, and a `hello.py` entry point. Since we already have source code, we run `uv init` and remove the generated `hello.py`.
- `uv add requests` adds the existing runtime dependency to `pyproject.toml` and creates `uv.lock`.
- `uv add --dev pytest python-dotenv` adds test dependencies under `[dependency-groups] > dev`.

### pyproject.toml Structure

```toml
[project]
name = "bitbucket-server"
version = "0.1.0"
description = "BitBucket Server REST API CLI Tool"
requires-python = ">=3.11"
dependencies = ["requests"]

[dependency-groups]
dev = ["pytest", "python-dotenv"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Running Tests

```bash
uv run pytest           # run all tests
uv run pytest tests/test_discovery.py   # run only discovery tests
uv run pytest -v        # verbose output
```

`uv run` automatically creates/activates the virtual environment and installs dependencies on first run.

## python-dotenv Integration

### conftest.py Pattern

```python
import pytest
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()
```

- `scope="session"`: loads `.env` once for the entire test run (not per test)
- `autouse=True`: applies to all tests without explicit fixture reference
- `load_dotenv()` reads `.env` from the project root (cwd) by default

### .env File Format

```env
BITBUCKET_URL=https://bitbucket.example.com
BITBUCKET_USER=your-username
BITBUCKET_TOKEN=your-personal-access-token
TEST_PROJECT_KEY=PROJ
TEST_REPO_SLUG=my-repo
TEST_PR_ID=42
```

### Precedence

`load_dotenv()` does NOT override existing environment variables by default. If a variable is already set in the shell, the shell value takes precedence. This is the correct behavior for CI environments where variables are injected externally.

## pytest Fixtures for BitBucketClient

### Client Fixture

```python
@pytest.fixture(scope="session")
def client():
    return BitBucketClient()
```

Session-scoped to reuse the HTTP session across all tests. `BitBucketClient.__init__` reads `os.environ` which is populated by the `load_env` fixture.

### Test Configuration Fixture

```python
@pytest.fixture(scope="session")
def test_config():
    config = {
        "project_key": os.environ.get("TEST_PROJECT_KEY"),
        "repo_slug": os.environ.get("TEST_REPO_SLUG"),
        "pr_id": os.environ.get("TEST_PR_ID"),
    }
    missing = [k for k, v in config.items() if not v]
    if missing:
        pytest.skip(f"Missing test config: {', '.join(missing)}")
    config["pr_id"] = int(config["pr_id"])
    return config
```

If test target variables are missing, tests skip with a descriptive message rather than failing with cryptic errors.

## Commands Under Test

### Discovery Commands (4)

| Command | Client Method | Args | Returns |
|---------|---------------|------|---------|
| `list-projects` | `list_projects()` | none | `list[dict]` — each has `key`, `name` |
| `list-repos` | `list_repositories(project)` | project key | `list[dict]` — each has `slug`, `name`, `project` |
| `get-repo` | `get_repository(project, repo)` | project key, repo slug | `dict` — has `slug`, `name`, `defaultBranch`, `links` |
| `search-repos` | `search_repositories(name)` | name string | `list[dict]` — same as list-repos |

### PR Read Commands (5)

| Command | Client Method | Args | Returns |
|---------|---------------|------|---------|
| `list-prs` | `list_pull_requests(project, repo, state)` | project, repo, state | `list[dict]` — each has `id`, `title`, `state`, `author` |
| `get-pr` | `get_pull_request(project, repo, pr_id)` | project, repo, pr_id | `dict` — has `id`, `title`, `state`, `fromRef`, `toRef` |
| `get-diff` | `get_diff(project, repo, pr_id)` | project, repo, pr_id | `dict` — has `diffs` |
| `get-comments` | `get_comments(project, repo, pr_id)` | project, repo, pr_id | `list[dict]` — each has `id`, `text`, `author` |
| `get-tasks` | `get_tasks(project, repo, pr_id)` | project, repo, pr_id | `list[dict]` — each has `id`, `text`, `state` |
