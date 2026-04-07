#!/usr/bin/env python3
"""Resolve environment variables into config and launch nanobot gateway."""

import json
import os
from pathlib import Path


def main():
    config_path = Path("/app/nanobot/config.json")
    resolved_path = Path("/tmp/config.resolved.json")
    workspace_path = Path("/app/nanobot/workspace")

    with open(config_path) as f:
        config = json.load(f)

    # Override from environment
    if llm_key := os.environ.get("LLM_API_KEY"):
        config["providers"]["custom"]["apiKey"] = llm_key
    if llm_base := os.environ.get("LLM_API_BASE_URL"):
        config["providers"]["custom"]["apiBase"] = llm_base
    if llm_model := os.environ.get("LLM_API_MODEL"):
        config["agents"]["defaults"]["model"] = llm_model
    if gateway_host := os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS"):
        config["gateway"]["host"] = gateway_host
    if gateway_port := os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT"):
        config["gateway"]["port"] = int(gateway_port)

    # Replace LMS MCP with games MCP
    if "lms" in config.get("tools", {}).get("mcpServers", {}):
        del config["tools"]["mcpServers"]["lms"]
    if "obs" in config.get("tools", {}).get("mcpServers", {}):
        del config["tools"]["mcpServers"]["obs"]
    config["tools"]["mcpServers"]["games"] = {
        "command": "/app/nanobot/.venv/bin/python",
        "args": ["-m", "mcp_games"],
        "env": {
            "NANOBOT_LMS_BACKEND_URL": os.environ.get(
                "NANOBOT_LMS_BACKEND_URL", "http://backend:8000"
            )
        }
    }

    # Set venv Python for all MCP servers
    venv_python = "/app/nanobot/.venv/bin/python"
    for server_name in config.get("tools", {}).get("mcpServers", {}):
        config["tools"]["mcpServers"][server_name]["command"] = venv_python

    # Load skill prompt if exists
    skill_prompt_path = workspace_path / "skill_prompt.md"
    if skill_prompt_path.exists():
        config["agents"]["defaults"]["skill"] = skill_prompt_path.read_text()

    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    # Clear any existing cron jobs
    jobs_path = workspace_path / "jobs.json"
    jobs_path.write_text("[]")

    nanobot_bin = "/app/nanobot/.venv/bin/nanobot"
    os.execv(nanobot_bin, [nanobot_bin, "gateway", "--config", str(resolved_path), "--workspace", str(workspace_path)])


if __name__ == "__main__":
    main()
