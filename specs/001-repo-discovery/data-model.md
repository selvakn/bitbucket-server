# Data Model: Repository and Project Discovery

**Branch**: `001-repo-discovery` | **Date**: 2026-03-31

## Entities

This feature is read-only — no data is persisted or mutated by the skill. The entities below describe the structure of data returned by the BitBucket Server API and output by the CLI.

### Project

Represents an organizational unit in BitBucket Server that groups related repositories.

| Field       | Type    | Description                                            |
|-------------|---------|--------------------------------------------------------|
| key         | string  | Unique project identifier (e.g., "MYPROJ")             |
| name        | string  | Display name of the project                            |
| description | string  | Optional project description (may be null)             |
| public      | boolean | Whether the project is publicly accessible             |
| type        | string  | Project type (typically "NORMAL" or "PERSONAL")        |
| links       | object  | Self-link URLs for the project                         |

**Source**: `GET /rest/api/1.0/projects` → `values[]`

### Repository

Represents a code repository within a project.

| Field       | Type    | Description                                            |
|-------------|---------|--------------------------------------------------------|
| slug        | string  | URL-safe repository identifier (e.g., "my-repo")      |
| name        | string  | Display name of the repository                         |
| description | string  | Optional repository description (may be null)          |
| state       | string  | Repository state (e.g., "AVAILABLE")                   |
| public      | boolean | Whether the repository is publicly accessible          |
| forkable    | boolean | Whether the repository can be forked                   |
| scmId       | string  | Source control type (typically "git")                   |
| project     | Project | Nested project object (key, name)                      |
| links       | object  | Clone URLs (HTTP, SSH) and self-links                  |

**Source**: `GET /rest/api/1.0/projects/{projectKey}/repos` → `values[]`

### Repository Detail (extended)

The single-repository endpoint returns the same fields as Repository, plus the default branch obtained via a separate API call.

| Field         | Type   | Description                                          |
|---------------|--------|------------------------------------------------------|
| *(all Repository fields)* | | |
| defaultBranch | object | Default branch info: `id` (ref path), `displayId` (short name) |

**Source**: `GET /rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}` merged with `GET /rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}/default-branch`

## Relationships

```
Project (1) ──── has many ────> Repository (*)
```

- A project contains zero or more repositories
- Every repository belongs to exactly one project
- The repository's `project` field contains a nested reference to its parent project (with `key` and `name`)

## Clone URL Structure

The `links` field on a Repository contains a `clone` array with entries like:

| Field | Type   | Description                                |
|-------|--------|--------------------------------------------|
| href  | string | Full clone URL                             |
| name  | string | Protocol name: "http" or "ssh"             |

Example:
```json
{
  "clone": [
    { "href": "https://bitbucket.example.com/scm/PROJ/repo.git", "name": "http" },
    { "href": "ssh://git@bitbucket.example.com:7999/proj/repo.git", "name": "ssh" }
  ]
}
```

## No State Transitions

All operations in this feature are read-only. No entity state is mutated by the discovery commands.
