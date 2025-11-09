---
type: pattern
name: Google GenAI Library Migration
status: implemented
created: 2025-11-09
updated: 2025-11-09
files:
  - packages/backend-api/requirements.txt:4
  - packages/backend-api/api/chat.py:1-120
  - packages/backend-api/api/topics.py:1-79
related:
  - ../features/web-search-grounding.md
tags: [migration, google, genai, gemini, library-upgrade, api]
---

# Google GenAI Library Migration Pattern

## What It Is
A comprehensive pattern for migrating from the deprecated `google-generativeai` library to the new `google-genai` SDK, enabling modern features like Google Search grounding for Gemini 2.0+ models.

## When to Use This Pattern
- Upgrading from `google-generativeai` to `google-genai`
- Enabling Google Search grounding features
- Supporting Gemini 2.0+ models
- Preparing for `google-generativeai` end-of-life (August 31, 2025)

## Migration Steps

### Step 1: Update Dependencies

**requirements.txt:**
```diff
- google-generativeai
+ google-genai
```

**Install:**
```bash
pip install google-genai
```

### Step 2: Update Imports

**Before (Legacy):**
```python
import google.generativeai as genai
```

**After (New SDK):**
```python
from google import genai
from google.genai import types  # For type hints and configs
```

### Step 3: Update Client Initialization

**Before (Legacy):**
```python
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")
```

**After (New SDK):**
```python
client = genai.Client(api_key=api_key)
# No separate model initialization
```

### Step 4: Update Content Generation

**Before (Legacy):**
```python
response = model.generate_content(prompt)
text = response.text
```

**After (New SDK):**
```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)
text = response.text
```

### Step 5: Update Configuration (System Instructions, Tools)

**Before (Legacy):**
```python
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="You are a helpful assistant."
)
response = model.generate_content(prompt)
```

**After (New SDK):**
```python
config = types.GenerateContentConfig(
    system_instruction="You are a helpful assistant."
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=config
)
```

### Step 6: Add Google Search Tool (If Needed)

**New Capability (Not available in legacy):**
```python
from google.genai import types

config = types.GenerateContentConfig(
    system_instruction="...",
    tools=[types.Tool(google_search=types.GoogleSearch())]
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=config
)
```

### Step 7: Extract Grounding Metadata (If Using Search)

**New response structure:**
```python
# Sources are nested in candidates
if response.candidates and len(response.candidates) > 0:
    candidate = response.candidates[0]

    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
        metadata = candidate.grounding_metadata

        # Extract from grounding_chunks
        for chunk in metadata.grounding_chunks:
            if chunk.web:
                source = {
                    "uri": chunk.web.uri,
                    "title": chunk.web.title
                }
```

## Complete Example

### Before: chat.py (Legacy)

```python
import google.generativeai as genai

async def chat(request: ChatRequest, api_key: str = Depends(get_gemini_api_key)):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction="You are a helpful assistant."
    )
    response = model.generate_content(request.prompt)
    return {"text": response.text}
```

### After: chat.py (New SDK with Search)

```python
from google import genai
from google.genai import types

async def chat(request: ChatRequest, api_key: str = Depends(get_gemini_api_key)):
    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction="You are a helpful assistant.",
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=request.prompt,
        config=config
    )

    # Extract sources (new capability)
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

    return {
        "status": "success",
        "model": "gemini-2.5-flash",
        "reply": response.text.strip(),
        "sources": sources
    }
```

## Key Differences

| Aspect | Legacy (`google-generativeai`) | New SDK (`google-genai`) |
|--------|-------------------------------|-------------------------|
| **Import** | `import google.generativeai as genai` | `from google import genai` |
| **Client** | `genai.configure(api_key)` | `genai.Client(api_key=...)` |
| **Model** | `GenerativeModel("model-name")` | `client.models.generate_content(model="...")` |
| **Config** | Model constructor args | `types.GenerateContentConfig(...)` |
| **Search** | Not supported properly | `types.Tool(google_search=types.GoogleSearch())` |
| **Response** | Direct attributes | Nested in `response.candidates[0]` |
| **Support** | Ends Aug 31, 2025 | Actively maintained |

## Testing Migration

**Test basic functionality:**
```bash
# Before migration (should work)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello"}'

# After migration (should still work)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello"}'
```

**Test new search feature:**
```bash
# Should return current information + sources
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is today'\''s weather in London?"}'
```

## Common Migration Issues

### Issue: "No module named 'google.genai'"
**Cause**: Old library still installed or wrong import

**Solution**:
```bash
pip uninstall google-generativeai
pip install google-genai
```

### Issue: "google_search_retrieval is not supported"
**Cause**: Using legacy tool name with new library

**Solution**: Use `google_search` instead:
```python
# Wrong
tools='google_search_retrieval'  # Legacy syntax

# Correct
tools=[types.Tool(google_search=types.GoogleSearch())]
```

### Issue: Response structure changed
**Cause**: New SDK nests response in `candidates[0]`

**Solution**: Always check candidates:
```python
if response.candidates and len(response.candidates) > 0:
    candidate = response.candidates[0]
    # Access properties from candidate
```

### Issue: Type errors with configs
**Cause**: Not importing `types` from `google.genai`

**Solution**:
```python
from google.genai import types

config = types.GenerateContentConfig(...)
```

## Related Knowledge
- [Web Search Grounding Feature](../features/web-search-grounding.md) - Main feature enabled by this migration

## Resources
- [Google GenAI SDK Documentation](https://googleapis.github.io/python-genai/)
- [Migration Guide](https://ai.google.dev/gemini-api/docs/migrate)
- [Google Search Grounding Docs](https://ai.google.dev/gemini-api/docs/google-search)

## Future Considerations
- Consider using async client: `genai.AsyncClient()`
- Explore streaming responses: `client.models.generate_content_stream(...)`
- Implement dynamic retrieval config to control search triggering
- Monitor pricing: $35 per 1,000 grounded queries
