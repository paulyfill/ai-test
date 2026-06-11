FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ripgrep git curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir hermes-agent mcp

RUN mkdir -p /opt/hermes-defaults/skills
COPY config/config.yaml /opt/hermes-defaults/config.yaml
COPY skills/ /opt/hermes-defaults/skills/

RUN mkdir -p /root/.hermes

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
