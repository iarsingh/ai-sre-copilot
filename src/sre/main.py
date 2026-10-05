from sre.ops import router as ops_router
from fastapi import FastAPI
from sre.copilot import investigate

app = FastAPI()
app.include_router(ops_router, prefix="/v1")

@app.post("/investigate")
def post_investigate(body: dict):
    return investigate(body)
