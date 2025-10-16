# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi[standard]",
#   "uvicorn",
#   "requests",
#   "python-dotenv"
# ]
# ///

import base64
import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if GITHUB_TOKEN:
    print(f"✅ Token loaded successfully. Starts with: {GITHUB_TOKEN[:4]}, Ends with: {GITHUB_TOKEN[-4:]}")
else:
    print("❌ ERROR: GITHUB_TOKEN not found in environment!")


def validate_secret(secret: str) -> bool:
    """Placeholder for secret validation logic."""
    return secret == os.getenv("secret")


def create_github_repo(repo_name: str):
    """Uses the GitHub API to create a repo with the given name."""
    payload = {
        "name": repo_name,
        "private": False,
        "auto_init": True,
        "license_template": "mit",
    }

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.post("https://api.github.com/user/repos", json=payload, headers=headers)
    if response.status_code != 201:
        raise Exception(
            f"Failed to create repository: {response.status_code}, {response.text}"
        )
    else:
        return response.json()


def enable_github_pages(repo_name: str):
    """Takes a repo name and enables GitHub Pages using the GitHub API."""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    payload = {"build_type": "legacy", "source": {"branch": "main", "path": "/"}}
    response = requests.post(
        f"https://api.github.com/repos/hasratmd697/{repo_name}/pages",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            f"Failed to enable GitHub Pages: {response.status_code}, {response.text}"
        )


def get_sha_of_latest_commit(repo_name: str, branch: str = "main") -> str:
    """Takes repo and branch names and returns the SHA of the latest commit."""
    response = requests.get(
        f"https://api.github.com/repos/hasratmd697/{repo_name}/commits/{branch}"
    )
    if response.status_code != 200:
        raise Exception(
            f"Failed to get latest commit SHA: {response.status_code}, {response.text}"
        )
    return response.json().get("sha")


def push_files_to_repo(repo_name: str, files: list[dict], round_num: int):
    """
    Creates or updates files in a GitHub repository using the API.

    Each file in the list should be a dictionary with 'name' and 'content' keys.
    """
    latest_sha = None
    if round_num == 2:
        # To update a file, you need the file's specific blob SHA, not the commit SHA.
        # This part might need adjustment depending on the exact update logic.
        # latest_sha = get_sha_of_latest_commit(repo_name)
        pass

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    for file_item in files:
        file_name = file_item.get("name")
        file_content = file_item.get("content")

        if file_content is None:
            encoded_content = base64.b64encode(b"").decode("utf-8")
        elif isinstance(file_content, bytes):
            encoded_content = base64.b64encode(file_content).decode("utf-8")
        else:
            encoded_content = base64.b64encode(str(file_content).encode("utf-8")).decode(
                "utf-8"
            )

        payload = {"message": f"Add {file_name}", "content": encoded_content}

        if latest_sha:
            payload["sha"] = latest_sha

        response = requests.put(
            f"https://api.github.com/repos/hasratmd697/{repo_name}/contents/{file_name}",
            headers=headers,
            json=payload,
        )

        # 201 for creation, 200 for update.
        if response.status_code not in [200, 201]:
            raise Exception(
                f"Failed to push file {file_name}: {response.status_code}, {response.text}"
            )


def write_code_with_llm():
    """Generates file content, currently hardcoded."""
    # TODO: Integrate with an LLM to generate code dynamically.
    return [
        {
            "name": "index.html",
            "content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hello World</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    body {
        font-family: 'Inter', sans-serif;
    }
</style>
</head>
<body class="bg-gray-100 flex items-center justify-center h-screen">
    <div class="text-center">
        <h1 class="text-5xl font-bold text-gray-800">
            Hello World
        </h1>
        <p class="mt-4 text-lg text-gray-600">
            This is a simple HTML page.
        </p>
    </div>
</body>
</html>""",
        }
    ]


def round1(data):
    """Handles the first round of task processing."""
    repo_name = f"{data['task']}_{data['nonce']}"
    files = write_code_with_llm()
    create_github_repo(repo_name)
    enable_github_pages(repo_name)
    push_files_to_repo(repo_name, files, 1)


def round2(data):
    """Handles the second round of task processing."""
    pass


app = FastAPI()


@app.post("/handle_task")
async def handle_task(data: dict):
    """
    Receives a task and processes it based on the specified round.
    """
    if not validate_secret(data.get("secret", "")):
        return {"error": "Invalid secret"}

    round_num = data.get("round")
    if round_num == 1:
        round1(data)
        return {"message": "Round 1 task processing started"}
    elif round_num == 2:
        round2(data)
        return {"message": "Round 2 task processing started"}
    else:
        return {"error": "Invalid round"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)