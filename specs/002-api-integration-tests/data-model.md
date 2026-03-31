# Data Model: API Integration Tests

**Branch**: `002-api-integration-tests` | **Date**: 2026-03-31

## Overview

This feature does not introduce persistent data entities. The "data model" consists of:
1. **Test configuration** — environment variables that configure which server resources tests target
2. **Expected response structures** — the fields tests validate in API responses

## Test Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `BITBUCKET_URL` | Yes | Base URL of BitBucket Server | `https://bitbucket.example.com` |
| `BITBUCKET_USER` | Yes | Username for authentication | `john.doe` |
| `BITBUCKET_TOKEN` | Yes | Personal access token | `NjM2...` |
| `TEST_PROJECT_KEY` | Yes | Project key to test against | `PROJ` |
| `TEST_REPO_SLUG` | Yes | Repository slug to test against | `my-repo` |
| `TEST_PR_ID` | Yes | PR ID to test against (must exist in test repo) | `42` |

### Variable Categories

- **Credentials** (`BITBUCKET_URL`, `BITBUCKET_USER`, `BITBUCKET_TOKEN`): Used by `BitBucketClient.__init__` to authenticate. Missing credentials cause `EnvironmentError` from the client constructor.
- **Test targets** (`TEST_PROJECT_KEY`, `TEST_REPO_SLUG`, `TEST_PR_ID`): Used by test fixtures to know which resources to query. Missing targets cause `pytest.skip()` with a descriptive message.

### Relationships

```
BITBUCKET_URL
  └── TEST_PROJECT_KEY (project must exist on this server)
        └── TEST_REPO_SLUG (repo must exist in this project)
              └── TEST_PR_ID (PR must exist in this repo, any state)
```

## Expected Response Structures

### Project (from `list_projects`)

```
{
  "key": str,          # unique project identifier
  "name": str,         # human-readable name
  "description": str,  # optional
  "public": bool,
  "type": str,         # "NORMAL" or "PERSONAL"
  "links": dict
}
```

### Repository (from `list_repositories`, `search_repositories`)

```
{
  "slug": str,         # unique within project
  "name": str,
  "project": {         # parent project reference
    "key": str
  },
  "state": str,        # "AVAILABLE"
  "public": bool,
  "links": dict        # contains clone URLs
}
```

### Repository Detail (from `get_repository`)

Same as Repository, plus:

```
{
  ...Repository fields,
  "defaultBranch": {   # may be null if no branches
    "id": str,         # "refs/heads/main"
    "displayId": str   # "main"
  } | null
}
```

### Pull Request (from `list_pull_requests`, `get_pull_request`)

```
{
  "id": int,
  "title": str,
  "state": str,        # "OPEN", "MERGED", "DECLINED"
  "author": {
    "user": {
      "displayName": str
    }
  },
  "fromRef": dict,
  "toRef": dict
}
```

### Diff (from `get_diff`)

```
{
  "diffs": list        # list of file diffs
}
```

### Comment (from `get_comments`)

```
{
  "id": int,
  "text": str,
  "author": str,       # displayName (formatted by _format_comment)
  "state": str,
  "severity": str,
  "createdDate": int,
  "threadResolved": bool
}
```

### Task (from `get_tasks`)

```
{
  "id": int,
  "text": str,
  "state": str,        # "OPEN" or "RESOLVED"
  "author": str
}
```
