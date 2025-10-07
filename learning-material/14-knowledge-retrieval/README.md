# Pattern 14: Knowledge Retrieval (Search / RAG Hooks)

> "Route retrieval requests to external search and merge results into context"

Codex surfaces web search calls as explicit tool items and tracks begin/end via synthetic events.

Codex references:
- `codex-rs/core/src/client.rs` (detect `web_search_call`, emit `WebSearchCallBegin`)
- `codex-rs/core/src/codex.rs` (handle begin/end events)

## Example (Python)

```python
class Retriever:
    def search(self, query: str) -> list[str]:
        return [f"Result for {query}"]

def answer_with_retrieval(q: str, retriever: Retriever) -> str:
    hits = retriever.search(q)
    return f"Q: {q}\nSources: {hits}"
```
