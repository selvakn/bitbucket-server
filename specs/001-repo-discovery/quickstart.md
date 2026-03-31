# Quickstart: Repository and Project Discovery

**Branch**: `001-repo-discovery` | **Date**: 2026-03-31

## Prerequisites

Ensure the following environment variables are set:

```bash
export BITBUCKET_URL="https://bitbucket.example.com"
export BITBUCKET_USER="your-username"
export BITBUCKET_TOKEN="your-personal-access-token"
```

## Discovery Commands

### 1. List all projects

```bash
python3 scripts/bitbucket_api.py list-projects
```

### 2. List repositories in a project

```bash
python3 scripts/bitbucket_api.py list-repos --project MYPROJ
```

### 3. Get repository details

```bash
python3 scripts/bitbucket_api.py get-repo --project MYPROJ --repo my-repo
```

### 4. Search repositories by name

```bash
python3 scripts/bitbucket_api.py search-repos --name payment
```

## Typical Workflow

```
list-projects → pick a project key → list-repos → pick a repo → get-repo
                                                                    ↓
                                                              clone / create-pr
```

Or, if you already know part of the repo name:

```
search-repos --name "service" → find the repo + project → get-repo → create-pr
```
