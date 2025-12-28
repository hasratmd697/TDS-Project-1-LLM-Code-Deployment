# Describe2Deploy

> 🚀 An automated tool that turns natural language descriptions into deployed web pages on GitHub Pages

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This project is a FastAPI server that accepts natural language descriptions of web pages, uses **GPT-4o-mini** (via AIPIPE) to generate complete HTML/CSS/JS code, and automatically deploys them to GitHub Pages.

**Workflow:** Describe what you want → AI generates code → Auto-deploys to GitHub Pages ⚡

## Features

- 🤖 **AI-Powered Generation** - GPT-4o-mini generates production-ready HTML applications
- 📦 **One-Click Deployment** - Automatic GitHub repo creation and Pages setup
- 🔄 **Iterative Updates** - Round 1 creates new apps, Round 2 updates existing ones
- 📝 **Auto Documentation** - Generates professional README for each deployed app
- 🎨 **Modern Design** - Uses Tailwind CSS for responsive, animated UIs
- 🔐 **Secure** - Secret-based authentication
- ♻️ **Retry Logic** - Robust error handling with exponential backoff

## Prerequisites

- Python 3.11+
- GitHub Personal Access Token ([Get one here](https://github.com/settings/tokens))
- AIPIPE API Key ([Sign up](https://aipipe.org))

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/hasratmd697/TDS-Project-1-LLM-Code-Deployment.git
cd TDS-Project-1-LLM-Code-Deployment

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
GH_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
AIPIPE_API_KEY=your_aipipe_key_here
secret=your_secret_phrase
```

### 3. Run Server

```bash
python main.py
```

Server starts at `http://localhost:8000` 🎉

## API Reference

### Health Check

```
GET /
```

Returns: `{"status": "running", "message": "Task handler is ready"}`

### Handle Task

```
POST /handle_task
```

**Request Body:**

| Field            | Type    | Description                             |
| ---------------- | ------- | --------------------------------------- |
| `email`          | string  | Your email address                      |
| `secret`         | string  | Must match `.env` secret                |
| `task`           | string  | Unique task identifier                  |
| `round`          | integer | `1` = create new, `2` = update existing |
| `nonce`          | string  | Unique nonce for the task               |
| `brief`          | string  | Natural language app description        |
| `checks`         | array   | Requirements the app must satisfy       |
| `evaluation_url` | string  | Callback URL for notification           |
| `attachments`    | array   | Optional file attachments               |

**Example Request:**

```bash
curl http://localhost:8000/handle_task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "secret": "your_secret",
    "task": "counter-app",
    "round": 1,
    "nonce": "abc123",
    "brief": "Create a counter app with increment and decrement buttons",
    "checks": ["Counter starts at 0", "Buttons work correctly"],
    "evaluation_url": "https://example.com/callback",
    "attachments": []
  }'
```

**Success Response:**

```json
{
  "message": "Round 1 completed successfully",
  "repo_url": "https://github.com/hasratmd697/counter-app_abc123",
  "pages_url": "https://hasratmd697.github.io/counter-app_abc123/"
}
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  POST Request   │────▶│  FastAPI Server  │────▶│  AIPIPE API     │
│  (task details) │     │  (main.py)       │     │  (GPT-4o-mini)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │                        │
                                ▼                        ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │  GitHub API      │◀────│  Generated Code │
                        │  (create repo)   │     │  (HTML/CSS/JS)  │
                        └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │  GitHub Pages    │
                        │  (live site)     │
                        └──────────────────┘
```

## Project Structure

```
TDS-Project-1-LLM-Code-Deployment/
├── main.py             # Core FastAPI application
├── .env                # Environment variables (git-ignored)
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── LICENSE             # MIT License
└── README.md           # This file
```

## Environment Variables

| Variable                   | Description                                        |
| -------------------------- | -------------------------------------------------- |
| `GH_PERSONAL_ACCESS_TOKEN` | GitHub PAT with `repo`, `workflow`, `pages` scopes |
| `AIPIPE_API_KEY`           | AIPIPE API key for LLM access                      |
| `secret`                   | Authentication secret for API requests             |

## Troubleshooting

| Error               | Solution                                |
| ------------------- | --------------------------------------- |
| `Invalid secret`    | Check `.env` secret matches request     |
| `GitHub API error`  | Verify token permissions and validity   |
| `AIPIPE error 402`  | Add credits to AIPIPE account           |
| `Pages not loading` | Wait 2-3 minutes for GitHub Pages build |

## Tech Stack

- **Backend:** FastAPI + Uvicorn
- **AI Model:** GPT-4o-mini via AIPIPE
- **Deployment:** GitHub Pages
- **Frontend:** HTML5 + Tailwind CSS

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

**Hasrat MD**

- GitHub: [@hasratmd697](https://github.com/hasratmd697)

---

<div align="center">

⭐ **Star this repo if you find it helpful!**

Made with ❤️ for TDS Project 1

</div>
