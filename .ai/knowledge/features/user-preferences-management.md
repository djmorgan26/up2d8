---
type: feature
name: User Preferences Management
status: implemented
created: 2025-11-09
updated: 2025-11-09
files:
  - packages/backend-api/api/users.py
  - packages/web-app/src/components/PreferencesDialog.tsx
  - packages/web-app/src/components/NotificationsDialog.tsx
  - packages/web-app/src/pages/Settings.tsx
  - packages/web-app/src/lib/api.ts
  - packages/backend-api/tests/api/test_users.py
related:
  - .ai/knowledge/features/ai-topic-suggestions.md
  - .ai/knowledge/features/entra-id-authentication.md
  - .ai/knowledge/patterns/entra-id-user-migration.md
tags: [settings, preferences, notifications, topics, backend, frontend, dialogs]
---

# User Preferences Management

## What It Does

Comprehensive user preference management system allowing users to customize their news experience. Includes topic selection with AI suggestions, newsletter format preferences, email notification settings, and breaking news alerts. Fully integrated with Settings page through modal dialogs.

## How It Works

### Backend API (`packages/backend-api/api/users.py`)

**User Creation/Update Endpoints:**
```python
POST /api/users           # Create or update user with topics
PUT /api/users/{user_id}  # Update user preferences
```

**User creation logic** (`api/users.py:20-67`):
1. **Extract user from Entra ID token** (via `get_current_user` dependency)
2. **Check for existing user by user_id** (sub from token)
3. **If exists**: Update topics (addToSet pattern)
4. **If not by ID, check by email**: Migration scenario (see Entra ID Migration pattern)
5. **If completely new**: Create new user document with topics and metadata

**User update logic** (`api/users.py:70-90`):
```python
PUT /api/users/{user_id}
{
  "topics": ["tech", "science"],
  "preferences": {
    "newsletter_format": "detailed",
    "email_notifications": true,
    "newsletter_frequency": "daily",
    "breaking_news": false
  }
}
```

**Key features:**
- Partial updates supported (only send changed fields)
- Topics array completely replaced if provided
- Preferences object merged with existing
- Returns 404 if user not found

### Frontend - Preferences Dialog (`packages/web-app/src/components/PreferencesDialog.tsx`)

**Topic Management:**
- Input field to add custom topics
- Display topics as badges with remove button (X icon)
- Enter key or Add button to add topic
- Duplicate prevention (can't add same topic twice)

**AI Topic Discovery:**
- Search input for topic ideas
- "Suggest" button with Sparkles icon triggers AI suggestions
- AI-generated topics appear as clickable badges with + icon
- One-click to add suggestions to topic list
- Filters out topics already selected
- See [AI Topic Suggestions](./ai-topic-suggestions.md) for details

**Newsletter Format:**
- Radio group with two options:
  - "Concise" - Quick summaries and headlines
  - "Detailed" - In-depth analysis and full articles
- Saved to `preferences.newsletter_format`

**Save behavior:**
- Validates at least one topic selected
- Calls `updateUser(userId, { topics, preferences })`
- Shows success toast and closes dialog
- Triggers `onSaveSuccess()` callback to refresh parent data

### Frontend - Notifications Dialog (`packages/web-app/src/components/NotificationsDialog.tsx`)

**Email Notifications Toggle:**
- Master switch for all email notifications
- Disables other options when off
- Saved to `preferences.email_notifications`

**Newsletter Frequency:**
- Radio group with three options:
  - Daily - Every morning at 8 AM
  - Weekly - Every Monday morning
  - Monthly - First of each month
- Disabled when email notifications are off
- Saved to `preferences.newsletter_frequency`

**Breaking News Alerts:**
- Toggle for instant notifications on major events
- Disabled when email notifications are off
- Saved to `preferences.breaking_news`

### Settings Page Integration (`packages/web-app/src/pages/Settings.tsx`)

**Implementation:**
```typescript
const [preferencesOpen, setPreferencesOpen] = useState(false);
const [notificationsOpen, setNotificationsOpen] = useState(false);
const [userData, setUserData] = useState<any>(null);
const { user } = useAuth();

// Fetch user data on mount
useEffect(() => {
  if (user?.localAccountId) {
    const response = await getUser(user.localAccountId);
    setUserData(response.data);
  }
}, [user]);

// Refresh after dialog saves
const refreshUserData = async () => {
  const response = await getUser(user.localAccountId);
  setUserData(response.data);
};
```

**Replaces placeholder toast messages** with actual dialog functionality:
- "Edit Preferences" → Opens PreferencesDialog
- "Configure Notifications" → Opens NotificationsDialog
- Both dialogs receive current user data and refresh on save

## Important Decisions

### 1. Separate Dialogs for Preferences vs Notifications
**Why**: Different conceptual groups - content preferences vs delivery preferences
**UX**: Two separate buttons in Settings, two separate modals
**Alternative considered**: Single mega-preferences dialog (rejected - too complex)

### 2. Topics as String Array (not structured)
**Why**: Simple, flexible, supports user-defined topics
**Trade-off**: No validation, no taxonomy, but maximum flexibility
**Future**: Could add structured categories later without breaking schema

### 3. Complete Topic Array Replacement
**Why**: Simpler UX - user sees exactly what they're setting
**Alternative**: Additive-only (rejected - harder to remove topics)
**Implementation**: PUT sends entire topics array, backend replaces

### 4. Disable Dependent Controls
**Why**: Clear visual hierarchy - email notifications must be on for other settings
**UX**: Radio groups and switches disabled (grayed out) when master toggle is off
**Accessibility**: Proper disabled state for screen readers

### 5. Optimistic UI with Callback Pattern
**Why**: Settings page needs to refresh after dialog saves
**Implementation**: `onSaveSuccess` callback triggers parent refresh
**Benefit**: Always shows latest data, no stale state

### 6. Entra ID Integration from Day One
**Why**: User identity from token, no manual email entry
**Implementation**: `get_current_user` dependency provides user_id and email
**Migration**: Handles legacy email-only users (see migration pattern)

## Usage Example

**Opening dialogs from Settings:**
```typescript
<Button onClick={() => setPreferencesOpen(true)}>
  Edit Preferences
</Button>

<PreferencesDialog
  open={preferencesOpen}
  onOpenChange={setPreferencesOpen}
  userId={user?.localAccountId}
  currentTopics={userData?.topics || []}
  currentNewsletterFormat={userData?.preferences?.newsletter_format || "concise"}
  onSaveSuccess={refreshUserData}
/>
```

**Backend - updating user:**
```python
# User wants detailed newsletters daily
PUT /api/users/abc123
{
  "topics": ["technology", "startups", "AI"],
  "preferences": {
    "newsletter_format": "detailed",
    "email_notifications": true,
    "newsletter_frequency": "daily",
    "breaking_news": true
  }
}

Response:
{
  "message": "Preferences updated.",
  "user_id": "abc123"
}
```

## Testing

**Backend tests** (`packages/backend-api/tests/api/test_users.py`):
- ✅ Create new user with topics (Entra ID user)
- ✅ Update topics for existing user (by user_id)
- ✅ Migrate legacy user (found by email, add user_id)
- ✅ Update preferences (partial update)
- ✅ User not found (404 error)
- ✅ Partial updates (topics only, preferences only)

**Key test patterns:**
- Mock `get_current_user` dependency with `app.dependency_overrides`
- Mock MongoDB collections with MagicMock
- Test all three user lookup paths (by id, by email, new)
- Clean up dependency overrides after each test

**Frontend**: Manual testing via Settings page

## Common Issues

**Issue**: Settings page shows stale data after saving preferences
**Solution**: Use `onSaveSuccess` callback to trigger refresh:
```typescript
const refreshUserData = async () => {
  const response = await getUser(user.localAccountId);
  setUserData(response.data);
};
```

**Issue**: User can save preferences with no topics
**Solution**: Frontend validation prevents save:
```typescript
if (topics.length === 0) {
  toast.error("Please add at least one topic");
  return;
}
```

**Issue**: Legacy user without user_id can't be found
**Solution**: Backend tries email lookup if user_id lookup fails (migration pattern)

**Issue**: Email not available from Entra ID token
**Solution**: Backend returns 400 with clear error message:
```python
if not email:
    raise HTTPException(
        status_code=400,
        detail="Email not available in user token. Ensure 'email' scope is included."
    )
```

## Related Knowledge

- [AI Topic Suggestions](./ai-topic-suggestions.md) - Integrated into Preferences dialog
- [Entra ID Authentication](./entra-id-authentication.md) - Provides user identity
- [Entra ID User Migration](../patterns/entra-id-user-migration.md) - Handles legacy users
- [Settings Dialogs Component](../components/settings-dialogs.md) - UI components

## Future Ideas

- [ ] Topic categories/taxonomy (group related topics)
- [ ] Preview newsletter format before saving
- [ ] Notification preview (send test email)
- [ ] Bulk topic import (paste comma-separated list)
- [ ] Topic popularity indicators (how many users follow)
- [ ] Recommended frequency based on content volume
- [ ] Topic aliases (e.g., "AI" = "Artificial Intelligence")
- [ ] Advanced filtering (exclude certain sources within topics)
- [ ] Time-of-day preferences for daily newsletters
- [ ] Digest preview before it's sent
- [ ] Export/import preferences (backup/restore)
- [ ] Shared topic templates (curated starter packs)
