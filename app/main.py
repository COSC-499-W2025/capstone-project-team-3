"""
Minimal Python entry point.
"""
from fastapi import FastAPI
from app.data.db import init_db, seed_db
import uvicorn

# Database Entry Point#
def main():
    init_db()  # creates the SQLite DB + tables
    seed_db()  # automatically populate test data
    print("Database started")

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

if __name__ == "__main__":
    main()
    print("App started")
    uvicorn.run(app, host="0.0.0.0", port=8000)
