# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi[standard]",
#   "uvicorn",
# ]
# ///


from fastapi import FastAPI

app = FastAPI()

# post endpoint that receives a json object with following fields: email, secret, task, round, nonce,
# briefs, checks(array), evaluation_url, attachments(array with bobjects with url and name fields)

@app.post("/handle_task")
async def handle_task(data: dict):
    # just return the received data for now
    print(data)
    return {"message": "Task_received", "data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)