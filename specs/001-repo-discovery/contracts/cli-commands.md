# CLI Command Contracts: Repository and Project Discovery

**Branch**: `001-repo-discovery` | **Date**: 2026-03-31

All commands are subcommands of `python3 scripts/bitbucket_api.py`.

---

## `list-projects`

List all projects accessible to the authenticated user.

### Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| *(none)* | | | | No arguments needed |

### Example

```bash
python3 scripts/bitbucket_api.py list-projects
```

### Output (JSON)

Array of project objects:

```json
[
  {
    "key": "PROJ",
    "name": "My Project",
    "description": "Project description",
    "public": false,
    "type": "NORMAL",
    "links": { "self": [{ "href": "https://..." }] }
  }
]
```

### Errors

| Condition | Exit code | stderr message |
|-----------|-----------|----------------|
| Missing env vars | 1 | `Configuration Error: Missing required environment variables: ...` |
| Auth failure (401) | 1 | `Error: API Error 401: ...` |
| Network unreachable | 1 | `Network Error: ...` |

---

## `list-repos`

List all repositories within a specified project.

### Arguments

| Argument    | Short | Required | Default | Description        |
|-------------|-------|----------|---------|--------------------|
| `--project` | `-p`  | Yes      |         | Project key        |

### Example

```bash
python3 scripts/bitbucket_api.py list-repos --project MYPROJ
```

### Output (JSON)

Array of repository objects:

```json
[
  {
    "slug": "my-repo",
    "name": "My Repo",
    "description": "Repo description",
    "state": "AVAILABLE",
    "public": false,
    "forkable": true,
    "project": { "key": "MYPROJ", "name": "My Project" },
    "links": {
      "clone": [
        { "href": "https://bitbucket.example.com/scm/MYPROJ/my-repo.git", "name": "http" },
        { "href": "ssh://git@bitbucket.example.com:7999/myproj/my-repo.git", "name": "ssh" }
      ],
      "self": [{ "href": "https://..." }]
    }
  }
]
```

### Errors

| Condition | Exit code | stderr message |
|-----------|-----------|----------------|
| Missing `--project` | 2 | argparse error (automatic) |
| Project not found (404) | 1 | `Error: API Error 404: ...` |
| Auth failure (401) | 1 | `Error: API Error 401: ...` |

---

## `get-repo`

Get detailed information about a specific repository, including its default branch.

### Arguments

| Argument    | Short | Required | Default | Description        |
|-------------|-------|----------|---------|--------------------|
| `--project` | `-p`  | Yes      |         | Project key        |
| `--repo`    | `-r`  | Yes      |         | Repository slug    |

### Example

```bash
python3 scripts/bitbucket_api.py get-repo --project MYPROJ --repo my-repo
```

### Output (JSON)

Single repository object with default branch merged in:

```json
{
  "slug": "my-repo",
  "name": "My Repo",
  "description": "Repo description",
  "state": "AVAILABLE",
  "public": false,
  "forkable": true,
  "scmId": "git",
  "project": {
    "key": "MYPROJ",
    "name": "My Project",
    "description": "Project description",
    "public": false,
    "type": "NORMAL"
  },
  "links": {
    "clone": [
      { "href": "https://bitbucket.example.com/scm/MYPROJ/my-repo.git", "name": "http" },
      { "href": "ssh://git@bitbucket.example.com:7999/myproj/my-repo.git", "name": "ssh" }
    ],
    "self": [{ "href": "https://..." }]
  },
  "defaultBranch": {
    "id": "refs/heads/main",
    "displayId": "main",
    "type": "BRANCH",
    "isDefault": true
  }
}
```

### Errors

| Condition | Exit code | stderr message |
|-----------|-----------|----------------|
| Missing `--project` or `--repo` | 2 | argparse error (automatic) |
| Repository not found (404) | 1 | `Error: API Error 404: ...` |

### Notes

- Makes two API calls: one for repository metadata, one for default branch
- If the default branch endpoint fails (e.g., empty repository with no commits), the `defaultBranch` field is set to `null` and the rest of the repository info is still returned

---

## `search-repos`

Search for repositories by name across all accessible projects.

### Arguments

| Argument   | Short | Required | Default | Description                          |
|------------|-------|----------|---------|--------------------------------------|
| `--name`   | `-n`  | Yes      |         | Repository name to search for        |

### Example

```bash
python3 scripts/bitbucket_api.py search-repos --name payment
```

### Output (JSON)

Array of repository objects (same shape as `list-repos` output), each including its parent project context:

```json
[
  {
    "slug": "payment-service",
    "name": "Payment Service",
    "description": "Handles payment processing",
    "state": "AVAILABLE",
    "project": { "key": "PAYMENTS", "name": "Payments Team" },
    "links": { "clone": [...], "self": [...] }
  },
  {
    "slug": "payment-gateway",
    "name": "Payment Gateway",
    "description": "External payment gateway integration",
    "state": "AVAILABLE",
    "project": { "key": "INTEGRATIONS", "name": "Integrations" },
    "links": { "clone": [...], "self": [...] }
  }
]
```

### Errors

| Condition | Exit code | stderr message |
|-----------|-----------|----------------|
| Missing `--name` | 2 | argparse error (automatic) |
| No results | 0 | Outputs empty JSON array `[]` |
| Auth failure (401) | 1 | `Error: API Error 401: ...` |
