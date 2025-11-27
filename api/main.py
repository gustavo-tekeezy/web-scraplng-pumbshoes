from fastapi import FastAPI
from fastapi.responses import JSONResponse
import subprocess
import json
import redis
import hashlib
import uuid
import os

app = FastAPI()

# Lê variáveis do ambiente (produção usa essas)
REDIS_HOST = os.getenv("REDIS_HOST", "redis-cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)

CACHE_TTL = 1800  # 30 minutos


def run_scrapy(query: str):
    temp_file = f"/tmp/{uuid.uuid4()}.json"

    cmd = [
        "scrapy",
        "crawl",
        "pumb",
        "-a", f"query={query}",
        "-O", temp_file
    ]

    result = subprocess.run(
        cmd,
        cwd="/app",
        capture_output=True,
        text=True
    )

    print("\n=== SCRAPY STDOUT ===\n", result.stdout)
    print("\n=== SCRAPY STDERR ===\n", result.stderr)

    if not os.path.exists(temp_file):
        print("Arquivo não encontrado:", temp_file)
        return []

    try:
        with open(temp_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

    try:
        os.remove(temp_file)
    except:
        pass

    return data


@app.get("/pumb")
def pumb_search(q: str):
    cache_key = f"pumb:{hashlib.md5(q.encode()).hexdigest()}"

    cached = r.get(cache_key)
    if cached:
        return JSONResponse(content=json.loads(cached))

    data = run_scrapy(q)

    r.set(cache_key, json.dumps(data), ex=CACHE_TTL)

    return JSONResponse(content=data)
