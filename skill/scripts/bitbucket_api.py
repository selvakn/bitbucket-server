#!/usr/bin/env python3
"""
BitBucket Server REST API CLI Tool

A command-line interface for interacting with BitBucket Server's REST API,
supporting project/repository discovery and Pull Request management workflows.

Environment Variables Required:
    BITBUCKET_URL   - Base URL of BitBucket Server (e.g., https://bitbucket.example.com)
    BITBUCKET_USER  - Username for authentication
    BITBUCKET_TOKEN - Personal access token
"""

import argparse
import json
import os
import sys
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


class BitBucketClient:
    """Client for BitBucket Server REST API."""

    def __init__(self):
        self.base_url = os.environ.get("BITBUCKET_URL")
        self.username = os.environ.get("BITBUCKET_USER")
        self.token = os.environ.get("BITBUCKET_TOKEN")

        if not all([self.base_url, self.username, self.token]):
            missing = []
            if not self.base_url:
                missing.append("BITBUCKET_URL")
            if not self.username:
                missing.append("BITBUCKET_USER")
            if not self.token:
                missing.append("BITBUCKET_TOKEN")
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

        self.base_url = self.base_url.rstrip("/")
        self.api_url = f"{self.base_url}/rest/api/1.0"
        self.session = requests.Session()
        self.session.auth = (self.username, self.token)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _request(self, method, endpoint, **kwargs):
        """Make an API request and handle errors."""
        url = f"{self.api_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)

        if not response.ok:
            error_msg = f"API Error {response.status_code}"
            try:
                error_data = response.json()
                if "errors" in error_data:
                    error_msg += ": " + "; ".join(e.get("message", str(e)) for e in error_data["errors"])
                elif "message" in error_data:
                    error_msg += f": {error_data['message']}"
            except (json.JSONDecodeError, KeyError):
                error_msg += f": {response.text}"
            raise requests.HTTPError(error_msg, response=response)

        if response.status_code == 204:
            return {}

        return response.json() if response.text else {}

    def _get_paginated(self, endpoint, **kwargs):
        """Get all results from a paginated endpoint."""
        params = kwargs.pop("params", {})
        all_values = []
        start = 0

        while True:
            params["start"] = start
            result = self._request("GET", endpoint, params=params, **kwargs)
            values = result.get("values", [])
            all_values.extend(values)

            if result.get("isLastPage", True):
                break
            start = result.get("nextPageStart", start + len(values))

        return all_values

    # Project & Repository Methods
    def list_projects(self):
        """List all projects accessible to the authenticated user."""
        return self._get_paginated("/projects")

    def list_repositories(self, project):
        """List all repositories in a project."""
        endpoint = f"/projects/{project}/repos"
        return self._get_paginated(endpoint)

    def get_repository(self, project, repo):
        """Get detailed information about a specific repository, including default branch."""
        endpoint = f"/projects/{project}/repos/{repo}"
        result = self._request("GET", endpoint)
        try:
            branch_endpoint = f"/projects/{project}/repos/{repo}/default-branch"
            default_branch = self._request("GET", branch_endpoint)
            result["defaultBranch"] = default_branch
        except requests.HTTPError:
            result["defaultBranch"] = None
        return result

    def search_repositories(self, name):
        """Search for repositories by name across all accessible projects."""
        return self._get_paginated("/repos", params={"name": name})

    # Pull Request Methods
    def list_pull_requests(self, project, repo, state="OPEN"):
        """List pull requests in a repository."""
        endpoint = f"/projects/{project}/repos/{repo}/pull-requests"
        params = {"state": state} if state else {}
        return self._get_paginated(endpoint, params=params)

    def get_pull_request(self, project, repo, pr_id):
        """Get details of a specific pull request."""
        endpoint = f"/projects/{project}/repos/{repo}/pull-requests/{pr_id}"
        return self._request("GET", endpoint)

    def create_pull_request(self, project, repo, title, from_branch, to_branch, description=""):
        """Create a new pull request."""
        endpoint = f"/projects/{project}/repos/{repo}/pull-requests"
        data = {
            "title": title,
            "description": description,
            "fromRef": {
                "id": f"refs/heads/{from_branch}",
                "repository": {
                    "slug": repo,
                    "project": {"key": project}
                }
            },
            "toRef": {
                "id": f"refs/heads/{to_branch}",
                "repository": {
                    "slug": repo,
                    "project": {"key": project}
                }
            }
        }
        return self._request("POST", endpoint, json=data)

    def get_diff(self, project, repo, pr_id, context_lines=3):
        """Get the diff of a pull request."""
        endpoint = f"/projects/{project}/repos/{repo}/pull-requests/{pr_id}/diff"
        params = {"contextLines": context_lines}
        return self._request("GET", endpoint, params=params)

    def approve_pull_request(self, project, repo, pr_id):
        """Approve a pull request."""
        endpoint = f"/projects/{project}/repos/{repo}/pull-requests/{pr_id}/approve"
        return self._request("POST", endpoint)

    def merge_pull_request(self, project, repo, pr_id, version=None):
        """Merge a pull request."""
        pr = self.get_pull_request(project, repo, pr_id)
        current_version = pr.get("version", 0)

        endpoint = f"/projects/{project}/repos/{repo}/pull-requests/{pr_id}/merge"
        params = {"version": version if version is not None else current_version}
        return self._request("POST", endpoint, params=params)

    def decline_pull_request(self, project, repo, pr_id, version=None):
        """Decline a pull request."""
        pr = self.get_pull_request(project, repo, pr_id)
        current_version = pr.get("version", 0)

        endpoint = f"/projects/{project}/repos/{repo}/pull-requests/{pr_id}/decline"
        params = {"version": version if version is not None else current_version}
        return self._request("POST", endpoint, params=params)

    # Comment Methods
    def get_activities(self, project, repo, pr_id):
        """Get all activities (including comments) on a pull request."""
        endpoint = f"/projects/{project}/repos/{repo}/pull-requests/{pr_id}/activities"
        return self._get_paginated(endpoint)

    def get_comments(self, project, repo, pr_id):
        """Get all comments on a pull request (filtered from activities)."""
        activities = self.get_activities(project, repo, pr_id)
        comments = []
        for activity in activities:
            if activity.get("action") == "COMMENTED":
                comment = activity.get("comment", {})
                if comment:
                    comments.append(self._format_comment(comment, activity))
        return comments

    def _format_comment(self, comment, activity=None):
        """Format a comment for output."""
        result = {
            "id": comment.get("id"),
            "text": comment.get("text"),
            "author": comment.get("author", {}).get("displayName"),
            "createdDate": comment.get("createdDate"),
            "updatedDate": comment.get("updatedDate"),
            "state": comment.get("state"),
            "severity": comment.get("severity"),
            "threadResolved": comment.get("threadResolved", False),
        }

        # Include anchor info for inline comments
        if activity and "commentAnchor" in activity:
            anchor = activity["commentAnchor"]
            result["anchor"] = {
                "path": anchor.get("path"),
                "line": anchor.get("line"),
                "lineType": anchor.get("lineType"),
                "fileType": anchor.get("fileType"),
            }

        # Include nested replies
        if "comments" in comment:
            result["replies"] = [
                self._format_comment(reply) for reply in comment["comments"]
            ]

        return result

    def add_comment(self, project, repo, pr_id, text, file_path=None, line=None, line_type="ADDED"):
        """Add a comment to a pull request."""
        endpoint = f"/projects/{project}/repos/{repo}/pull-requests/{pr_id}/comments"
        data = {"text": text}

        if file_path and line:
            data["anchor"] = {
                "path": file_path,
                "line": line,
                "lineType": line_type,  # ADDED, REMOVED, or CONTEXT
                "fileType": "TO"  # TO for new file, FROM for old file
            }

        return self._request("POST", endpoint, json=data)

    def reply_to_comment(self, project, repo, pr_id, comment_id, text):
        """Reply to an existing comment."""
        endpoint = f"/projects/{project}/repos/{repo}/pull-requests/{pr_id}/comments/{comment_id}/comments"
        data = {"text": text}
        return self._request("POST", endpoint, json=data)

    # Task Methods
    # Note: Tasks in BitBucket Server are Comments with severity=BLOCKER.
    # They are managed via the Comments API, not a separate Tasks API.

    def get_tasks(self, project, repo, pr_id):
        """Get all tasks (BLOCKER comments) on a pull request."""
        comments = self.get_comments(project, repo, pr_id)
        tasks = []
        self._collect_tasks(comments, tasks)
        return tasks

    def _collect_tasks(self, comments, tasks):
        """Recursively collect tasks from comments and their replies."""
        for comment in comments:
            if comment.get("severity") == "BLOCKER":
                tasks.append({
                    "id": comment.get("id"),
                    "text": comment.get("text"),
                    "state": comment.get("state"),
                    "author": comment.get("author"),
                    "anchor": comment.get("anchor"),
                })
            # Check replies for tasks too
            if "replies" in comment:
                self._collect_tasks(comment["replies"], tasks)

    def update_task(self, project, repo, pr_id, comment_id, state, version=None):
        """Update task state (OPEN or RESOLVED) via Comments API."""
        # First get current comment to obtain version if not provided
        if version is None:
            endpoint = f"/projects/{project}/repos/{repo}/pull-requests/{pr_id}/comments/{comment_id}"
            comment = self._request("GET", endpoint)
            version = comment.get("version", 0)

        endpoint = f"/projects/{project}/repos/{repo}/pull-requests/{pr_id}/comments/{comment_id}"
        data = {
            "state": state,
            "version": version
        }
        return self._request("PUT", endpoint, json=data)

    def complete_task(self, project, repo, pr_id, comment_id, version=None):
        """Mark a task as completed (resolve the BLOCKER comment)."""
        return self.update_task(project, repo, pr_id, comment_id, "RESOLVED", version)

    def complete_tasks(self, project, repo, pr_id, comment_ids):
        """Mark multiple tasks as completed. Returns results for each task."""
        results = []
        for comment_id in comment_ids:
            try:
                result = self.complete_task(project, repo, pr_id, comment_id)
                results.append({
                    "comment_id": comment_id,
                    "status": "completed",
                    "success": True,
                    "result": result
                })
            except requests.HTTPError as e:
                results.append({
                    "comment_id": comment_id,
                    "status": "failed",
                    "success": False,
                    "error": str(e)
                })
        return results

    def reopen_task(self, project, repo, pr_id, comment_id, version=None):
        """Reopen a completed task."""
        return self.update_task(project, repo, pr_id, comment_id, "OPEN", version)

    def reopen_tasks(self, project, repo, pr_id, comment_ids):
        """Reopen multiple tasks. Returns results for each task."""
        results = []
        for comment_id in comment_ids:
            try:
                result = self.reopen_task(project, repo, pr_id, comment_id)
                results.append({
                    "comment_id": comment_id,
                    "status": "reopened",
                    "success": True,
                    "result": result
                })
            except requests.HTTPError as e:
                results.append({
                    "comment_id": comment_id,
                    "status": "failed",
                    "success": False,
                    "error": str(e)
                })
        return results


def output_json(data):
    """Output data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(
        description="BitBucket Server REST API CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Common arguments for PR commands
    def add_pr_args(p):
        p.add_argument("--project", "-p", required=True, help="Project key")
        p.add_argument("--repo", "-r", required=True, help="Repository slug")

    def add_pr_id_args(p):
        add_pr_args(p)
        p.add_argument("--pr-id", "-i", required=True, type=int, help="Pull request ID")

    # list-projects
    subparsers.add_parser("list-projects", help="List all accessible projects")

    # list-repos
    p_list_repos = subparsers.add_parser("list-repos", help="List repositories in a project")
    p_list_repos.add_argument("--project", "-p", required=True, help="Project key")

    # get-repo
    p_get_repo = subparsers.add_parser("get-repo", help="Get repository details")
    p_get_repo.add_argument("--project", "-p", required=True, help="Project key")
    p_get_repo.add_argument("--repo", "-r", required=True, help="Repository slug")

    # search-repos
    p_search_repos = subparsers.add_parser("search-repos", help="Search repositories by name")
    p_search_repos.add_argument("--name", "-n", required=True, help="Repository name to search for")

    # list-prs
    p_list = subparsers.add_parser("list-prs", help="List pull requests")
    add_pr_args(p_list)
    p_list.add_argument("--state", "-s", default="OPEN",
                        choices=["OPEN", "MERGED", "DECLINED", "ALL"],
                        help="Filter by state (default: OPEN)")

    # get-pr
    p_get = subparsers.add_parser("get-pr", help="Get pull request details")
    add_pr_id_args(p_get)

    # create-pr
    p_create = subparsers.add_parser("create-pr", help="Create a pull request")
    add_pr_args(p_create)
    p_create.add_argument("--title", "-t", required=True, help="PR title")
    p_create.add_argument("--from-branch", "-f", required=True, help="Source branch")
    p_create.add_argument("--to-branch", "-b", required=True, help="Target branch")
    p_create.add_argument("--description", "-d", default="", help="PR description")

    # get-diff
    p_diff = subparsers.add_parser("get-diff", help="Get pull request diff")
    add_pr_id_args(p_diff)
    p_diff.add_argument("--context", "-c", type=int, default=3, help="Context lines")

    # approve
    p_approve = subparsers.add_parser("approve", help="Approve a pull request")
    add_pr_id_args(p_approve)

    # merge
    p_merge = subparsers.add_parser("merge", help="Merge a pull request")
    add_pr_id_args(p_merge)

    # decline
    p_decline = subparsers.add_parser("decline", help="Decline a pull request")
    add_pr_id_args(p_decline)

    # get-comments
    p_comments = subparsers.add_parser("get-comments", help="Get pull request comments")
    add_pr_id_args(p_comments)

    # add-comment
    p_add_comment = subparsers.add_parser("add-comment", help="Add a comment")
    add_pr_id_args(p_add_comment)
    p_add_comment.add_argument("--text", "-t", required=True, help="Comment text")
    p_add_comment.add_argument("--file-path", help="File path for inline comment")
    p_add_comment.add_argument("--line", type=int, help="Line number for inline comment")
    p_add_comment.add_argument("--line-type", default="ADDED",
                               choices=["ADDED", "REMOVED", "CONTEXT"],
                               help="Line type for inline comment")

    # reply-comment
    p_reply = subparsers.add_parser("reply-comment", help="Reply to a comment")
    add_pr_id_args(p_reply)
    p_reply.add_argument("--comment-id", "-c", required=True, type=int, help="Comment ID")
    p_reply.add_argument("--text", "-t", required=True, help="Reply text")

    # get-tasks
    p_tasks = subparsers.add_parser("get-tasks", help="Get pull request tasks")
    add_pr_id_args(p_tasks)

    # complete-task
    p_complete = subparsers.add_parser("complete-task", help="Complete a task (resolve BLOCKER comment)")
    add_pr_id_args(p_complete)
    p_complete.add_argument("--comment-id", "-c", required=True, type=int, help="Comment ID (task)")

    # complete-tasks (multiple)
    p_complete_multi = subparsers.add_parser("complete-tasks", help="Complete multiple tasks at once")
    add_pr_id_args(p_complete_multi)
    p_complete_multi.add_argument("--comment-ids", "-c", required=True, type=str,
                                   help="Comma-separated list of comment IDs (e.g., 123,456,789)")

    # reopen-task
    p_reopen = subparsers.add_parser("reopen-task", help="Reopen a task")
    add_pr_id_args(p_reopen)
    p_reopen.add_argument("--comment-id", "-c", required=True, type=int, help="Comment ID (task)")

    # reopen-tasks (multiple)
    p_reopen_multi = subparsers.add_parser("reopen-tasks", help="Reopen multiple tasks at once")
    add_pr_id_args(p_reopen_multi)
    p_reopen_multi.add_argument("--comment-ids", "-c", required=True, type=str,
                                 help="Comma-separated list of comment IDs (e.g., 123,456,789)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = BitBucketClient()

        if args.command == "list-projects":
            result = client.list_projects()
            output_json(result)

        elif args.command == "list-repos":
            result = client.list_repositories(args.project)
            output_json(result)

        elif args.command == "get-repo":
            result = client.get_repository(args.project, args.repo)
            output_json(result)

        elif args.command == "search-repos":
            result = client.search_repositories(args.name)
            output_json(result)

        elif args.command == "list-prs":
            state = None if args.state == "ALL" else args.state
            result = client.list_pull_requests(args.project, args.repo, state)
            output_json(result)

        elif args.command == "get-pr":
            result = client.get_pull_request(args.project, args.repo, args.pr_id)
            output_json(result)

        elif args.command == "create-pr":
            result = client.create_pull_request(
                args.project, args.repo, args.title,
                args.from_branch, args.to_branch, args.description
            )
            output_json(result)

        elif args.command == "get-diff":
            result = client.get_diff(args.project, args.repo, args.pr_id, args.context)
            output_json(result)

        elif args.command == "approve":
            result = client.approve_pull_request(args.project, args.repo, args.pr_id)
            output_json({"status": "approved", "pr_id": args.pr_id})

        elif args.command == "merge":
            result = client.merge_pull_request(args.project, args.repo, args.pr_id)
            output_json(result)

        elif args.command == "decline":
            result = client.decline_pull_request(args.project, args.repo, args.pr_id)
            output_json(result)

        elif args.command == "get-comments":
            result = client.get_comments(args.project, args.repo, args.pr_id)
            output_json(result)

        elif args.command == "add-comment":
            result = client.add_comment(
                args.project, args.repo, args.pr_id, args.text,
                args.file_path, args.line, args.line_type
            )
            output_json(result)

        elif args.command == "reply-comment":
            result = client.reply_to_comment(
                args.project, args.repo, args.pr_id, args.comment_id, args.text
            )
            output_json(result)

        elif args.command == "get-tasks":
            result = client.get_tasks(args.project, args.repo, args.pr_id)
            output_json(result)

        elif args.command == "complete-task":
            result = client.complete_task(args.project, args.repo, args.pr_id, args.comment_id)
            output_json({"status": "completed", "comment_id": args.comment_id, "result": result})

        elif args.command == "complete-tasks":
            comment_ids = [int(cid.strip()) for cid in args.comment_ids.split(",")]
            results = client.complete_tasks(args.project, args.repo, args.pr_id, comment_ids)
            succeeded = sum(1 for r in results if r["success"])
            output_json({
                "status": "completed",
                "total": len(comment_ids),
                "succeeded": succeeded,
                "failed": len(comment_ids) - succeeded,
                "results": results
            })

        elif args.command == "reopen-task":
            result = client.reopen_task(args.project, args.repo, args.pr_id, args.comment_id)
            output_json({"status": "reopened", "comment_id": args.comment_id, "result": result})

        elif args.command == "reopen-tasks":
            comment_ids = [int(cid.strip()) for cid in args.comment_ids.split(",")]
            results = client.reopen_tasks(args.project, args.repo, args.pr_id, comment_ids)
            succeeded = sum(1 for r in results if r["success"])
            output_json({
                "status": "reopened",
                "total": len(comment_ids),
                "succeeded": succeeded,
                "failed": len(comment_ids) - succeeded,
                "results": results
            })

    except EnvironmentError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Network Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
