from fastapi import FastAPI
import subprocess
import json
import uuid
import os

app = FastAPI()

# Caminho do projeto SCRAPY (corrigido para /app)
SCRAPY_PROJECT_DIR = "/app/shopbot"

def run_scrapy(spider_name: str, args: dict):
    file = f"output_{uuid.uuid4().hex}.json"
    file_path = os.path.join(SCRAPY_PROJECT_DIR, file)

    command = [
        "scrapy", "crawl", spider_name,
        "-o", file
    ]

    for k, v in args.items():
        command += ["-a", f"{k}={v}"]

    process = subprocess.run(
        command,
        cwd=SCRAPY_PROJECT_DIR,
        capture_output=True,
        text=True
    )

    if process.returncode != 0:
        return {"error": "scrapy_failed", "details": process.stderr}

    if not os.path.exists(file_path):
        return {"error": "file_not_found", "path": file_path}

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.remove(file_path)

    return data


# Endpoints ===================================================================

@app.get("/pumb")
def scrape_pumb(q: str):
    return run_scrapy("pumb", {"query": q})

@app.get("/product")
def scrape_product(url: str):
    return run_scrapy("product_details", {"url": url})
