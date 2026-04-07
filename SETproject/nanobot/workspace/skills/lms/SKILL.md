
---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

## LMS Assistant Skills

You have access to these LMS MCP tools:

| Tool | Description | Requires Lab? |
|------|-------------|---------------|
| `lms_health` | Check if LMS backend is healthy, report item count | No |
| `lms_labs` | List all available labs | No |
| `lms_learners` | List all registered learners | No |
| `lms_pass_rates` | Get pass rates (avg score, attempts) for a lab | Yes |
| `lms_timeline` | Get submission timeline (date + count) for a lab | Yes |
| `lms_groups` | Get group performance (avg score, student count) for a lab | Yes |
| `lms_top_learners` | Get top learners by average score for a lab | Yes |
| `lms_completion_rate` | Get completion rate (passed / total) for a lab | Yes |
| `lms_sync_pipeline` | Trigger the LMS sync pipeline | No |

## Strategy Rules

### 1. When user asks for lab-specific data WITHOUT naming a lab

If the user asks about **scores, pass rates, completion, groups, timeline, or top learners** without specifying a lab:

1. First call `lms_labs` to get available labs
2. If multiple labs exist, ask the user to choose one
3. Use each lab's title as the user-facing label
4. Let the shared structured-ui skill decide how to present the choice

**Example flow:**
User: “Show me the scores”
→ Call lms_labs
→ Present lab choices to user
→ User selects a lab
→ Call lms_pass_rates with selected lab


### 2. When user asks "what can you do?"

Explain your capabilities clearly:

> "I can query the LMS for:
> - Available labs and learners
> - Pass rates, completion rates, and scores for specific labs
> - Submission timelines and group performance
> - Top learners by average score
> 
> For detailed stats, I need you to specify which lab (e.g., 'lab-01', 'lab-08')."

### 3. Format numeric results

- **Percentages**: Show with % symbol, round to 1-2 decimals (e.g., "85.5%")
- **Counts**: Show as integers (e.g., "42 students")
- **Dates**: Use readable format (e.g., "2026-03-28")
- **Rates**: Show as fraction and percentage (e.g., "15/20 (75%)")

### 4. Keep responses concise

- Answer the question directly
- Don't dump raw JSON — summarize key insights
- Offer follow-up actions (e.g., "Would you like to see the timeline for this lab?")

### 5. Handle errors gracefully

- **Backend unavailable**: "The LMS backend is currently unavailable. Please try again later."
- **Lab not found**: "Lab '{name}' not found. Available labs: {list}"
- **No data**: "No data available for {metric} in {lab} yet."

### 6. Use structured UI when appropriate

When presenting choices (e.g., multiple labs), structure the output so the shared structured-ui skill can render interactive buttons on supported channels:

- Provide clear labels (use lab titles)
- Include lab identifiers as values
- Keep options under 10 if possible
