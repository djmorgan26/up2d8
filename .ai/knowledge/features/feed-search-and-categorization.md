---
type: feature
name: Feed Search and Categorization
status: implemented
created: 2025-11-09
updated: 2025-11-09
files:
  - packages/web-app/src/pages/Feeds.tsx
  - packages/backend-api/api/rss_feeds.py
related:
  - .ai/knowledge/frontend/web-app-structure.md
tags: [feeds, search, categorization, filtering, ui, frontend]
---

# Feed Search and Categorization

## What It Does

Provides search and categorization capabilities for RSS feed management. Users can search feeds by title or URL, and feeds are automatically grouped by category for better organization. Improves feed discoverability and organization, especially for users with many feeds.

## How It Works

### Frontend Implementation (`packages/web-app/src/pages/Feeds.tsx`)

**Search functionality** (`:89-97`):
```typescript
const [searchTerm, setSearchTerm] = useState("");

// Filter feeds based on search term
const filteredFeeds = feeds.filter(
  (feed) =>
    feed.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    feed.url.toLowerCase().includes(searchTerm.toLowerCase())
);
```

**Key features:**
- Case-insensitive search
- Searches both title and URL fields
- Real-time filtering (no submit button)
- Empty state handles no search results

**Category grouping** (`:100-107`):
```typescript
// Group filtered feeds by category
const groupedFeeds = filteredFeeds.reduce((acc, feed) => {
  const category = feed.category || "Uncategorized";
  if (!acc[category]) {
    acc[category] = [];
  }
  acc[category].push(feed);
  return acc;
}, {} as Record<string, Feed[]>);
```

**Key features:**
- Groups feeds by category field
- Fallback to "Uncategorized" for feeds without category
- Uses reduce pattern for efficient grouping
- Dynamic categorization (updates as feeds change)

**UI Structure:**
```tsx
<Input
  placeholder="Search feeds by title or URL..."
  value={searchTerm}
  onChange={(e) => setSearchTerm(e.target.value)}
  className="glass-card border-border/50"
/>

{Object.entries(groupedFeeds).map(([category, categoryFeeds]) => (
  <div key={category} className="space-y-3">
    <h3 className="text-lg font-semibold">{category}</h3>
    {categoryFeeds.map((feed) => (
      <GlassCard key={feed.id} hover>
        <h3>{feed.title || "Untitled Feed"}</h3>
        <p>{feed.url}</p>
        <Button onClick={() => handleDeleteFeed(feed.id)}>
          <Trash2 className="h-4 w-4" />
        </Button>
      </GlassCard>
    ))}
  </div>
))}
```

### Backend Support

**Feed model** includes category field:
```typescript
interface Feed {
  id: string;
  url: string;
  title?: string;
  category?: string;  // Added for categorization
}
```

**Note**: Backend API (`packages/backend-api/api/rss_feeds.py`) supports category field, but it's not currently exposed in the add feed UI. Categories would need to be:
1. Manually set in database, OR
2. Added to add feed dialog (future enhancement), OR
3. Auto-detected from feed metadata (future enhancement)

## Important Decisions

### 1. Client-Side Filtering
**Why**: Instant feedback, no API calls, works offline
**Trade-off**: All feeds must be loaded (fine for < 1000 feeds)
**Alternative rejected**: Server-side search (adds latency, complexity)

### 2. Search Both Title and URL
**Why**: Users might remember either identifier
**Example**: Searching "techcrunch" matches:
  - Title: "TechCrunch - Latest News"
  - URL: "https://techcrunch.com/feed"
**Alternative rejected**: Title-only search (miss feeds with generic titles)

### 3. Real-Time Search (No Submit Button)
**Why**: Faster UX, immediate feedback
**Implementation**: onChange event triggers filter
**Performance**: Array.filter is fast enough for typical feed counts

### 4. "Uncategorized" Fallback
**Why**: Gracefully handles feeds without category
**UX**: All feeds visible, even if uncategorized
**Alternative rejected**: Hide uncategorized feeds (data loss)

### 5. Category Grouping Always On
**Why**: Better organization, scales well
**Trade-off**: Extra nesting level in UI
**Alternative rejected**: Flat list (hard to scan with many feeds)

### 6. No Category Editing in UI (Yet)
**Why**: MVP feature, categories not widely used yet
**Current state**: Category field supported but not exposed
**Future**: Add category selector to add/edit feed dialogs

## Usage Example

**Searching for feeds:**
```typescript
// User types "tech" in search box
setSearchTerm("tech");

// Filters to feeds matching "tech"
filteredFeeds = [
  { id: "1", title: "TechCrunch", url: "...", category: "Technology" },
  { id: "2", title: "Ars Technica", url: "...", category: "Technology" }
];

// Groups by category
groupedFeeds = {
  "Technology": [
    { id: "1", title: "TechCrunch", ... },
    { id: "2", title: "Ars Technica", ... }
  ]
};
```

**Category grouping:**
```typescript
// Feeds from API
feeds = [
  { id: "1", title: "TechCrunch", category: "Technology" },
  { id: "2", title: "Hacker News", category: "Technology" },
  { id: "3", title: "BBC News", category: "News" },
  { id: "4", title: "Random Blog", category: undefined }
];

// After grouping
groupedFeeds = {
  "Technology": [
    { id: "1", title: "TechCrunch" },
    { id: "2", title: "Hacker News" }
  ],
  "News": [
    { id: "3", title: "BBC News" }
  ],
  "Uncategorized": [
    { id: "4", title: "Random Blog" }
  ]
};
```

## UI States

**Empty state (no feeds):**
```tsx
<GlassCard className="text-center py-12">
  <p className="text-muted-foreground">
    No feeds added yet. Add your first feed to get started!
  </p>
</GlassCard>
```

**Empty search results:**
```tsx
<GlassCard className="text-center py-12">
  <p className="text-muted-foreground">
    No feeds found. Try adjusting your search or add a new feed!
  </p>
</GlassCard>
```

**Loading state:**
```tsx
{[1, 2, 3].map((i) => <FeedSkeleton key={i} />)}
```

## Common Issues

**Issue**: Search doesn't work for partial matches
**Solution**: Already uses `.includes()` for substring matching

**Issue**: Category names inconsistent (e.g., "Tech" vs "Technology")
**Solution**: Need category standardization when adding category UI
**Future**: Predefined category list with autocomplete

**Issue**: Uncategorized section appears empty but feeds exist
**Solution**: Check that category field is actually undefined (not empty string)

**Issue**: Search is case-sensitive
**Solution**: Already uses `.toLowerCase()` on both sides

## Testing

**Manual testing checklist:**
- [ ] Search by feed title (partial match)
- [ ] Search by feed URL (partial match)
- [ ] Clear search (see all feeds again)
- [ ] Add feed without category (appears in Uncategorized)
- [ ] Multiple categories display correctly
- [ ] Empty search results show correct message
- [ ] Search while loading (should wait for data)

**Test cases needed:**
```typescript
describe("Feed search", () => {
  it("filters by title", () => {
    // searchTerm="tech" matches "TechCrunch"
  });

  it("filters by URL", () => {
    // searchTerm="techcrunch.com" matches feed
  });

  it("is case-insensitive", () => {
    // searchTerm="TECH" matches "techcrunch"
  });

  it("handles no results", () => {
    // searchTerm="zzz" shows empty state
  });
});

describe("Feed categorization", () => {
  it("groups by category", () => {
    // Multiple feeds with same category grouped together
  });

  it("handles uncategorized feeds", () => {
    // Feeds without category appear in Uncategorized
  });

  it("handles empty categories gracefully", () => {
    // Empty string treated as Uncategorized
  });
});
```

## Related Knowledge

- [Web App Structure](../frontend/web-app-structure.md) - Overall frontend architecture
- [RSS Feed Management](./rss-feed-management.md) - Parent feature (if documented)

## Future Ideas

- [ ] **Category editing**: Add category selector to add/edit feed dialogs
- [ ] **Category autocomplete**: Suggest existing categories when adding feed
- [ ] **Predefined categories**: Tech, News, Sports, Science, Entertainment, etc.
- [ ] **Category colors**: Visual distinction between categories
- [ ] **Collapsible categories**: Expand/collapse category sections
- [ ] **Category stats**: Show feed count per category in header
- [ ] **Advanced search**: Filter by category + search term
- [ ] **Search highlighting**: Highlight matching text in results
- [ ] **Saved searches**: Remember recent search terms
- [ ] **Sort options**: Alphabetical, by date added, by article count
- [ ] **Bulk categorization**: Select multiple feeds, assign category
- [ ] **Category renaming**: Rename category (update all feeds)
- [ ] **Auto-categorization**: Use AI to suggest category from feed content
- [ ] **Feed metadata extraction**: Parse category from feed XML/JSON
- [ ] **Category management page**: CRUD operations on categories
- [ ] **Category icons**: Icon per category for visual appeal
- [ ] **Multi-category support**: Feed can belong to multiple categories (tags)
