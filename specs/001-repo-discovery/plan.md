# Implementation Plan: Repository and Project Discovery

**Branch**: `001-repo-discovery` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-repo-discovery/spec.md`

## Summary

Add project and repository discovery commands to the existing BitBucket Server CLI skill. Four new CLI commands (`list-projects`, `list-repos`, `get-repo`, `search-repos`) will be added to `scripts/bitbucket_api.py`, following the same patterns as the existing PR/comment/task commands: new methods on `BitBucketClient` with corresponding argparse subparsers, JSON output via `output_json`, and transparent pagination via `_get_paginated`.

## Technical Context

**Language/Version**: Python 3.6+ (matching existing codebase)
**Primary Dependencies**: `requests` (already in use; no new dependencies)
**Storage**: N/A (stateless CLI tool — all data comes from BitBucket Server API)
**Testing**: Manual testing against a BitBucket Server instance (no test framework in current repo)
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: CLI tool / coding agent skill
**Performance Goals**: N/A (thin API wrapper; performance bound by server response)
**Constraints**: Must preserve backward compatibility with all existing commands
**Scale/Scope**: Handles pagination for instances with hundreds of projects/repositories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution file (`constitution.md`) contains only template placeholders with no ratified principles. No gates are defined; proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/001-repo-discovery/
├── plan.md              # This file
├── research.md          # Phase 0: API endpoint research
├── data-model.md        # Phase 1: Entity model
├── quickstart.md        # Phase 1: Usage quick reference
├── contracts/           # Phase 1: CLI command contracts
│   └── cli-commands.md  # New command definitions
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
scripts/
└── bitbucket_api.py     # Extended with 4 new commands + 4 new client methods

references/
└── api_endpoints.md     # Updated with project/repo endpoint documentation

SKILL.md                 # Updated with discovery command documentation
README.md                # Updated with discovery command examples
```

**Structure Decision**: The existing single-file CLI architecture (`scripts/bitbucket_api.py`) is retained. The four new commands add approximately 120 lines of code (4 client methods + 4 argparse subparsers + 4 dispatch branches), keeping the file well under 700 lines total. No structural refactoring is needed.

## Complexity Tracking

No constitution violations. No complexity justification required.
