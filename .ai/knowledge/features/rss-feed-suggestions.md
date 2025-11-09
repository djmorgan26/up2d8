# RSS Feed Suggestions with AI

## Feature Description
This feature enhances the user experience by allowing users to discover and add new RSS feeds using AI-powered suggestions. Instead of manually searching for RSS feed URLs, users can provide a natural language query (e.g., "tech news feeds", "cooking blogs"), and the system will leverage Google Gemini with Google Search grounding to suggest relevant RSS feeds.

## Implementation Details

### Backend (`packages/backend-api`)
- **Endpoint:** `POST /api/rss_feeds/suggest`
  - Accepts a `query` string from the frontend.
  - Utilizes `google.genai` client with `gemini-2.5-flash` model.
  - Employs `types.Tool(google_search=types.GoogleSearch())` for web search grounding.
  - The LLM is prompted to return a JSON array of objects, each containing `title`, `url`, and `category` for suggested feeds.
  - Includes logic to strip markdown code block fences (` ```json...``` `) from the LLM's response before JSON parsing.
  - Returns a list of suggested feeds.

### Frontend (`packages/web-app`)
- **Component:** `src/pages/Feeds.tsx`
  - New state variables: `llmSearchQuery`, `llmSuggestions`, `llmLoading`.
  - `SuggestedFeed` interface updated to include `title`, `url`, and `category`.
  - UI elements within the "Add New RSS Feed" dialog:
    - Input field for `llmSearchQuery`.
    - "Suggest" button to trigger `handleSuggestFeeds`.
    - Loading indicator (`Loader2`).
    - Display area for `llmSuggestions`, showing title, URL, and category.
    - "Add" button for each suggestion, triggering `handleAddSuggestedFeed`.
- **API Client:** `src/lib/api.ts`
  - New function `suggestRSSFeeds(query: string)`: Makes a POST request to `/api/rss_feeds/suggest`.
  - `addRSSFeed` function updated to accept `title?: string` and `category?: string` parameters.

## How it Works
1.  User enters a query in the "Suggest Feeds with AI" input field.
2.  `handleSuggestFeeds` in the frontend calls `suggestRSSFeeds` in the API client.
3.  The backend's `/api/rss_feeds/suggest` endpoint sends the query to the Gemini LLM.
4.  The LLM performs a Google Search, identifies relevant RSS feeds, and formats them as a JSON array with `title`, `url`, and `category`.
5.  The backend parses the LLM's response and sends the suggestions back to the frontend.
6.  The frontend displays the suggested feeds.
7.  When a user clicks "Add" on a suggested feed, `handleAddSuggestedFeed` calls `addRSSFeed` with the provided `url`, `title`, and `category`.
8.  The backend's `create_rss_feed` function stores the new feed, applying category standardization.
