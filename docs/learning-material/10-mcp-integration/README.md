# Pattern 10: MCP Integration

> "Discover and call external tools via the Model Context Protocol"

Codex launches MCP servers (stdio/http), lists tools, and forwards tool calls.

Codex references:
- `codex-rs/mcp-client/src/mcp_client.rs`
- `codex-rs/core/src/tools/router.rs` (MCP routing)

## Example (Python, stub)

```python
class MCPClient:
    def __init__(self, server_cmd: list[str]):
        self.server_cmd = server_cmd
    def tools_list(self):
        return [{"name":"search","desc":"web search"}]
    def tools_call(self, name: str, args: dict):
        if name=="search":
            return ["result1","result2"]
        raise ValueError("unknown tool")
```
