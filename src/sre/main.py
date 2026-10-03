from fastapi import FastAPI
from sre.copilot import investigate

app = FastAPI()

@app.post("/investigate")
def post_investigate(body: dict):
    return investigate(body)
