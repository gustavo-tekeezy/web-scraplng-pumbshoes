from fastapi import FastAPI
from fastapi.responses import JSONResponse
import subprocess
import json
import redis
import hashlib
import uuid
import os

app = FastAPI()

# Redis local via docker compose
r = redis.Redis(
    host="redis-cache",
    port=6379,
    db=0,
    decode_responses=True
)

CACHE_TTL = 1800  # 30 minutos


def run_scrapy(query: str):
    """Executa o Scrapy gerando JSONL e converte para lista."""
    temp_file = f"/tmp/{uuid.uuid4()}.jsonl"

    cmd = [
        "scrapy",
        "crawl",
        "pumb",
        "-a", f"query={query}",
        "-o", f"{temp_file}:jsonlines"
    ]

    result = subprocess.run(
        cmd,
        cwd="/app",
        capture_output=True,
        text=True
    )

    print("\n=== SCRAPY STDOUT ===\n", result.stdout)
    print("\n=== SCRAPY STDERR ===\n", result.stderr)

    # Se o arquivo não existir, retorna vazio
    if not os.path.exists(temp_file):
        print("Arquivo JSONL não encontrado:", temp_file)
        return []

    # Converte JSONL para lista
    data = []
    try:
        with open(temp_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data.append(json.loads(line.strip()))
                except:
                    pass
    except:
        data = []

    # Remove o arquivo temporário
    try:
        os.remove(temp_file)
    except:
        pass

    return data


@app.get("/pumb")
def pumb_search(q: str):
    cache_key = f"pumb:{hashlib.md5(q.encode()).hexdigest()}"

    # 1. Cache
    cached = r.get(cache_key)
    if cached:
        return JSONResponse(content=json.loads(cached))

    # 2. Scrapy
    data = run_scrapy(q)

    # 3. Salva no cache
    r.set(cache_key, json.dumps(data), ex=CACHE_TTL)

    return JSONResponse(content=data)
