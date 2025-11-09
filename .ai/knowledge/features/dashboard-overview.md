---
type: feature
name: Dashboard Overview
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - packages/web-app/src/pages/Dashboard.tsx
  - packages/backend-api/api/articles.py
  - packages/backend-api/api/rss_feeds.py
related:
  - .ai/knowledge/features/ai-chat-integration.md
  - .ai/knowledge/components/web-app-structure.md
tags: [dashboard, frontend, web-app, stats, ux]
---

# Dashboard Overview

## What It Does

The Dashboard is the main landing page of the UP2D8 web app, providing users with an at-a-glance view of their personalized news digest. It displays key statistics, featured articles, and recent content in a visually organized layout with stats cards, prioritized sections, and actionable empty states.

**Key features:**
- 4 interactive stats cards (Total Articles, Active Feeds, New Today, AI Chat shortcut)
- Featured Stories section highlighting top 3 articles
- Recent Articles grid showing latest 6 items
- Enhanced empty state with call-to-action
- Real-time date display
- Responsive grid layouts for mobile/tablet/desktop

## How It Works

### Architecture

The Dashboard follows a **hybrid stats + content approach**, combining overview metrics with prioritized article display.

**Data Flow:**
```
Dashboard Component
  ↓ (parallel fetch)
  ├─> GET /api/articles → Backend transforms DB fields → Article list
  └─> GET /api/rss_feeds → RSS feed count
  ↓
Stats Calculation (client-side)
  ├─> Total articles count
  ├─> Active feeds count
  └─> Filter articles published today
  ↓
Render Sections
  ├─> Stats cards (4 metrics)
  ├─> Featured stories (top 3)
  └─> Recent articles (latest 6)
```

### Key Files

- **`packages/web-app/src/pages/Dashboard.tsx:1-199`** - Main dashboard component
  - Fetches articles and feeds in parallel (lines 28-30)
  - Calculates today's articles (lines 45-49)
  - Renders stats cards, featured section, recent articles
  - Handles loading states and empty state

- **`packages/backend-api/api/articles.py:62-92`** - Articles API endpoint
  - Transforms MongoDB fields to frontend schema (lines 67-92)
  - Extracts article source from URL domain (lines 70-81)
  - Generates missing IDs for old articles (line 84)
  - Returns standardized `{data: [...]}` format

- **`packages/backend-api/api/rss_feeds.py:44-48`** - RSS Feeds API endpoint
  - Returns feed list wrapped in `{data: [...]}` format
  - Used to display Active Feeds count

### Data Transformation Pattern

**Problem:** Backend stores articles with fields (`link`, `summary`, `published`) that don't match frontend expectations (`url`, `description`, `published_at`).

**Solution:** API layer transforms data on read:

```python
# Backend transformation (articles.py:67-92)
transformed.append({
    "id": article.get("id") or str(uuid.uuid4()),  # Generate if missing
    "title": article.get("title"),
    "description": article.get("summary"),          # summary → description
    "url": article.get("link"),                     # link → url
    "published_at": article.get("published"),       # published → published_at
    "source": source,                               # Extracted from URL
})
```

This keeps the database schema independent from frontend contracts.

### Source Extraction Pattern

Articles often lack explicit `source` metadata. The API extracts it from the article URL:

```python
# Extract domain from URL (articles.py:70-81)
link = "https://techcrunch.com/2025/10/31/article-title/"
domain = urlparse(link).netloc  # → "techcrunch.com"
source = domain.replace("www.", "").split(".")[0].title()  # → "Techcrunch"
```

**Fallback chain:**
1. Use `article.source` if present and not "rss"
2. Extract from URL domain
3. Default to "RSS" if URL missing

## Important Decisions

### Decision 1: Hybrid Dashboard Layout (Stats + Content)

**Options considered:**
- A) Stats-rich dashboard (metrics-focused)
- B) Simple fix (just show articles)
- C) Feed-centric (group by source)

**Chosen:** Hybrid approach combining stats cards with prioritized content sections

**Rationale:**
- Provides immediate value (stats overview) + engagement (content preview)
- Stats cards act as navigation shortcuts (e.g., "Ask AI" card links to chat)
- Prioritization (Featured vs Recent) better than flat article grid
- Scalable: Can add more stats/sections as features grow

### Decision 2: API Data Transformation Layer

**Alternative:** Update all database records to match frontend schema

**Chosen:** Transform data in API layer during read operations

**Rationale:**
- Non-destructive: Works with existing database records
- Flexible: Frontend schema can evolve without migrations
- Handles missing data gracefully (generates IDs, extracts sources)
- Single source of truth for field mapping

### Decision 3: Client-Side Stats Calculation

**Alternative:** Backend calculates "New Today" count via aggregation query

**Chosen:** Fetch all articles, filter on client

**Rationale:**
- Simple implementation for MVP
- Article count is small (< 100s), performance acceptable
- Reduces backend complexity
- Can optimize with backend aggregation later if needed

### Decision 4: Featured Stories = Top 3 Articles

**Alternative:** Use ML/AI to determine "featured" based on engagement, topics, etc.

**Chosen:** Simple slice of first 3 articles

**Rationale:**
- MVP approach: Get UI working first
- Articles are already sorted by relevance (backend could sort by date/score)
- Placeholder for future smart ranking algorithm
- Easy to replace with sophisticated logic later

## Usage Example

**Frontend - Dashboard Component:**

```tsx
const Dashboard = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [feedCount, setFeedCount] = useState(0);

  // Fetch data in parallel
  useEffect(() => {
    const fetchData = async () => {
      const [articlesRes, feedsRes] = await Promise.all([
        getArticles(),
        getRSSFeeds().catch(() => ({ data: { data: [] } }))
      ]);
      setArticles(articlesRes.data.data || []);
      setFeedCount(feedsRes.data?.data?.length || 0);
    };
    fetchData();
  }, []);

  // Calculate stats
  const todayArticles = articles.filter((a) => {
    return new Date(a.published_at).toDateString() === new Date().toDateString();
  });

  // Prioritize content
  const featuredArticles = articles.slice(0, 3);
  const recentArticles = articles.slice(0, 6);

  return (
    <div>
      {/* Stats Cards */}
      <StatsGrid articles={articles} feedCount={feedCount} todayCount={todayArticles.length} />

      {/* Featured & Recent Sections */}
      <FeaturedSection articles={featuredArticles} />
      <RecentSection articles={recentArticles} />
    </div>
  );
};
```

**Backend - Articles API:**

```python
@router.get("/api/articles")
async def get_articles(db=Depends(get_db_client)):
    articles = list(db.articles.find({}, {"_id": 0}))

    # Transform each article
    transformed = []
    for article in articles:
        # Extract source from URL if missing
        source = extract_source_from_url(article.get("link"))

        transformed.append({
            "id": article.get("id") or str(uuid.uuid4()),
            "title": article.get("title"),
            "description": article.get("summary"),
            "url": article.get("link"),
            "published_at": article.get("published"),
            "source": source,
        })

    return {"data": transformed}
```

## UI Components Used

- **GlassCard** - Glassmorphism card container for stats
- **ArticleCard** - Individual article display with title, description, date, source
- **ArticleSkeleton** - Loading placeholder during data fetch
- **Button** (shadcn/ui) - CTA in empty state
- **Link** (React Router) - Navigation to Feeds and Chat pages
- **Icons** (lucide-react) - Newspaper, Rss, TrendingUp, Clock, MessageSquare

## Sections Breakdown

### 1. Stats Cards (4 metrics)

| Metric | Calculation | Icon | Color | Interactive |
|--------|-------------|------|-------|-------------|
| Total Articles | `articles.length` | Newspaper | Primary | No |
| Active Feeds | `feedCount` | Rss | Accent | No |
| New Today | Filter by `published_at === today` | Clock | Green | No |
| Ask AI | Link to `/chat` | MessageSquare | Purple | Yes (hover effect) |

### 2. Featured Stories

- Shows top 3 articles
- 3-column grid on desktop
- Same ArticleCard component as recent section
- Only visible if articles exist

### 3. Recent Articles

- Shows latest 6 articles
- 3-column grid on desktop, 2 on tablet, 1 on mobile
- Shows count indicator if > 6 articles total
- Uses same ArticleCard component

### 4. Empty State

Displayed when `articles.length === 0`:
- Icon (large newspaper)
- Heading: "No articles yet"
- Description: Explains next step
- CTA Button: "Add Your First Feed" → links to `/feeds`

## Testing

**Manual testing performed:**
- ✅ Dashboard loads with 1 article (verified stats display correctly)
- ✅ Source extraction works (URL → domain name)
- ✅ Empty state displays when no articles
- ✅ Stats card navigation (Ask AI → /chat)
- ✅ Responsive grid layouts
- ✅ Loading skeletons appear during fetch

**Test scenarios to add:**
- [ ] Multiple articles (test featured vs recent sections)
- [ ] Articles from different sources (verify source extraction)
- [ ] Articles from today vs older (verify "New Today" count)
- [ ] Error handling (API failure, network issues)

## Common Issues

### Issue 1: "Unknown" source displayed

**Cause:** Article in database has no `source` field or `source: "rss"`

**Fix:** API now extracts source from URL domain (implemented in articles.py:70-81)

**Verification:** Check article card bottom-right corner shows domain name (e.g., "Techcrunch")

### Issue 2: "Invalid Date" in article cards

**Cause:** Field mismatch - backend sends `published`, frontend expects `published_at`

**Fix:** API transformation maps `published` → `published_at` (articles.py:88)

**Status:** ✅ Fixed in commit 2e5697d

### Issue 3: Missing article IDs

**Cause:** Old articles in database created before `id` field was added

**Fix:** API generates UUID if `id` is null/missing (articles.py:84)

**Impact:** Prevents React key warnings, ensures unique identifiers

## Performance Considerations

**Current approach:**
- Fetches ALL articles from database (no pagination)
- Client-side filtering for "New Today"
- Parallel requests for articles + feeds

**Scalability limits:**
- Works well for < 1000 articles
- Network payload grows with article count
- Client-side filtering acceptable for small datasets

**Future optimizations:**
- [ ] Add pagination to `/api/articles` endpoint
- [ ] Backend aggregation for "New Today" count
- [ ] Caching layer (Redis) for frequently accessed data
- [ ] GraphQL for selective field fetching

## Related Knowledge

- [AI Chat Integration](./ai-chat-integration.md) - "Ask AI" stat card links here
- [Web App Structure](../frontend/web-app-structure.md) - Dashboard is one of 6 pages
- [Entra ID Authentication](./entra-id-authentication.md) - May require auth in future

## Future Ideas

- [ ] **Smart Featured Algorithm** - Use ML/engagement data to rank "featured" articles
- [ ] **Read/Unread Tracking** - Add "Unread" metric to stats cards
- [ ] **Saved Articles** - Add "Saved for Later" section
- [ ] **Filter by Source** - Dropdown to filter articles by feed source
- [ ] **Date Range Selector** - View articles from specific time periods
- [ ] **Personalization** - User preferences affect featured article ranking
- [ ] **Activity Feed** - Show recent user actions (saved, read, chatted about)
- [ ] **Trending Topics** - Extract and display trending keywords/topics
- [ ] **Search Bar** - Quick search across all articles
- [ ] **Bulk Actions** - Mark all as read, archive old articles
- [ ] **Export** - Download articles as PDF/Markdown
- [ ] **Notifications** - Badge on "New Today" if unread articles exist

## Migration Notes

**Database compatibility:**
- Works with existing articles that lack `id` or `source` fields
- No database migration required
- Backward compatible with old schema

**API versioning:**
- Current endpoint: `/api/articles` (no version prefix)
- Consider `/api/v1/articles` for future breaking changes
- Response format `{data: [...]}` is standard for all endpoints

---

**Summary:** The Dashboard provides a comprehensive overview of the user's news digest with stats, prioritized content, and smart empty states. The implementation balances simplicity (MVP) with extensibility (room for ML/AI enhancements). Data transformation in the API layer ensures frontend/backend schema independence.
