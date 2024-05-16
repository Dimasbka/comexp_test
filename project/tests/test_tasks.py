from worker import download_file_url, DOWNLOADS_DIR
from unittest.mock import patch

import json


def test_home(test_app):
    response = test_app.get("/")
    assert response.status_code == 200


TEST_URL = "https://i.ytimg.com/vi/G4MlZK8fd44/hq720.jpg"
TEST_RESULT = DOWNLOADS_DIR + "hq720.jpg"


@patch("worker.create_task.run")
def test_mock_task(mock_run):
    assert download_file_url.run(TEST_URL)
    download_file_url.run.assert_called_once_with(1)

    assert download_file_url.run(TEST_URL)
    assert download_file_url.run.call_count == 2

    assert download_file_url.run(TEST_URL)
    assert download_file_url.run.call_count == 3


def test_task_status(test_app):
    response = test_app.post("/download/file", data=json.dumps({"url": TEST_URL}))
    content = response.json()
    task_id = content["task_id"]
    assert task_id

    response = test_app.get(f"tasks/{task_id}")
    content = response.json()
    assert content == {
        "task_id": task_id,
        "task_status": "PENDING",
        "task_result": None,
    }
    assert response.status_code == 200

    while content["task_status"] == "PENDING":
        response = test_app.get(f"tasks/{task_id}")
        content = response.json()
    assert content == {
        "task_id": task_id,
        "task_status": "SUCCESS",
        "task_result": TEST_RESULT,
    }
