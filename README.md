# BitBucket Server Skill for Claude Code

A [Claude Code](https://claude.ai/code) skill that enables interaction with BitBucket Server's REST API, focusing on Pull Request management workflows.

## Features

- **Pull Request Management**: List, create, review, approve, merge, and decline PRs
- **Code Review**: View diffs, add comments (general and inline), reply to comments
- **Task Management**: List, complete, and reopen tasks (BLOCKER comments)
- **Batch Operations**: Complete or reopen multiple tasks in a single request

## Installation

Copy the `bitbucket-server` folder to your Claude Code skills directory:

```bash
# User-level installation
cp -r bitbucket-server ~/.claude/skills/

# Or project-level installation
cp -r bitbucket-server .claude/skills/
```

## Configuration

Set the following environment variables:

```bash
export BITBUCKET_URL="https://bitbucket.example.com"
export BITBUCKET_USER="your-username"
export BITBUCKET_TOKEN="your-personal-access-token"
```

## Requirements

- Python 3.6+
- `requests` library (`pip install requests`)

## Usage

Once installed, Claude Code will automatically use this skill when you ask about BitBucket Server operations. Examples:

- "Show me all open PRs in project MYPROJ/my-repo"
- "Create a PR from feature/login to main"
- "What are the open tasks on PR #42?"
- "Complete all tasks on PR #42"
- "Show me the comments on PR #123"

## Available Commands

The skill provides a CLI tool at `scripts/bitbucket_api.py`:

### Pull Requests

```bash
# List PRs
python3 scripts/bitbucket_api.py list-prs --project PROJ --repo my-repo --state OPEN

# Get PR details
python3 scripts/bitbucket_api.py get-pr --project PROJ --repo my-repo --pr-id 42

# Create PR
python3 scripts/bitbucket_api.py create-pr --project PROJ --repo my-repo \
  --title "My PR" --from-branch feature/x --to-branch main

# Get diff
python3 scripts/bitbucket_api.py get-diff --project PROJ --repo my-repo --pr-id 42

# Approve/Merge/Decline
python3 scripts/bitbucket_api.py approve --project PROJ --repo my-repo --pr-id 42
python3 scripts/bitbucket_api.py merge --project PROJ --repo my-repo --pr-id 42
python3 scripts/bitbucket_api.py decline --project PROJ --repo my-repo --pr-id 42
```

### Comments

```bash
# Get comments
python3 scripts/bitbucket_api.py get-comments --project PROJ --repo my-repo --pr-id 42

# Add general comment
python3 scripts/bitbucket_api.py add-comment --project PROJ --repo my-repo --pr-id 42 \
  --text "Looks good!"

# Add inline comment
python3 scripts/bitbucket_api.py add-comment --project PROJ --repo my-repo --pr-id 42 \
  --text "Consider renaming" --file-path src/main.py --line 42 --line-type ADDED

# Reply to comment
python3 scripts/bitbucket_api.py reply-comment --project PROJ --repo my-repo --pr-id 42 \
  --comment-id 123 --text "Fixed!"
```

### Tasks

Tasks in BitBucket Server are comments with BLOCKER severity.

```bash
# List tasks
python3 scripts/bitbucket_api.py get-tasks --project PROJ --repo my-repo --pr-id 42

# Complete single task
python3 scripts/bitbucket_api.py complete-task --project PROJ --repo my-repo --pr-id 42 \
  --comment-id 456

# Complete multiple tasks
python3 scripts/bitbucket_api.py complete-tasks --project PROJ --repo my-repo --pr-id 42 \
  --comment-ids 456,789,123

# Reopen tasks
python3 scripts/bitbucket_api.py reopen-task --project PROJ --repo my-repo --pr-id 42 \
  --comment-id 456
python3 scripts/bitbucket_api.py reopen-tasks --project PROJ --repo my-repo --pr-id 42 \
  --comment-ids 456,789
```

## API Reference

See [references/api_endpoints.md](references/api_endpoints.md) for detailed BitBucket Server REST API documentation.

## License

MIT License - see [LICENSE](LICENSE) for details.
