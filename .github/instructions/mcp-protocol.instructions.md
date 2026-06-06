---
applyTo: "**/mcp/**/*.py,**/mcp/**/*.ts,**/mcp_server/**/*.py,**/.mcp/**"
---

# Model Context Protocol (MCP) Development Standards

## Tool Design

- Write complete JSON Schema definitions for all tool `inputSchema` — incomplete schemas cause LLM tool misuse
- Tool descriptions must explain: what the tool does, when to use it, and what it returns
- Every tool must handle invalid input gracefully — return an error string, not raise an unhandled exception
- Mark non-idempotent tools (those that cause side effects) explicitly in their description
- Limit tool scope to the minimum necessary — one tool per logical operation

## Resource Design

- Resource URIs must be stable and predictable — avoid timestamp or random-component URIs
- Always include `mimeType` on resource responses
- Implement resource listing (`list_resources`) alongside `read_resource`

## Server Implementation

- Use official `mcp` SDK (`pip install mcp` / `npm install @modelcontextprotocol/sdk`)
- Implement graceful shutdown handlers
- Log all tool invocations with tool name, input hash, and response time (not full input content if PII risk)
- Version your MCP server — include version in the server name or capabilities

## Security

- Validate all file path inputs — never allow path traversal (`../`) in file-reading tools
- Implement authentication for HTTP-based (SSE) MCP servers
- Rate limit expensive or external-API-calling tools
- Never expose credentials in tool schemas, descriptions, or error messages

## mcp.json Configuration

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["-m", "my_mcp_server"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

- Always inject secrets via environment variables — never hardcode in `mcp.json`
- Pin the server command to a specific executable path or virtual environment in production
