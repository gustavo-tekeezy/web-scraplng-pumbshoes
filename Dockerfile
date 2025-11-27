FROM python:3.10-slim

WORKDIR /app

# Instala dependências de sistema
RUN apt-get update && apt-get install -y curl && apt-get clean

# Instala dependências do Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Instala o Playwright (necessário para scrapy-playwright)
RUN playwright install --with-deps chromium

# Copia todo o código para dentro do container
COPY . /app

# Porta usada pelo uvicorn (FastAPI)
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
