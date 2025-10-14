# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi[standard]",
#   "uvicorn",
#   "requests",
# ]
# ///

import requests
import os
from fastapi import FastAPI
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

def enable_github_pages():
    pass

def deploy_github_pages():
    pass

def push_code_to_repo():
    pass

def write_code_with_llm():
    pass

def round1(data):
    write_code_with_llm()
    create_github_repo(f"{data['task']}_{data['nonce']}")
    enable_github_pages()
    deploy_github_pages()
    push_code_to_repo()
    
    
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