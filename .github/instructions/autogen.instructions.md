---
applyTo: "**/autogen/**/*.py,**/multi_agent/**/*.py"
---

# Microsoft AutoGen Development Standards

## Agent Configuration

- Always set `max_consecutive_auto_reply` — unlimited auto-reply is a runaway cost risk
- Define explicit `is_termination_msg` functions — never rely on agents deciding to stop
- Set temperature to 0.0–0.3 for agents performing deterministic tasks (code, structured data)
- Use `human_input_mode="NEVER"` in production; use `"ALWAYS"` or `"TERMINATE"` in interactive flows

## Code Execution

- Always use Docker for code execution in production: `code_execution_config={"use_docker": True}`
- Never allow auto code execution without sandboxing
- Limit working directory to a scoped temp directory
- Validate all tool function signatures with Python type annotations

## GroupChat

- Define a clear `speaker_selection_method` — `"auto"` uses LLM routing; define custom logic for deterministic routing
- Set `max_round` on all GroupChats — default is unlimited (cost risk)
- Keep GroupChat agent count to the minimum needed — every extra agent adds routing complexity and cost

## Security

- Never hardcode API keys — read from environment variables only
- Validate all external tool calls before execution
- Log every agent message exchange with sender and token count for cost tracking

## LLM Config

```python
config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
llm_config = {
    "config_list": config_list,
    "temperature": 0.1,
    "max_tokens": 2000,
    "timeout": 60,
}
```

- Always set `timeout` to prevent blocking on slow model responses
- Always set `max_tokens` — unbounded generation is a cost risk
