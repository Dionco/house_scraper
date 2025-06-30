from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from typing import List

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE = "listing_database.jsonl"

@app.get("/api/listings")
def get_listings() -> List[dict]:
    listings = []
    if os.path.exists(DATABASE):
        with open(DATABASE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        listings.append(json.loads(line))
                    except Exception:
                        pass
    return listings

# This file is not imported by any main code. Move to deprecated/ if not needed.
