import os
import sys

import pytest
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from bitbucket_api import BitBucketClient


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(scope="session")
def client():
    return BitBucketClient()


@pytest.fixture(scope="session")
def test_config():
    config = {
        "project_key": os.environ.get("TEST_PROJECT_KEY"),
        "repo_slug": os.environ.get("TEST_REPO_SLUG"),
        "pr_id": os.environ.get("TEST_PR_ID"),
    }
    missing = [k for k, v in config.items() if not v]
    if missing:
        pytest.skip(
            f"Missing test configuration env vars: {', '.join(missing)}. "
            "Set TEST_PROJECT_KEY, TEST_REPO_SLUG, TEST_PR_ID in .env"
        )
    config["pr_id"] = int(config["pr_id"])
    return config
