# Adapted from se-toolkit-lab-8

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB:-}ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app/nanobot

# 1. Create venv first
RUN uv venv

# 2. Install dependencies (cached unless this line changes)
RUN uv pip install mcp websockets aiohttp \
    "nanobot-ai @ https://github.com/HKUDS/nanobot/archive/e7d371ec1e6531b28898ec2c869ef338e8dd46ec.zip"

# 3. Copy and install local packages
COPY --from=workspace /nanobot-websocket-channel/nanobot-channel-protocol /tmp/nanobot-channel-protocol
COPY --from=workspace /nanobot-websocket-channel/nanobot-webchat /tmp/nanobot-webchat
COPY --from=workspace /mcp/mcp-games /tmp/mcp-games

# Remove workspace source references
RUN sed -i '/\[tool.uv.sources\]/,/^\[/d' /tmp/nanobot-webchat/pyproject.toml && \
    sed -i '/\[tool.uv.sources\]/,/^\[/d' /tmp/mcp-games/pyproject.toml

RUN uv pip install /tmp/nanobot-channel-protocol /tmp/nanobot-webchat /tmp/mcp-games

# 4. Copy application files (config.json is generated from template)
COPY config.template.json pyproject.toml entrypoint.py ./
COPY workspace/ ./workspace/

# 5. Generate config.json and enable webchat
RUN cp config.template.json config.json && \
    python -c "import json; c=json.load(open('/app/nanobot/config.json')); c['channels']['webchat']={'enabled':True,'allowFrom':['*']}; json.dump(c,open('/app/nanobot/config.json','w'),indent=2)"

CMD ["python", "/app/nanobot/entrypoint.py"]
