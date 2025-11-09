---
type: feature
name: AI Chat Integration
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - packages/web-app/src/pages/Chat.tsx
  - packages/backend-api/api/chat.py
  - packages/web-app/vite.config.ts
related:
  - .ai/knowledge/features/entra-id-authentication.md
  - .ai/knowledge/frontend/web-app-structure.md
tags: [ai, chat, gemini, ux, loading-states, web-app, backend]
---

# AI Chat Integration

## What It Does

Provides an interactive chat interface in the web app that connects to Google's Gemini AI (gemini-2.5-flash) through the FastAPI backend. Users can ask questions and receive AI-generated responses with visual feedback during processing, creating a smooth conversational experience.

## How It Works

**Architecture flow:**
```
Web App (Chat.tsx) → Vite Proxy → Backend API (chat.py) → Google Gemini API
```

### Frontend (Web App)

**Key file:** `packages/web-app/src/pages/Chat.tsx`

**State management:**
- `messages` - Array of chat messages (user/assistant roles)
- `message` - Current input text
- `isLoading` - Boolean tracking AI processing state

**User flow:**
1. User types message and clicks Send (or presses Enter)
2. Frontend acquires Azure AD token via MSAL
3. User message added to chat immediately (optimistic UI)
4. Loading state activated (input disabled, typing indicator shown)
5. POST request to `/api/chat` with Bearer token
6. Assistant response added to chat
7. Loading state cleared

**UX enhancements:**
- **Typing indicator**: 3 bouncing dots with staggered animation delays (0ms, 150ms, 300ms)
- **Disabled input**: Input field disabled with "Waiting for response..." placeholder
- **Pulsing send button**: Send icon pulses during processing
- **Error handling**: Toast notification on failure, optimistic update reverted

**Code reference:**
- Chat.tsx:13 - `isLoading` state definition
- Chat.tsx:33 - Loading state activation before API call
- Chat.tsx:63 - Loading state cleared in finally block
- Chat.tsx:113-123 - Typing indicator animation
- Chat.tsx:131-149 - Input/button disabled states

### Backend (API)

**Key file:** `packages/backend-api/api/chat.py`

**Endpoint:** `POST /api/chat`

**Request schema:**
```python
{
  "prompt": str  # User's question/message
}
```

**Response schema:**
```python
{
  "text": str,      # AI-generated response
  "sources": []     # Empty array (placeholder for future RAG)
}
```

**Implementation:**
- chat.py:20-28 - Main chat endpoint
- chat.py:21 - Uses dependency injection for Gemini API key from Azure Key Vault
- chat.py:23 - Configures genai client with API key
- chat.py:24 - Uses `gemini-2.5-flash` model (latest, replacing deprecated `gemini-pro`)
- chat.py:25 - Synchronous content generation (blocking)
- chat.py:27 - Error handling with 500 status on Gemini API failures

### API Proxy Configuration

**Key file:** `packages/web-app/vite.config.ts`

**Configuration:**
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

**Purpose:** Routes frontend `/api/*` requests to backend (port 8000) during development, avoiding CORS issues.

**Reference:** vite.config.ts:11-16

## Important Decisions

### 1. Gemini Model Selection
**Decision:** Use `gemini-2.5-flash` instead of `gemini-pro`

**Rationale:**
- Gemini 1.0 and 1.5 models (including `gemini-pro`) were retired in early 2025
- `gemini-2.5-flash` is the current stable model for production
- Provides faster responses suitable for interactive chat
- Maintains compatibility with existing `generate_content()` API

**Alternative considered:** `gemini-2.5-pro` (more capable but slower and more expensive)

### 2. Loading State UX
**Decision:** Show typing indicator + disable input + pulse send button

**Rationale:**
- Users need clear feedback that the system is working
- Multiple visual cues (animation, disabled state, pulsing) prevent confusion
- Prevents duplicate submissions during processing
- Creates professional, polished user experience

**Implementation details:**
- Typing indicator uses 3 bouncing dots with CSS animations
- Animation delays staggered for wave effect (0ms, 150ms, 300ms)
- Input placeholder changes to "Waiting for response..."
- Send button icon pulses with Tailwind's `animate-pulse`

### 3. Optimistic UI Updates
**Decision:** Add user message to chat immediately, before API response

**Rationale:**
- Feels more responsive (no delay before message appears)
- User gets instant feedback that action was received
- Revert on error to maintain consistency

**Tradeoff:** Requires error handling to remove message if API fails

### 4. Vite Proxy vs Environment Variable
**Decision:** Use Vite proxy for development API routing

**Rationale:**
- Simpler than CORS configuration in development
- No need to track different URLs for dev vs production
- Standard Vite pattern for API integration
- Frontend code uses relative URLs (`/api/chat`) that work in all environments

**Production consideration:** Production deployment requires backend URL configuration or reverse proxy

## Usage Example

**Frontend usage:**
```typescript
// User types "What's the weather?" and clicks Send

// 1. Message added to state
setMessages([...messages, { role: "user", content: "What's the weather?" }]);
setIsLoading(true);

// 2. API call with auth token
const response = await fetch("/api/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${accessToken.accessToken}`,
  },
  body: JSON.stringify({ prompt: "What's the weather?" }),
});

// 3. Response added to chat
const data = await response.json();
setMessages([...messages, { role: "assistant", content: data.text }]);
setIsLoading(false);
```

**Backend usage:**
```python
# Endpoint processes request
@router.post("/api/chat")
async def chat(request: ChatRequest, api_key: str = Depends(get_gemini_api_key)):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(request.prompt)
    return {"text": response.text, "sources": []}
```

## Authentication

**Required:** Azure AD Bearer token in Authorization header

**Flow:**
1. User must be authenticated (MSAL checks `accounts.length > 0`)
2. If not authenticated, login popup triggered automatically
3. Token acquired silently via MSAL's `acquireTokenSilent()`
4. Token passed as Bearer token to backend
5. Backend validates token (handled by `fastapi-azure-auth`)

**Reference:** Chat.tsx:17-24, Chat.tsx:34-37

## Error Handling

**Frontend errors:**
- Login failure: Logged to console, chat not sent
- Empty message: Silently ignored (button disabled)
- API failure: Toast notification + optimistic update reverted
- Network errors: Caught by try/catch, same handling as API errors

**Backend errors:**
- Gemini API error: 500 status with error message in detail
- Missing API key: Caught by dependency injection (401/403)
- Invalid request: Pydantic validation (422)

**Code reference:**
- Chat.tsx:55-61 - Frontend error handling
- chat.py:27-28 - Backend error handling

## Testing

**Manual testing performed:**
- ✅ Chat message sends successfully
- ✅ Typing indicator appears during processing
- ✅ Input disabled while waiting
- ✅ Response appears in chat
- ✅ Multiple messages work in sequence
- ✅ Error handling (tested with backend down)

**Test files:** None yet

**Coverage:** 0% (no automated tests)

## Common Issues

### Issue 1: 404 error on `/api/chat`
**Symptom:** Frontend request fails with 404 Not Found

**Cause:** Vite proxy not configured or dev server not restarted

**Solution:**
1. Check `vite.config.ts` has proxy configuration
2. Restart Vite dev server to pick up config changes
3. Verify backend is running on port 8000

### Issue 2: 500 error with "gemini-pro not found"
**Symptom:** Backend returns 500 with model not found error

**Cause:** Using deprecated Gemini model name

**Solution:**
1. Update to `gemini-2.5-flash` in chat.py:24
2. Restart backend server

### Issue 3: Typing indicator doesn't disappear
**Symptom:** Loading dots persist after response arrives

**Cause:** `isLoading` not cleared in finally block

**Solution:** Ensure `setIsLoading(false)` is in finally block (Chat.tsx:63)

## Performance Considerations

**Response time:**
- Gemini API typically responds in 1-3 seconds for simple queries
- No timeout configured (uses default fetch timeout)
- Longer queries may take 5-10+ seconds

**Future optimizations:**
- Add timeout handling (30s recommended)
- Implement streaming responses for long-form content
- Cache common responses
- Add request queuing to prevent concurrent API calls

## Future Ideas

- [ ] Streaming responses (word-by-word display like ChatGPT)
- [ ] Message history persistence (save to MongoDB)
- [ ] Chat sessions (multiple conversation threads)
- [ ] RAG integration (answer questions about user's news feed)
- [ ] Voice input support
- [ ] Message editing/regeneration
- [ ] Copy message to clipboard button
- [ ] Markdown rendering in responses
- [ ] Code syntax highlighting
- [ ] Image generation support
- [ ] Conversation export (PDF/text)
- [ ] Rate limiting on frontend
- [ ] Request cancellation if user navigates away

## Related Knowledge

- [Entra ID Authentication](./entra-id-authentication.md) - Provides Bearer tokens for API calls
- [Web App Structure](../frontend/web-app-structure.md) - Contains Chat.tsx page
- [Azure Functions Architecture](../components/azure-functions-architecture.md) - Future: batch processing of chat analytics

## Dependencies

**Frontend:**
- React 18 (state management)
- @azure/msal-react (authentication)
- lucide-react (icons)
- sonner (toast notifications)
- Tailwind CSS (animations, styling)

**Backend:**
- FastAPI (web framework)
- google-generativeai (Gemini SDK)
- fastapi-azure-auth (token validation)
- pydantic (request/response validation)

**Configuration:**
- Gemini API key stored in Azure Key Vault
- Retrieved via dependency injection in chat.py:21
