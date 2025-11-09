---
type: feature
name: AI Topic Suggestions
status: implemented
created: 2025-11-09
updated: 2025-11-09
files:
  - packages/backend-api/api/topics.py
  - packages/web-app/src/components/PreferencesDialog.tsx
  - packages/web-app/src/lib/api.ts
related:
  - .ai/knowledge/features/ai-chat-integration.md
  - .ai/knowledge/components/web-app-structure.md
tags: [ai, gemini, topics, suggestions, personalization, backend, frontend]
---

# AI Topic Suggestions

## What It Does

Provides intelligent topic suggestions to help users discover new content areas to follow. Uses Google Gemini AI to generate personalized recommendations based on existing interests or search queries. Integrated directly into the Preferences dialog for seamless topic discovery.

## How It Works

**Backend Architecture** (`packages/backend-api/api/topics.py:1-79`)

The backend provides a POST endpoint that uses Google Gemini 2.0 Flash Experimental to generate topic suggestions:

```python
POST /api/topics/suggest
Request: { interests: string[], query: string }
Response: { suggestions: string[] }
```

**Three suggestion modes:**
1. **Query-based**: User searches for specific area (e.g., "machine learning")
2. **Interest-based**: AI suggests related topics based on existing user interests
3. **Popular topics**: Suggests general popular topics when no input provided

**Key implementation details:**
- Uses `gemini-2.0-flash-exp` model for fast, cost-effective suggestions
- Prompt engineering requests comma-separated list format
- Post-processing cleans up numbering/bullets that might slip through
- Limits results to 8 suggestions maximum
- Error handling with proper logging and HTTP 500 on failure

**Frontend Integration** (`packages/web-app/src/components/PreferencesDialog.tsx:57-81`)

```typescript
const handleGetSuggestions = async () => {
  const response = await suggestTopics(topics, searchQuery);
  const newSuggestions = response.data.suggestions.filter(
    (s: string) => !topics.includes(s)
  );
  setSuggestions(newSuggestions);
};
```

**User experience:**
1. User opens Preferences dialog from Settings
2. Can search for topic ideas using search input
3. Clicks "Suggest" button with Sparkles icon
4. AI generates 5-8 relevant suggestions
5. Suggestions appear as clickable badges with + icon
6. One-click to add suggestion to user's topic list
7. Filters out topics already in user's list

## Important Decisions

### 1. Use Gemini 2.0 Flash Experimental
**Why**: Latest model with better instruction-following, faster, and cheaper than 2.5 Flash
**Trade-off**: Experimental models may change behavior, but worth it for better performance

### 2. Comma-Separated Prompt Strategy
**Why**: Easier to parse than JSON or numbered lists, more natural for LLM
**Implementation**: Request "comma-separated list, no explanations" in prompt
**Backup**: Post-processing cleans up any numbering that leaks through

### 3. Inline Integration in Preferences Dialog
**Why**: Topic discovery should be part of the topic editing workflow
**Alternative considered**: Separate discovery page (rejected - too many clicks)
**UX**: Search box + button in "Discover New Topics" section within preferences

### 4. Filter Already-Selected Topics
**Why**: Don't suggest topics user already has
**Implementation**: Client-side filtering after receiving suggestions
**Benefit**: Prevents duplicate suggestions, cleaner UX

## Usage Example

**Backend API:**
```python
# Query-based suggestions
POST /api/topics/suggest
{
  "interests": [],
  "query": "artificial intelligence"
}

Response:
{
  "suggestions": [
    "Machine Learning",
    "Neural Networks",
    "Deep Learning",
    "AI Ethics",
    "Computer Vision",
    "Natural Language Processing",
    "Robotics",
    "AI Research"
  ]
}
```

**Frontend:**
```typescript
import { suggestTopics } from "@/lib/api";

// Get suggestions based on current interests
const response = await suggestTopics(
  ["technology", "science"],
  ""
);

// Get suggestions based on search query
const response = await suggestTopics(
  [],
  "startup funding"
);
```

## Testing

**Backend tests**: `packages/backend-api/tests/api/test_topics.py` (not created yet)
**Frontend**: Manual testing via Preferences dialog

**Test scenarios needed:**
- [ ] Query-based suggestions
- [ ] Interest-based suggestions
- [ ] Default popular topics (no input)
- [ ] Error handling (API key missing, Gemini failure)
- [ ] Suggestion cleaning (numbering removal)
- [ ] Limit to 8 suggestions

## Common Issues

**Issue**: Suggestions include numbering (e.g., "1. Technology")
**Solution**: Post-processing strips common prefixes:
```python
if ". " in cleaned:
    cleaned = cleaned.split(". ", 1)[-1]
if cleaned.startswith("- "):
    cleaned = cleaned[2:]
```

**Issue**: Same topics suggested as user already has
**Solution**: Frontend filters out duplicates:
```typescript
const newSuggestions = response.data.suggestions.filter(
  (s: string) => !topics.includes(s)
);
```

**Issue**: Gemini API key not configured
**Solution**: Proper error handling returns 500 with generic message, logs detailed error

## Related Knowledge

- [AI Chat Integration](./ai-chat-integration.md) - Also uses Gemini for chat responses
- [User Preferences Management](./user-preferences-management.md) - Where topic suggestions are used
- [Web App Structure](../frontend/web-app-structure.md) - Overall frontend architecture

## Future Ideas

- [ ] Cache suggestions for common queries to reduce API calls
- [ ] Allow users to provide feedback on suggestions (thumbs up/down)
- [ ] Track which suggestions users actually add to refine future suggestions
- [ ] Suggest based on trending topics in user's feeds
- [ ] Multi-language support for topic suggestions
- [ ] Show why a topic was suggested (explanation from AI)
- [ ] Batch suggestion generation for onboarding (suggest 20 diverse topics)
- [ ] Use user's article reading history to improve suggestions
