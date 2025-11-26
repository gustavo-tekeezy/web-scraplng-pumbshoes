FROM python:3.10

# Dependências do Playwright
RUN apt-get update && apt-get install -y \
    wget curl git \
    && apt-get clean

# Instala pip
RUN pip install --upgrade pip

# Instala scrapy + scrapy-playwright
RUN pip install scrapy scrapy-playwright

# Instala Jupyter
RUN pip install jupyterlab ipykernel

# Instala navegadores Playwright
RUN playwright install --with-deps chromium

WORKDIR /workspace
