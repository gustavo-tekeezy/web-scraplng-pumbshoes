FROM python:3.10-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y curl && apt-get clean

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright + deps
RUN pip install playwright
RUN playwright install --with-deps chromium

# Copiar tudo
COPY . .

EXPOSE 8000

# Comando da API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
