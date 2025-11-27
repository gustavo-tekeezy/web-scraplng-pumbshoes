from fastapi import FastAPI
import subprocess
import json
import uuid
import os

app = FastAPI()

# Caminho do projeto SCRAPY (onde está scrapy.cfg)
SCRAPY_PROJECT_DIR = "/workspace/shopbot"

def run_scrapy(spider_name: str, args: dict):
    # Gera nome único para o arquivo
    file = f"output_{uuid.uuid4().hex}.json"
    file_path = os.path.join(SCRAPY_PROJECT_DIR, file)

    # Comando para executar scrapy
    command = [
        "scrapy", "crawl", spider_name,
        "-o", file
    ]

    # Adiciona argumentos -a
    for k, v in args.items():
        command += ["-a", f"{k}={v}"]

    # Executa scrapy
    process = subprocess.run(
        command,
        cwd=SCRAPY_PROJECT_DIR,
        capture_output=True,
        text=True
    )

    # Se scrapy falhou
    if process.returncode != 0:
        return {"error": "scrapy_failed", "details": process.stderr}

    # Verifica se o arquivo foi gerado
    if not os.path.exists(file_path):
        return {"error": "file_not_found", "path": file_path}

    # Lê o JSON gerado
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Remove o arquivo após leitura
    os.remove(file_path)

    return data


# =====================================================================
# ENDPOINTS
# =====================================================================

# 🟦 1) BUSCA DE PRODUTOS /pumb?q=
@app.get("/pumb")
def scrape_pumb(q: str):
    return run_scrapy("pumb", {"query": q})


# 🟧 2) DETALHES DO PRODUTO /product?url=
@app.get("/product")
def scrape_product(url: str):
    return run_scrapy("product_details", {"url": url})
