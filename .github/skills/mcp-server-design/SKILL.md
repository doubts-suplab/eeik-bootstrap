# MCP Server Design Skill

## Trigger

Use this skill when designing or implementing Model Context Protocol (MCP) servers that expose tools, resources, or prompt templates to LLM hosts.

## What This Skill Does

1. Designs the tool catalogue: what tools the server exposes and their JSON Schema definitions
2. Implements the MCP server in Python or TypeScript using the official SDK
3. Configures transport: stdio (local process) or SSE (HTTP-based)
4. Produces the `mcp.json` configuration for Claude Code integration
5. Implements security controls: input validation, path sanitisation, rate limiting
6. Documents error codes and handling

## Inputs Required

- Description of what the MCP server should expose (tools, resources, or prompts)
- The external system being integrated (database, API, file system, etc.)
- Target transport: stdio or HTTP/SSE
- Authentication requirements (if HTTP-based)
- Any sensitive data or operations that require extra care

## Outputs Produced

- Complete Python or TypeScript MCP server implementation
- JSON Schema definitions for all tools
- `mcp.json` configuration snippet for Claude Code
- Tool description guide (how to write descriptions that LLMs use correctly)
- Security checklist for the server

## Tool Quality Criteria

Good MCP tool definitions:
- Have a description that explains WHEN to use the tool (not just what it does)
- Have complete JSON Schema with descriptions on all properties
- Return structured, parseable output
- Handle errors as structured responses, not exceptions

## Standards Applied

See `.github/instructions/mcp-protocol.instructions.md`

## Related Agents

- `mcp-engineer` — Claude Code agent for MCP server implementation
- `a2a-engineer` — for multi-agent communication using MCP
- `ai-engineer` — for LLM applications that consume MCP tools
