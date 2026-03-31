"""Integration tests for pull request read commands."""


def test_list_pull_requests(client, test_config):
    result = client.list_pull_requests(
        test_config["project_key"], test_config["repo_slug"], state="ALL"
    )

    assert isinstance(result, list)
    for pr in result:
        assert isinstance(pr["id"], int)
        assert isinstance(pr["title"], str)
        assert isinstance(pr["state"], str)


def test_get_pull_request(client, test_config):
    result = client.get_pull_request(
        test_config["project_key"], test_config["repo_slug"], test_config["pr_id"]
    )

    assert isinstance(result, dict)
    assert result["id"] == test_config["pr_id"]
    assert isinstance(result["title"], str)
    assert isinstance(result["state"], str)
    assert "author" in result
    assert "fromRef" in result
    assert "toRef" in result


def test_get_diff(client, test_config):
    result = client.get_diff(
        test_config["project_key"], test_config["repo_slug"], test_config["pr_id"]
    )

    assert isinstance(result, dict)
    assert "diffs" in result
    assert isinstance(result["diffs"], list)


def test_get_comments(client, test_config):
    result = client.get_comments(
        test_config["project_key"], test_config["repo_slug"], test_config["pr_id"]
    )

    assert isinstance(result, list)
    for comment in result:
        assert isinstance(comment["id"], int)
        assert isinstance(comment["text"], str)
        assert isinstance(comment["author"], str)


def test_get_tasks(client, test_config):
    result = client.get_tasks(
        test_config["project_key"], test_config["repo_slug"], test_config["pr_id"]
    )

    assert isinstance(result, list)
    for task in result:
        assert isinstance(task["id"], int)
        assert isinstance(task["text"], str)
        assert isinstance(task["state"], str)
