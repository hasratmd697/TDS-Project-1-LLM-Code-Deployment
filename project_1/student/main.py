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
import time

import requests
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

GITHUB_TOKEN = os.getenv("GH_PERSONAL_ACCESS_TOKEN")
AIPIPE_API_KEY = os.getenv("AIPIPE_API_KEY")
SECRET = os.getenv("secret")
GITHUB_USERNAME = "hasratmd697"


# Debug prints
if GITHUB_TOKEN:
    print(f"✅ GITHUB_TOKEN loaded: {GITHUB_TOKEN[:10]}...")
else:
    print("❌ GITHUB_TOKEN not found!")

if AIPIPE_API_KEY:
    print(f"✅ AIPIPE_API_KEY loaded: {AIPIPE_API_KEY[:10]}...")
else:
    print("❌ AIPIPE_API_KEY not found!")

if SECRET:
    print(f"✅ SECRET loaded: {SECRET}")
else:
    print("❌ SECRET not found!")

app = FastAPI()


def validate_secret(secret: str) -> bool:
    """Validate the incoming secret against environment variable."""
    return secret == SECRET


def github_request(method: str, endpoint: str, **kwargs):
    """Generic GitHub API request handler."""
    headers = kwargs.pop("headers", {})
    headers.update({
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    response = requests.request(
        method, 
        f"https://api.github.com{endpoint}", 
        headers=headers, 
        **kwargs
    )
    if response.status_code not in [200, 201, 204]:
        print(f"GitHub API error: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API error: {response.status_code}, {response.text}")
    return response.json() if response.content else {}


def llm_generate(prompt: str) -> str:
    """Call AIPIPE API to generate content."""
    response = requests.post(
        "https://aipipe.org/openrouter/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {AIPIPE_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
        },
        timeout=120,
    )
    if response.status_code != 200:
        print(f"AIPIPE error: {response.status_code}, {response.text}")
        raise Exception(f"AIPIPE error: {response.status_code}, {response.text}")
    
    content = response.json().get("content", [{}])[0].get("text", "")
    # Strip markdown code blocks if present
    for lang in ["html", "markdown", ""]:
        marker = f"```{lang}"
        if marker in content:
            content = content.split(marker)[1].split("```")[0].strip()
            break
    return content


def create_repo_with_pages(repo_name: str, files: list[dict]):
    """Create repo, enable pages, and push files."""
    print(f"Creating repository: {repo_name}")
    
    # Create repo
    github_request("POST", "/user/repos", json={
        "name": repo_name,
        "private": False,
        "auto_init": True,
        "license_template": "mit",
    })
    
    # Enable GitHub Pages
    print("Enabling GitHub Pages...")
    time.sleep(3)  # Wait for repo initialization
    
    try:
        github_request("POST", f"/repos/{GITHUB_USERNAME}/{repo_name}/pages", json={
            "build_type": "legacy",
            "source": {"branch": "main", "path": "/"}
        })
    except Exception as e:
        print(f"Pages enable error (may already exist): {e}")
    
    # Push files
    print("Pushing files...")
    for file in files:
        content = file["content"]
        path = file["name"]
        
        # Base64 encode the content
        if isinstance(content, bytes):
            encoded = base64.b64encode(content).decode("utf-8")
        else:
            encoded = base64.b64encode(str(content).encode("utf-8")).decode("utf-8")
        
        # --- START: MODIFIED LOGIC ---
        
        # 1. Check if the file already exists to get its SHA
        current_sha = None
        try:
            file_data = github_request("GET", f"/repos/{GITHUB_USERNAME}/{repo_name}/contents/{path}")
            current_sha = file_data.get("sha")
        except Exception:
            # If it throws an error (like 404), the file doesn't exist. That's fine.
            print(f"File '{path}' not found. Creating it.")

        # 2. Build the payload, including the SHA if it exists
        payload = {
            "message": f"Add or update {path}",
            "content": encoded,
        }
        if current_sha:
            payload["sha"] = current_sha

        # 3. Make the request to create or update the file
        github_request("PUT", f"/repos/{GITHUB_USERNAME}/{repo_name}/contents/{path}", json=payload)
        
        # --- END: MODIFIED LOGIC ---
        
        print(f"Pushed: {path}")


def update_repo_files(repo_name: str, files: list[dict]):
    """Update existing files in repo."""
    print(f"Updating files in repository: {repo_name}")
    
    for file in files:
        try:
            # Get current file SHA
            file_data = github_request("GET", f"/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file['name']}")
            
            content = file["content"]
            encoded = base64.b64encode(str(content).encode("utf-8")).decode("utf-8")
            
            github_request("PUT", f"/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file['name']}", json={
                "message": f"Update {file['name']}",
                "content": encoded,
                "sha": file_data["sha"],
            })
            print(f"Updated: {file['name']}")
        except Exception as e:
            print(f"Error updating {file['name']}: {e}")
            raise


def generate_app_code(brief: str, checks: list[str], attachments: list[dict]) -> list[dict]:
    """Generate application code using LLM."""
    print("Generating application code...")
    
    attachments_info = "\n".join([f"- {a['name']}: {a['url'][:100]}..." for a in attachments]) if attachments else "None"
    
    html_code = llm_generate(f"""Create a complete, beautiful single-page HTML application.

Brief: {brief}

Requirements (must satisfy these checks):
{chr(10).join(f"- {c}" for c in checks)}

Attachments: {attachments_info}

Create a fully functional, responsive HTML page with:
- Tailwind CSS (via CDN: https://cdn.tailwindcss.com)
- Modern, beautiful design with animations
- All logic embedded in <script> tags
- Handle query parameters as specified
- Professional, polished UI

Return ONLY the complete HTML code, no explanations.""")
    
    readme = llm_generate(f"""Create a professional README.md for this project.

Brief: {brief}

Include:
1. Project title and brief description
2. Features list
3. Setup instructions
4. Usage guide with examples
5. Code structure explanation
6. License (MIT)

Keep it concise but professional. Return ONLY the README content.""")
    
    return [
        {"name": "index.html", "content": html_code},
        {"name": "README.md", "content": readme},
    ]


def update_app_code(repo_name: str, brief: str, checks: list[str]) -> list[dict]:
    """Update existing application code based on new requirements."""
    print("Updating application code...")
    
    # Get current files
    index_data = github_request("GET", f"/repos/{GITHUB_USERNAME}/{repo_name}/contents/index.html")
    readme_data = github_request("GET", f"/repos/{GITHUB_USERNAME}/{repo_name}/contents/README.md")
    
    current_html = base64.b64decode(index_data["content"]).decode("utf-8")
    current_readme = base64.b64decode(readme_data["content"]).decode("utf-8")
    
    updated_html = llm_generate(f"""Update this HTML application based on new requirements.

Current Code:
```html
{current_html[:2000]}...
```

New Requirements: {brief}

Checks to satisfy:
{chr(10).join(f"- {c}" for c in checks)}

Modify the code to meet the new requirements while maintaining quality and design.
Return ONLY the complete updated HTML code, no explanations.""")
    
    updated_readme = llm_generate(f"""Update this README.md for the modified application.

Current README:
{current_readme}

New Requirements: {brief}

Update the README to reflect the changes while maintaining professionalism.
Return ONLY the complete updated README, no explanations.""")
    
    return [
        {"name": "index.html", "content": updated_html},
        {"name": "README.md", "content": updated_readme},
    ]


def notify_evaluation(data: dict):
    """Send repo details to evaluation URL with retry logic."""
    print("Notifying evaluation endpoint...")
    
    # Get latest commit SHA
    commit_data = github_request("GET", f"/repos/{GITHUB_USERNAME}/{data['task']}_{data['nonce']}/commits/main")
    
    payload = {
        "email": data["email"],
        "task": data["task"],
        "round": data["round"],
        "nonce": data["nonce"],
        "repo_url": f"https://github.com/{GITHUB_USERNAME}/{data['task']}_{data['nonce']}",
        "commit_sha": commit_data["sha"],
        "pages_url": f"https://{GITHUB_USERNAME}.github.io/{data['task']}_{data['nonce']}/",
    }
    
    print(f"Payload: {payload}")
    
    for attempt, delay in enumerate([1, 2, 4, 8], 1):
        try:
            response = requests.post(
                data["evaluation_url"], 
                json=payload, 
                headers={"Content-Type": "application/json"}, 
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Notification successful on attempt {attempt}")
                return
            else:
                print(f"Attempt {attempt} failed: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Attempt {attempt} error: {e}")
        
        if attempt < 4:
            time.sleep(delay)
    
    print("❌ All notification attempts failed")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "running", "message": "Task handler is ready"}


@app.post("/handle_task")
async def handle_task(data: dict):
    """Main endpoint to handle task requests."""
    print(f"\n{'='*50}")
    print(f"Received task request")
    print(f"Task: {data.get('task', 'N/A')}")
    print(f"Round: {data.get('round', 'N/A')}")
    print(f"Nonce: {data.get('nonce', 'N/A')}")
    print(f"{'='*50}\n")
    
    # Validate secret (case-insensitive for 'secret' key)
    incoming_secret = data.get("secret") or data.get("SECRET")
    if not validate_secret(incoming_secret):
        print("❌ Invalid secret provided")
        return {"error": "Invalid secret"}
    
    repo_name = f"{data['task']}_{data['nonce']}"
    round_num = data["round"]
    
    try:
        if round_num == 1:
            files = generate_app_code(
                data["brief"], 
                data.get("checks", []), 
                data.get("attachments", [])
            )
            create_repo_with_pages(repo_name, files)
        elif round_num == 2:
            files = update_app_code(
                repo_name, 
                data["brief"], 
                data.get("checks", [])
            )
            update_repo_files(repo_name, files)
        else:
            return {"error": "Invalid round number. Must be 1 or 2."}
        
        # Wait for GitHub Pages to deploy
        time.sleep(5)
        
        # Notify evaluation endpoint
        notify_evaluation(data)
        
        print(f"✅ Round {round_num} completed successfully")
        return {
            "message": f"Round {round_num} completed successfully",
            "repo_url": f"https://github.com/{GITHUB_USERNAME}/{repo_name}",
            "pages_url": f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"
        }
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting FastAPI server...")
    print(f"Server will run on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)