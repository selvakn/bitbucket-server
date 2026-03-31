"""Integration tests for project and repository discovery commands."""


def test_list_projects(client):
    result = client.list_projects()

    assert isinstance(result, list)
    assert len(result) > 0, "Expected at least one project"
    for project in result:
        assert isinstance(project["key"], str)
        assert isinstance(project["name"], str)


def test_list_repositories(client, test_config):
    result = client.list_repositories(test_config["project_key"])

    assert isinstance(result, list)
    assert len(result) > 0, (
        f"Expected at least one repository in project {test_config['project_key']}"
    )
    for repo in result:
        assert isinstance(repo["slug"], str)
        assert isinstance(repo["name"], str)
        assert "key" in repo["project"]


def test_get_repository(client, test_config):
    result = client.get_repository(
        test_config["project_key"], test_config["repo_slug"]
    )

    assert isinstance(result, dict)
    assert result["slug"] == test_config["repo_slug"]
    assert isinstance(result["name"], str)
    assert "links" in result
    assert "defaultBranch" in result


def test_search_repositories(client, test_config):
    result = client.search_repositories(test_config["repo_slug"])

    assert isinstance(result, list)
    slugs = [repo["slug"] for repo in result]
    assert test_config["repo_slug"] in slugs, (
        f"Expected repo '{test_config['repo_slug']}' in search results, "
        f"got: {slugs}"
    )
