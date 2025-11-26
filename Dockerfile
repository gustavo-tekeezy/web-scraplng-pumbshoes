FROM python:3.10-slim

WORKDIR /workspace

# Install system deps
RUN apt-get update && apt-get install -y curl && apt-get clean

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

COPY . .

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
