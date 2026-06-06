# MCP Server Development Workflow

Design and implement a Model Context Protocol (MCP) server to expose the following capabilities.

**Server Purpose:** $SERVER_PURPOSE
**Target Integration:** Claude Code / other MCP host

## Workflow Steps

### Step 1 — Capability Design
Before writing code, design what the server exposes:
- [ ] List each tool with: name, purpose, inputs, outputs
- [ ] List each resource with: URI pattern, content type, update frequency
- [ ] Identify any prompt templates to expose
- [ ] Determine transport: stdio (local) or SSE (HTTP)

### Step 2 — Security Assessment
For each tool and resource:
- [ ] Does it access the file system? → Need path validation
- [ ] Does it call external APIs? → Need rate limiting and timeout
- [ ] Does it access a database? → Need parameterised queries
- [ ] Does it handle PII? → Need data classification review

### Step 3 — Tool Schema Design
For each tool, write the complete JSON Schema:
- [ ] All properties have `description` fields
- [ ] All required properties are listed in `required`
- [ ] Enum values documented where applicable
- [ ] Tool `description` explains WHEN to use the tool (not just what it does)

### Step 4 — Implementation
Activate the `mcp-engineer` agent to produce:
- [ ] Complete Python or TypeScript server implementation
- [ ] Input validation for all tool calls
- [ ] Structured error responses (not exceptions)
- [ ] Logging for all tool invocations

### Step 5 — Integration
- [ ] Produce `mcp.json` configuration for Claude Code
- [ ] Test all tools with representative inputs
- [ ] Verify error handling with invalid inputs
- [ ] Confirm sensitive data does not appear in logs

### Step 6 — Documentation
- [ ] Tool catalogue: name, purpose, example inputs, example outputs
- [ ] Setup guide for the MCP server
- [ ] Authentication setup guide (if HTTP-based)

## Output

Complete MCP server implementation, `mcp.json` configuration, tool catalogue, and setup documentation.
