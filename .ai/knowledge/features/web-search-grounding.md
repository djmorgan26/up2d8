---
type: feature
name: Web Search Grounding for AI Chat
status: implemented
created: 2025-11-09
updated: 2025-11-09
files:
  - packages/backend-api/api/chat.py:26-120
  - packages/backend-api/requirements.txt:4
  - packages/web-app/src/pages/Chat.tsx:54-56
related:
  - ./ai-chat-integration.md
  - ../patterns/google-genai-migration.md
tags: [ai, chat, web-search, grounding, google-gemini, real-time-data]
---

# Web Search Grounding for AI Chat

## What It Does
Enables the AI chatbot to search the web in real-time using Google Search and provide up-to-date information with source citations. Users can ask about current events, latest news, stock prices, weather, or any real-time information, and the AI will ground its responses with web search results.

## How It Works
The feature uses Google's Generative AI (GenAI) SDK with the Google Search tool to enable grounding:

**Key files:**
- `packages/backend-api/api/chat.py:26-120` - Chat endpoint with web search grounding
- `packages/backend-api/api/chat.py:80-114` - Source extraction from grounding metadata
- `packages/web-app/src/pages/Chat.tsx:54-56` - Frontend handles `reply` or `text` fields

### Architecture

```
User Query → Backend API → Google GenAI Client → Gemini 2.5 Flash + Google Search
                                                        ↓
                                                  Web Search Results
                                                        ↓
                                                  Grounding Metadata
                                                        ↓
              ← Response with sources ← Extract sources from candidates[0]
```

### API Request/Response Format

**Request:**
```json
POST /api/chat
{
  "prompt": "What is the current Bitcoin price?"
}
```

**Response:**
```json
{
  "status": "success",
  "model": "gemini-2.5-flash",
  "reply": "The current Bitcoin price is approximately $103,557 USD...",
  "sources": [
    {
      "web": {
        "uri": "https://...",
        "title": "CoinMarketCap"
      }
    }
  ]
}
```

### Implementation Details

1. **Library**: Uses `google-genai` (not the deprecated `google-generativeai`)
2. **Tool Configuration**: `types.Tool(google_search=types.GoogleSearch())`
3. **Source Extraction**: Sources are in `response.candidates[0].grounding_metadata.grounding_chunks`
4. **System Instructions**: Custom prompt for UP2D8 assistant behavior

## Important Decisions

- **google-genai vs google-generativeai**: Migrated to the new `google-genai` library because:
  - `google-generativeai` is deprecated (support ends Aug 31, 2025)
  - Only the new library properly supports Google Search grounding for Gemini 2.0+
  - Better API structure with `response.candidates[0]` pattern

- **Source Extraction Strategy**: Extract from `grounding_chunks` because:
  - Contains actual web sources with URIs and titles
  - Each chunk represents a grounded piece of information
  - Provides direct citations users can verify

- **Response Format**: Standardized with `status`, `model`, `reply`, `sources` fields for:
  - Predictable frontend parsing
  - Clear success/failure indication
  - Model tracking capability
  - Source citation support

## Usage Example

```python
# Backend (chat.py)
from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    tools=[types.Tool(google_search=types.GoogleSearch())]
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=request.prompt,
    config=config
)

# Extract sources from candidates[0].grounding_metadata
sources = []
if response.candidates and len(response.candidates) > 0:
    metadata = response.candidates[0].grounding_metadata
    if metadata and metadata.grounding_chunks:
        for chunk in metadata.grounding_chunks:
            if chunk.web:
                sources.append({
                    "web": {
                        "uri": chunk.web.uri,
                        "title": chunk.web.title
                    }
                })
```

```typescript
// Frontend (Chat.tsx)
const data = await response.json();
const assistantMessage = {
  role: "assistant",
  content: data.reply || data.text // Backward compatible
};
```

## Testing

**Test with real-time queries:**
```bash
# Bitcoin price (real-time financial data)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the current Bitcoin price?"}'

# Weather (real-time location data)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the weather in Paris today?"}'

# News (current events)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are today'\''s top tech news?"}'
```

**Expected results:**
- Current, accurate information (not from training data cutoff)
- 5-15 sources per query in the `sources` array
- Source URIs are vertexaisearch.cloud.google.com redirect links
- Source titles show the actual domains (wikipedia.org, spacex.com, etc.)

## Common Issues

### Issue: Sources array is empty
**Cause**: Accessing grounding metadata incorrectly (must use `response.candidates[0]`)

**Solution**: Always access via:
```python
if response.candidates and len(response.candidates) > 0:
    metadata = response.candidates[0].grounding_metadata
```

### Issue: "google_search_retrieval is not supported"
**Cause**: Using legacy syntax with new library

**Solution**: Use `google_search` tool:
```python
tools=[types.Tool(google_search=types.GoogleSearch())]
```

### Issue: Library import errors
**Cause**: Wrong library installed

**Solution**: Ensure `google-genai` (not `google-generativeai`) is in requirements.txt

## Related Knowledge
- [AI Chat Integration](./ai-chat-integration.md) - The base chat feature this extends
- [Google GenAI Migration Pattern](../patterns/google-genai-migration.md) - How to migrate from old to new library

## Future Ideas
- [ ] Add dynamic retrieval config to control when search is triggered (avoid unnecessary searches)
- [ ] Display sources as clickable links in the chat UI
- [ ] Add confidence scores from grounding_supports
- [ ] Implement search_entry_point to show Google Search link
- [ ] Cache frequent queries to reduce API costs ($35 per 1,000 grounded queries)
- [ ] Add source preview on hover
- [ ] Track which sources users click on for analytics
