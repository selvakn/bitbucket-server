# Research: Repository and Project Discovery

**Branch**: `001-repo-discovery` | **Date**: 2026-03-31

## API Endpoints

### 1. List Projects

- **Decision**: Use `GET /rest/api/1.0/projects`
- **Rationale**: This is the standard BitBucket Server REST API endpoint for retrieving projects. It returns a paginated list of all projects the authenticated user has `PROJECT_VIEW` permission on. Supports `name` query parameter for server-side filtering but per spec clarification, we will not expose client-side filtering — the command returns all projects.
- **Alternatives considered**: None. This is the only API endpoint for listing projects.

**Endpoint details**:
- Path: `GET /rest/api/1.0/projects`
- Query params: `start`, `limit` (pagination), `name` (optional filter — not used)
- Permissions: `PROJECT_VIEW` on each returned project
- Response: Paginated `{ values: [...], isLastPage, nextPageStart, ... }`
- Each project value contains: `key`, `name`, `description`, `public`, `type`, `links`

### 2. List Repositories in a Project

- **Decision**: Use `GET /rest/api/1.0/projects/{projectKey}/repos`
- **Rationale**: Standard endpoint for listing repositories within a specific project. Returns paginated results. Already used implicitly in the existing codebase (PR endpoints use the same project/repo path pattern).
- **Alternatives considered**: None. This is the canonical endpoint.

**Endpoint details**:
- Path: `GET /rest/api/1.0/projects/{projectKey}/repos`
- Path params: `projectKey` (required)
- Query params: `start`, `limit` (pagination)
- Permissions: `PROJECT_READ` on the specified project
- Response: Paginated `{ values: [...], isLastPage, nextPageStart, ... }`
- Each repo value contains: `slug`, `name`, `description`, `state`, `project` (nested), `public`, `links` (clone URLs)

### 3. Get Repository Details

- **Decision**: Use `GET /rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}` combined with `GET /rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}/default-branch`
- **Rationale**: The repository endpoint returns full metadata including clone URLs and project association. The default branch is a separate endpoint in BitBucket Server's API, so two calls are needed to get the complete picture specified in the requirements.
- **Alternatives considered**: Using only the repository endpoint (would miss default branch information, which is a key spec requirement).

**Repository endpoint**:
- Path: `GET /rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}`
- Path params: `projectKey`, `repositorySlug` (both required)
- Permissions: `REPO_READ` on the specified repository
- Response: Single `RestRepository` object with `slug`, `name`, `description`, `state`, `project`, `public`, `links`, `forkable`, `scmId`

**Default branch endpoint**:
- Path: `GET /rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}/default-branch`
- Response: `{ "id": "refs/heads/main", "displayId": "main", "type": "BRANCH", ... }`

### 4. Search Repositories Across Projects

- **Decision**: Use `GET /rest/api/1.0/repos`
- **Rationale**: BitBucket Server provides a dedicated global repository search endpoint that searches across all accessible projects. This is exactly what the spec requires for FR-004. It supports `name` filtering which matches our search-by-name requirement.
- **Alternatives considered**: Iterating over all projects and listing repos in each (would be slow and chatty). The global `/repos` endpoint is purpose-built for cross-project discovery.

**Endpoint details**:
- Path: `GET /rest/api/1.0/repos`
- Query params:
  - `name` (string): Filter repositories by name (partial match)
  - `projectname` (string): Filter by project name
  - `projectkey` (string): Filter by project key
  - `visibility` (string): Filter by visibility
  - `permission` (string): Filter by permission level
  - `state` (string): Filter by repository state
  - `archived` (string): Filter archived status
  - `start`, `limit`: Pagination
- Permissions: Implicit read permission (returns repos the user can access)
- Response: Paginated `{ values: [...], isLastPage, nextPageStart, ... }`

## Pagination Strategy

- **Decision**: Reuse the existing `_get_paginated` method on `BitBucketClient`
- **Rationale**: All four endpoints use the same BitBucket Server pagination format (`values`, `isLastPage`, `nextPageStart`) that `_get_paginated` already handles. No modifications to the pagination logic are needed.
- **Alternatives considered**: Custom pagination per command (rejected — would duplicate existing, working code).

## Output Format

- **Decision**: Use `output_json` (existing function) for all new commands, outputting raw API response data
- **Rationale**: Matches the convention used by existing commands (`list-prs`, `get-pr`, etc.). The coding agent consuming the output expects JSON. Project listing and repository listing return arrays; repository details return a single object.
- **Alternatives considered**: Custom formatting or summarized output (rejected — existing commands pass through API data directly, and the consuming agent benefits from rich data).

## CLI Argument Pattern

- **Decision**: Follow the existing argparse subparser pattern with shared argument helpers
- **Rationale**: Consistency with 15 existing commands. Common patterns:
  - `--project` / `-p` for project key
  - `--repo` / `-r` for repository slug
  - These are reused via the existing `add_pr_args` helper
- **Alternatives considered**: None. Consistency with existing CLI is a spec requirement (SC-004).

## Default Branch Retrieval

- **Decision**: For `get-repo`, make two API calls — one for repository details and one for default branch — then merge the results
- **Rationale**: BitBucket Server's `RestRepository` response from the repo endpoint does not consistently include the default branch. The dedicated `/default-branch` endpoint is the reliable way to get this information. The extra API call is acceptable since `get-repo` is a single-item detail view, not a bulk operation.
- **Alternatives considered**: Relying on the `defaultBranch` field in the repo response (unreliable — may be absent or null in some BitBucket Server versions).
