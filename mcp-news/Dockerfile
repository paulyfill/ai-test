FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN python -m venv .venv && \
    .venv/bin/pip install --no-cache-dir -r requirements.txt

COPY server.py .

CMD [".venv/bin/python", "server.py"]
