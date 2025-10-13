"""
Minimal Python entry point.
"""
#TODO: Database Entry Point#
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

if __name__ == "__main__":
    print("App started")
    uvicorn.run(app, host="0.0.0.0", port=8000)
