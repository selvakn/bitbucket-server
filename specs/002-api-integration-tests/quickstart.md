# Quickstart: API Integration Tests

**Branch**: `002-api-integration-tests` | **Date**: 2026-03-31

## First-Time Setup

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install project dependencies
uv sync

# 3. Create your .env file from the template
cp .env.example .env

# 4. Edit .env with your BitBucket Server credentials and test targets
#    BITBUCKET_URL=https://bitbucket.example.com
#    BITBUCKET_USER=your-username
#    BITBUCKET_TOKEN=your-personal-access-token
#    TEST_PROJECT_KEY=PROJ
#    TEST_REPO_SLUG=my-repo
#    TEST_PR_ID=42
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run only discovery tests
uv run pytest tests/test_discovery.py

# Run only PR read tests
uv run pytest tests/test_pull_requests.py

# Run a specific test
uv run pytest tests/test_discovery.py::test_list_projects
```

## Prerequisites

The test target BitBucket Server instance must have:

- At least one accessible project (matching `TEST_PROJECT_KEY`)
- At least one repository in that project (matching `TEST_REPO_SLUG`)
- At least one pull request in that repository (matching `TEST_PR_ID`, any state)

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `EnvironmentError: Missing required environment variables` | `.env` file missing or incomplete | Copy `.env.example` to `.env` and fill in values |
| Tests skipped with "Missing test config" | `TEST_PROJECT_KEY`, `TEST_REPO_SLUG`, or `TEST_PR_ID` not set | Add test target variables to `.env` |
| `ConnectionError` or timeout | BitBucket Server unreachable | Check `BITBUCKET_URL` and network connectivity |
| `HTTPError 401` | Invalid credentials | Verify `BITBUCKET_USER` and `BITBUCKET_TOKEN` |
| `HTTPError 404` on specific tests | Test target doesn't exist | Verify project/repo/PR exist on the server |
