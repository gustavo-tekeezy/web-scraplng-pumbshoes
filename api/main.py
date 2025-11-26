from fastapi import FastAPI
import subprocess
import json
import uuid
import os

app = FastAPI()

@app.get("/pumb")
def scrape_pumb(q: str):

    file = f"/workspace/output_{uuid.uuid4().hex}.json"

    command = [
        "scrapy", "crawl", "pumb",
        "-a", f"query={q}",
        "-o", file
    ]

    subprocess.run(command, capture_output=True, text=True)

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.remove(file)  # limpa após uso

    return data
