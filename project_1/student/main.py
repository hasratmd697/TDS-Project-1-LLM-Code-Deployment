# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi[standard]",
#   "uvicorn",
#   "requests",
# ]
# ///

from importlib.resources import files
from wsgiref import headers
import requests
import os
import base64
from fastapi import FastAPI
from dotenv import load_dotenv 

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def validate_secret(secret: str) -> bool:
    # Placeholder for secret validation logic
    return secret == os.getenv("secret")

def create_github_repo(repo_name: str):
    # use github api to create a repo using given name
    payload = {
        "name": repo_name,
        "private": False,
        "auto_init": True,
        "license_template": "mit",
    }

    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}",
               "Accept": "application/vnd.github.v3+json"}
    
    response = requests.post(
        "https://api.github.com/user/repos",
        json=payload,
        headers=headers
    )
    if response.status_code != 201:
        raise Exception(f"Failed to create repository: {response.status_code}, {response.text}")
    else:
        return response.json()


def enable_github_pages(repo_name: str):
    # takes repo name as argument and enables github pages using github api
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",   
        "Accept": "application/vnd.github+json"}
    
    payload = {
        "build_type": "legacy",
        "source": {"branch": "main", "path": "/"}
    }
    response = requests.post(
        f"https://api.github.com/repos/hasratmd697/{repo_name}/pages",
        headers=headers, json=payload
    )
    if response.status_code != 201:
        raise Exception(f"Failed to enable GitHub Pages: {response.status_code}, {response.text}")

def get_sha_of_latest_commit(repo_name: str, branch: str = "main") -> str:
    # takes repo name and branch name as argument and returns sha of latest commit on that branch using github api

    response = requests.get(f"https://api.github.com/repos/hasratmd697/{repo_name}/commits/{branch}")
    if response.status_code != 200:
        raise Exception(f"Failed to get latest commit SHA: {response.status_code}, {response.text}")
    return response.json().get("sha")


def push_files_to_repo(repo_name: str, files: list[dict], round: int):
    # takes a repo name and json array with object that have fields name of the file and content of the file 
    # and use github api to push the files to the repo
    if round == 2:
        latest_sha = get_sha_of_latest_commit(repo_name)
    else:
        latest_sha = None
        
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    for file in files:
        file_name = file.get("name")
        file_content = file.get("content")
        # if the content is bytes, convert it to base64 string
        if isinstance(file_content, bytes):
            file_content = base64.b64encode(file_content).decode("utf-8")
        else:
            # if the content is string, still encode to base64
            file_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")
        payload = {
                "message": f"Add {file_name}",
                "content": file_content
            }
        if latest_sha:
            payload["sha"] = latest_sha
        # create a new file in the repo
        response = requests.put(
            f"https://api.github.com/repos/hasratmd697/{repo_name}/contents/{file_name}",
            headers=headers,
            json=payload
        )
        if response.status_code != 201:
            raise Exception(f"Failed to push file {file_name}: {response.status_code}, {response.text}")

def write_code_with_llm():
    # hardcode with a single file now
    # TODO: integrate with LLM to generate code
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
</html>"""
        }
    ]


def round1(data):
    write_code_with_llm()
    files = write_code_with_llm()
    #create_github_repo(f"{data['task']}_{data['nonce']}")
    #enable_github_pages(f"{data['task']}_{data['nonce']}")
    push_files_to_repo(f"{data['task']}_{data['nonce']}", files, 1)
    
    
def round2(data):
    pass

app = FastAPI()

# post endpoint that receives a json object with following fields: email, secret, task, round, nonce,
# briefs, checks(array), evaluation_url, attachments(array with bobjects with url and name fields)

@app.post("/handle_task")
async def handle_task(data: dict):
    # validate the secret
    if not validate_secret(data.get("secret", "")):
        return {"error": "Invalid secret"}
    else:
        # process the task
        # depending on the round, call different functions
        if data.get("round") == 1:
            round1(data)
            return {"message": "Round 1 task processing started"}
        elif data.get("round") == 2:
            round2(data)
            return {"message": "Round 2 task processing started"}
        else:
            return {"error": "Invalid round"}
        
    return {"message": "Task_received", "data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)