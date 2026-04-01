# BitBucket Server REST API Endpoints Reference

Base URL: `{BITBUCKET_URL}/rest/api/1.0`

## Authentication

All requests use HTTP Basic Authentication with username and personal access token.

```
Authorization: Basic <base64(username:token)>
```

## Project & Repository Endpoints

### List Projects

```
GET /projects
```

**Parameters:**
- `name` (optional): Filter by project name
- `start` (optional): Pagination start
- `limit` (optional): Pagination limit

**Permissions:** `PROJECT_VIEW` on each returned project

**Response:**
```json
{
  "values": [
    {
      "key": "PROJ",
      "name": "My Project",
      "description": "Project description",
      "public": false,
      "type": "NORMAL",
      "links": { "self": [{ "href": "https://..." }] }
    }
  ],
  "isLastPage": true,
  "start": 0,
  "limit": 25
}
```

### List Repositories in Project

```
GET /projects/{projectKey}/repos
```

**Parameters:**
- `start` (optional): Pagination start
- `limit` (optional): Pagination limit

**Permissions:** `PROJECT_READ` on the specified project

**Response:**
```json
{
  "values": [
    {
      "slug": "my-repo",
      "name": "My Repo",
      "description": "Repo description",
      "state": "AVAILABLE",
      "public": false,
      "forkable": true,
      "scmId": "git",
      "project": { "key": "PROJ", "name": "My Project" },
      "links": {
        "clone": [
          { "href": "https://bitbucket.example.com/scm/PROJ/my-repo.git", "name": "http" },
          { "href": "ssh://git@bitbucket.example.com:7999/proj/my-repo.git", "name": "ssh" }
        ],
        "self": [{ "href": "https://..." }]
      }
    }
  ],
  "isLastPage": true,
  "start": 0,
  "limit": 25
}
```

### Get Repository

```
GET /projects/{projectKey}/repos/{repositorySlug}
```

**Permissions:** `REPO_READ` on the specified repository

**Response:** Single `RestRepository` object (same shape as list values above).

### Get Repository Default Branch

```
GET /projects/{projectKey}/repos/{repositorySlug}/default-branch
```

**Response:**
```json
{
  "id": "refs/heads/main",
  "displayId": "main",
  "type": "BRANCH",
  "isDefault": true
}
```

### Search Repositories (Global)

```
GET /repos
```

Searches across all accessible projects.

**Parameters:**
- `name` (optional): Filter by repository name (partial match)
- `projectname` (optional): Filter by project name
- `projectkey` (optional): Filter by project key
- `visibility` (optional): Filter by visibility
- `state` (optional): Filter by repository state
- `start` (optional): Pagination start
- `limit` (optional): Pagination limit

**Permissions:** Implicit read permission (returns repos the user can access)

**Response:** Paginated list of `RestRepository` objects (same shape as List Repositories response).

## Pull Request Endpoints

### List Pull Requests

```
GET /projects/{projectKey}/repos/{repoSlug}/pull-requests
```

**Parameters:**
- `state` (optional): OPEN, MERGED, DECLINED, ALL (default: OPEN)
- `direction` (optional): INCOMING, OUTGOING (default: INCOMING)
- `at` (optional): Branch to filter by
- `start` (optional): Pagination start
- `limit` (optional): Pagination limit

**Response:**
```json
{
  "values": [
    {
      "id": 1,
      "title": "PR Title",
      "description": "PR Description",
      "state": "OPEN",
      "fromRef": { "id": "refs/heads/feature", "displayId": "feature" },
      "toRef": { "id": "refs/heads/main", "displayId": "main" },
      "author": { "user": { "name": "username", "displayName": "User Name" } },
      "reviewers": [...],
      "createdDate": 1234567890000,
      "updatedDate": 1234567890000
    }
  ],
  "isLastPage": true,
  "start": 0,
  "limit": 25
}
```

### Get Pull Request

```
GET /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}
```

### Create Pull Request

```
POST /projects/{projectKey}/repos/{repoSlug}/pull-requests
```

**Request Body:**
```json
{
  "title": "PR Title",
  "description": "PR Description",
  "fromRef": {
    "id": "refs/heads/feature-branch",
    "repository": {
      "slug": "repo-name",
      "project": { "key": "PROJECT" }
    }
  },
  "toRef": {
    "id": "refs/heads/main",
    "repository": {
      "slug": "repo-name",
      "project": { "key": "PROJECT" }
    }
  },
  "reviewers": [
    { "user": { "name": "reviewer-username" } }
  ]
}
```

### Get Pull Request Diff

```
GET /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/diff
```

**Parameters:**
- `contextLines` (optional): Number of context lines (default: 3)
- `whitespace` (optional): Whitespace handling

### Approve Pull Request

```
POST /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/approve
```

### Unapprove Pull Request

```
DELETE /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/approve
```

### Merge Pull Request

```
POST /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/merge
```

**Parameters:**
- `version` (required): Current version of the PR (for optimistic locking)

### Decline Pull Request

```
POST /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/decline
```

**Parameters:**
- `version` (required): Current version of the PR

## Comment Endpoints

### Get Activities (includes comments)

```
GET /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/activities
```

**Response:**
```json
{
  "values": [
    {
      "id": 1,
      "action": "COMMENTED",
      "comment": {
        "id": 100,
        "text": "Comment text",
        "author": { "name": "user", "displayName": "User Name" },
        "createdDate": 1234567890000,
        "state": "OPEN",
        "severity": "NORMAL",
        "comments": [
          { "id": 101, "text": "Reply text", ... }
        ]
      },
      "commentAnchor": {
        "path": "src/file.py",
        "line": 42,
        "lineType": "ADDED",
        "fileType": "TO"
      }
    }
  ]
}
```

### Add Comment

```
POST /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/comments
```

**General Comment:**
```json
{
  "text": "This looks good!"
}
```

**Inline Comment:**
```json
{
  "text": "Consider renaming this variable",
  "anchor": {
    "path": "src/file.py",
    "line": 42,
    "lineType": "ADDED",
    "fileType": "TO"
  }
}
```

**Anchor Line Types:**
- `ADDED` - Line added in the PR
- `REMOVED` - Line removed in the PR
- `CONTEXT` - Unchanged context line

**Anchor File Types:**
- `TO` - New version of the file
- `FROM` - Old version of the file

### Reply to Comment

```
POST /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/comments/{commentId}/comments
```

**Request Body:**
```json
{
  "text": "Reply text"
}
```

### Update Comment

```
PUT /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/comments/{commentId}
```

**Request Body:**
```json
{
  "text": "Updated text",
  "version": 0
}
```

### Delete Comment

```
DELETE /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/comments/{commentId}
```

**Parameters:**
- `version` (required): Current version of the comment

## Task Endpoints

**Note:** Tasks in BitBucket Server are now managed as Comments with `severity: BLOCKER`. The dedicated `/tasks` API is deprecated. Use the Comments API instead.

### Get Tasks

Tasks are retrieved by filtering comments with `severity: BLOCKER` from the activities endpoint:

```
GET /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/activities
```

Filter the response for `action: COMMENTED` entries where `comment.severity: BLOCKER`.

### Complete/Reopen Task

Update the comment's state via the Comments API:

```
PUT /projects/{projectKey}/repos/{repoSlug}/pull-requests/{pullRequestId}/comments/{commentId}
```

**Request Body:**
```json
{
  "state": "RESOLVED",
  "version": 0
}
```

**Task/Comment States:**
- `OPEN` - Task is open/unresolved
- `RESOLVED` - Task is completed/resolved

**Note:** The `version` field is required for optimistic locking. Get the current version from the comment before updating.

## Error Responses

All errors follow this format:

```json
{
  "errors": [
    {
      "context": "field_name",
      "message": "Error description",
      "exceptionName": "com.atlassian.bitbucket.SomeException"
    }
  ]
}
```

**Common HTTP Status Codes:**
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `409` - Conflict (version mismatch, merge conflict)

## Pagination

Paginated endpoints return:

```json
{
  "values": [...],
  "size": 25,
  "limit": 25,
  "start": 0,
  "isLastPage": false,
  "nextPageStart": 25
}
```

To get the next page, use `?start={nextPageStart}`.
