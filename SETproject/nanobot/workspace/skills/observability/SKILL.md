---
name: observability
description: Use VictoriaLogs and VictoriaTraces for system observability
always: true
---

# Observability Skill

You have access to observability tools for querying logs and traces:

## Available Tools

### Log Tools (VictoriaLogs)
- `logs_search(query, time_range, limit)` — Search logs using LogsQL
- `logs_error_count(time_range, group_by)` — Count errors per service

### Trace Tools (VictoriaTraces)
- `traces_list(service, limit)` — List recent traces for a service
- `traces_get(trace_id)` — Fetch full trace by ID

## Strategy

### When user asks about errors or problems:

1. **Start with `logs_error_count`** — Get an overview of errors by service in the specified time window

2. **Use `logs_search` for details** — If errors are found, search for specific error logs:
   - Filter by service: `service.name:"Learning Management Service"`
   - Filter by severity: `severity:ERROR`
   - Extract `trace_id` from log entries if present

3. **Fetch the trace if available** — If you found a `trace_id` in logs, use `traces_get` to see the full request flow

4. **Summarize findings** — Provide a concise summary:
   - How many errors occurred
   - Which services were affected
   - What the error was (from logs)
   - Where in the request flow it happened (from traces)

### Example queries:

- "Any errors in the last hour?" → `logs_error_count(time_range="1h")`
- "Show me backend errors" → `logs_search(query='service.name:"backend" severity:ERROR')`
- "What happened in trace XYZ?" → `traces_get(trace_id="XYZ")`

### Important notes:

- Time ranges: use '10m', '1h', '1d' format
- Service names: "Learning Management Service", "qwen-code-api", "backend"
- Always prefer recent time windows (10m-1h) unless user specifies otherwise
- Don't dump raw JSON — summarize the key findings
- If no errors found, say so clearly

### For LMS backend specifically:

When asked about LMS errors, use:
- `service.name:"Learning Management Service"` in logs_search
- Narrow time range: "10m" for recent issues
