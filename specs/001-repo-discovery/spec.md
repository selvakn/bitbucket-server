# Feature Specification: Repository and Project Discovery

**Feature Branch**: `001-repo-discovery`  
**Created**: 2026-03-31  
**Status**: Draft  
**Input**: User description: "so far this repo (which is a coding agent skill) has been focused on pull request workflows. In addition to that, we want the abilities to list projects / repositories, to enable discovering repositories, in an ecosystem where there are multiple repositories, owned by different teams and they dependent on each other, and at times, you will have to raise PRs to other teams."

## Clarifications

### Session 2026-03-31

- Q: Should listing branches within a repository be in scope for this feature? → A: No, branch listing is a separate feature; this feature covers only project/repo-level discovery.
- Q: Should list commands support optional name filtering, or is the cross-project search command sufficient? → A: No filtering on list commands; the search command is sufficient for filtering needs.

## Scope Boundaries

**In scope**: Listing projects, listing repositories within a project, getting repository details, searching repositories by name.

**Out of scope**: Listing branches within a repository (separate feature), repository permissions/access management, repository statistics or activity history.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List All Projects (Priority: P1)

As a developer working in a multi-team ecosystem, I want to list all available projects on the BitBucket Server instance so I can see what teams and organizational units exist and understand the landscape of the codebase I operate within.

**Why this priority**: Listing projects is the foundational entry point for discovery. Without knowing what projects exist, a user cannot navigate to repositories. This is the top-level organizational unit in BitBucket Server.

**Independent Test**: Can be fully tested by requesting a list of projects and verifying the output contains project names, keys, and descriptions. Delivers immediate value by giving users visibility into the organizational structure.

**Acceptance Scenarios**:

1. **Given** a user with valid BitBucket credentials, **When** they request a list of projects, **Then** the system returns all projects accessible to the user, including each project's key, name, and description.
2. **Given** a BitBucket instance with many projects, **When** the user requests a list of projects, **Then** the system handles pagination and returns the complete list.
3. **Given** a user with limited permissions, **When** they request a list of projects, **Then** the system returns only the projects the user has access to (as determined by BitBucket Server's access control).

---

### User Story 2 - List Repositories Within a Project (Priority: P1)

As a developer, I want to list all repositories within a given project so I can discover what codebases a team owns and find repositories I may need to interact with (e.g., to raise a PR or understand a dependency).

**Why this priority**: Equally critical as listing projects — once a user knows which project to explore, they need to see the repositories within it. This is the primary mechanism for discovering codebases owned by other teams.

**Independent Test**: Can be fully tested by specifying a project key and verifying the output contains repository names, slugs, and clone URLs. Delivers value by enabling a developer to find the exact repository they need.

**Acceptance Scenarios**:

1. **Given** a valid project key, **When** the user requests a list of repositories in that project, **Then** the system returns all repositories in the project, including each repository's name, slug, and description.
2. **Given** a project with many repositories, **When** the user requests the list, **Then** the system handles pagination and returns the complete list.
3. **Given** an invalid or inaccessible project key, **When** the user requests a list of repositories, **Then** the system returns a clear error message indicating the project was not found or is not accessible.

---

### User Story 3 - Get Repository Details (Priority: P2)

As a developer who has found a repository of interest, I want to view its details — such as its default branch, clone URLs, and project association — so I can understand how to interact with it (clone it, raise PRs against it, etc.).

**Why this priority**: After discovering a repository by listing, the next natural step is to inspect its details before taking action. This bridges discovery and action (e.g., creating a cross-team PR).

**Independent Test**: Can be fully tested by specifying a project key and repository slug and verifying that detailed repository metadata is returned. Delivers value by giving developers the information needed to clone or contribute.

**Acceptance Scenarios**:

1. **Given** a valid project key and repository slug, **When** the user requests repository details, **Then** the system returns the repository's name, slug, description, default branch, clone URLs (HTTP and SSH), project info, and public/private status.
2. **Given** an invalid repository slug, **When** the user requests details, **Then** the system returns a clear error indicating the repository was not found.

---

### User Story 4 - Search Repositories Across Projects (Priority: P3)

As a developer in an ecosystem with many projects and repositories, I want to search for repositories by name or keyword so I can quickly find a specific repository without manually browsing through every project.

**Why this priority**: Search is a convenience feature that becomes essential at scale. While listing projects and repositories covers the core need, search accelerates discovery significantly when the user already knows part of the repository name.

**Independent Test**: Can be fully tested by providing a search term and verifying that matching repositories are returned across all accessible projects. Delivers value by reducing time spent navigating large BitBucket instances.

**Acceptance Scenarios**:

1. **Given** a search term, **When** the user searches for repositories, **Then** the system returns all repositories whose name or description contains the search term, across all accessible projects.
2. **Given** a search term that matches no repositories, **When** the user searches, **Then** the system returns an empty result set with a clear message indicating no matches were found.
3. **Given** a search term that matches repositories across multiple projects, **When** the user searches, **Then** the results include the project key/name alongside each repository so the user can distinguish between them.

---

### Edge Cases

- What happens when the user's credentials have expired or are invalid? The system should return a clear authentication error.
- What happens when the BitBucket Server instance is unreachable? The system should return a connection error with a helpful message.
- What happens when a project exists but contains zero repositories? The system should return an empty list, not an error.
- What happens when paginated results are very large (hundreds of projects or repositories)? The system should handle pagination transparently and return complete results.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a command to list all projects accessible to the authenticated user, returning each project's key, name, and description. No client-side filtering is required; the command returns all accessible projects.
- **FR-002**: System MUST provide a command to list all repositories within a specified project, returning each repository's name, slug, and description. No client-side filtering is required; users should use the search command (FR-004) for name-based lookup.
- **FR-003**: System MUST provide a command to retrieve detailed information about a specific repository, including its name, slug, description, default branch, clone URLs, and project association.
- **FR-004**: System MUST provide a command to search for repositories by name across all accessible projects, returning matching repositories with their project context.
- **FR-005**: System MUST handle paginated responses from the BitBucket Server API transparently, returning complete result sets to the user.
- **FR-006**: System MUST return output in a consistent format, matching the conventions already established by existing pull request commands (JSON for successful operations, clear error messages for failures).
- **FR-007**: System MUST use the same authentication mechanism (environment variables: `BITBUCKET_URL`, `BITBUCKET_USER`, `BITBUCKET_TOKEN`) as existing commands.
- **FR-008**: System MUST provide clear, actionable error messages when operations fail due to authentication issues, invalid parameters, or server errors.

### Key Entities

- **Project**: An organizational unit in BitBucket Server that groups related repositories. Key attributes: key (unique identifier), name, description.
- **Repository**: A code repository within a project. Key attributes: slug (URL-safe identifier), name, description, default branch, clone URLs (HTTP and SSH), associated project.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can discover all accessible projects on a BitBucket Server instance in a single command invocation.
- **SC-002**: Users can discover all repositories within a project in a single command invocation.
- **SC-003**: Users can find a specific repository by name without knowing which project it belongs to, using a search command.
- **SC-004**: The new discovery commands follow the same usage patterns (CLI flags, output format, error handling) as existing pull request commands, requiring no additional learning for existing users.
- **SC-005**: The skill documentation (SKILL.md) is updated so that the coding agent knows when and how to use the new discovery commands.

## Assumptions

- The existing BitBucket Server REST API provides endpoints for listing projects, listing repositories, and searching repositories, which this feature will consume.
- The authenticated user's permissions on the BitBucket Server instance determine what projects and repositories are visible; the skill does not implement its own access control.
- The existing authentication mechanism (`BITBUCKET_URL`, `BITBUCKET_USER`, `BITBUCKET_TOKEN` environment variables) is sufficient for the new discovery endpoints — no additional credentials are required.
- The feature extends the existing `scripts/bitbucket_api.py` CLI tool with new commands rather than creating a separate tool.
- Pagination limits and defaults will follow BitBucket Server's standard API behavior (typically 25 items per page), with the skill aggregating all pages automatically.
