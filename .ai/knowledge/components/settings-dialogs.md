---
type: component
name: Settings Dialogs (Preferences & Notifications)
status: implemented
created: 2025-11-09
updated: 2025-11-09
files:
  - packages/web-app/src/components/PreferencesDialog.tsx
  - packages/web-app/src/components/NotificationsDialog.tsx
related:
  - .ai/knowledge/features/user-preferences-management.md
  - .ai/knowledge/features/ai-topic-suggestions.md
  - .ai/knowledge/frontend/web-app-structure.md
tags: [components, dialogs, settings, ui, shadcn, frontend]
---

# Settings Dialogs (Preferences & Notifications)

## What It Does

Two reusable modal dialog components for managing user preferences and notification settings. Built with shadcn/ui components, fully controlled, and integrated with backend API. Used in Settings page to provide focused, task-oriented interfaces for different types of settings.

## How It Works

### PreferencesDialog (`packages/web-app/src/components/PreferencesDialog.tsx`)

**Props interface:**
```typescript
interface PreferencesDialogProps {
  open: boolean;                        // Dialog visibility
  onOpenChange: (open: boolean) => void; // Open/close callback
  userId?: string;                       // Current user ID
  currentTopics?: string[];              // Existing topics
  currentNewsletterFormat?: "concise" | "detailed";
  onSaveSuccess?: () => void;           // Callback after successful save
}
```

**Component structure:**
1. **Topics Section**:
   - Input field with "Add" button
   - Topic badges with X remove button
   - Empty state message
   - Enter key support for quick adding

2. **AI Topic Discovery Section**:
   - Search input for topic ideas
   - "Suggest" button with Sparkles icon
   - AI-generated suggestion badges (click to add)
   - Loading state during suggestion generation

3. **Newsletter Format Section**:
   - Radio group (Concise vs Detailed)
   - Descriptive labels for each option

4. **Dialog Footer**:
   - Cancel button (closes without saving)
   - Save button (disabled during save, shows "Saving...")

**State management:**
```typescript
const [topics, setTopics] = useState<string[]>(currentTopics);
const [newTopic, setNewTopic] = useState("");
const [newsletterFormat, setNewsletterFormat] = useState(currentNewsletterFormat);
const [saving, setSaving] = useState(false);
const [suggestions, setSuggestions] = useState<string[]>([]);
const [loadingSuggestions, setLoadingSuggestions] = useState(false);
const [searchQuery, setSearchQuery] = useState("");
```

**Key behaviors:**
- **Duplicate prevention**: Can't add topic that already exists
- **Validation**: Requires at least one topic to save
- **Optimistic filtering**: Removes added suggestions from suggestion list
- **Error handling**: Shows toast on API failure, keeps dialog open
- **Success flow**: Toast → callback → close dialog

### NotificationsDialog (`packages/web-app/src/components/NotificationsDialog.tsx`)

**Props interface:**
```typescript
interface NotificationsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  userId?: string;
  currentSettings?: {
    emailNotifications?: boolean;
    newsletterFrequency?: "daily" | "weekly" | "monthly";
    breakingNews?: boolean;
  };
  onSaveSuccess?: () => void;
}
```

**Component structure:**
1. **Email Notifications Toggle**:
   - Master switch for all email features
   - Descriptive subtext
   - Controls other settings' enabled state

2. **Newsletter Frequency**:
   - Radio group (Daily / Weekly / Monthly)
   - Descriptive labels with timing info
   - Disabled when email notifications off

3. **Breaking News Toggle**:
   - Switch for instant alerts
   - Descriptive subtext
   - Disabled when email notifications off

4. **Dialog Footer**:
   - Same pattern as PreferencesDialog

**State management:**
```typescript
const [emailNotifications, setEmailNotifications] = useState(currentSettings.emailNotifications ?? true);
const [newsletterFrequency, setNewsletterFrequency] = useState(currentSettings.newsletterFrequency ?? "daily");
const [breakingNews, setBreakingNews] = useState(currentSettings.breakingNews ?? false);
const [saving, setSaving] = useState(false);
```

**Key behaviors:**
- **Cascade disable**: When email notifications off, frequency and breaking news disabled
- **Default values**: Sensible defaults (email on, daily frequency, breaking news off)
- **No validation**: All combinations valid (email off is valid)
- **Consistent save flow**: Same pattern as Preferences dialog

## Important Decisions

### 1. Controlled Component Pattern
**Why**: Parent (Settings page) needs to control visibility and refresh data
**Implementation**: Open state passed as prop, changes via onOpenChange callback
**Benefit**: Can be used anywhere, not tied to Settings page

### 2. Current Values as Props
**Why**: Dialogs don't fetch their own data, receive current state
**Benefit**: Faster open (no loading spinner), single source of truth
**Trade-off**: Parent must manage data fetching and refresh

### 3. Callback for Success, Not Direct State Update
**Why**: Parent knows how to refresh data (may need full user object)
**Implementation**: `onSaveSuccess()` callback triggers parent's refresh logic
**Alternative rejected**: Return updated data from save (backend doesn't return full user)

### 4. shadcn/ui Components Throughout
**Why**: Consistent design system, accessible, well-tested
**Components used**: Dialog, Button, Input, Label, Switch, RadioGroup, Badge
**Benefit**: Minimal custom styling, built-in accessibility

### 5. Separate State for Each Field
**Why**: Individual control over each setting, easier validation
**Alternative rejected**: Single object state (harder to update, more boilerplate)
**Trade-off**: More useState calls, but simpler logic

### 6. Inline AI Suggestions in Preferences
**Why**: Topic discovery is part of topic management workflow
**Alternative rejected**: Separate suggestion dialog (too many modals)
**UX**: Bordered section visually separates discovery from management

## Usage Example

**In Settings page:**
```typescript
import { PreferencesDialog } from "@/components/PreferencesDialog";
import { NotificationsDialog } from "@/components/NotificationsDialog";
import { useAuth } from "@/hooks/useAuth";
import { getUser } from "@/lib/api";

const Settings = () => {
  const [preferencesOpen, setPreferencesOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userData, setUserData] = useState<any>(null);
  const { user } = useAuth();

  // Fetch user data
  useEffect(() => {
    if (user?.localAccountId) {
      const response = await getUser(user.localAccountId);
      setUserData(response.data);
    }
  }, [user]);

  // Refresh after save
  const refreshUserData = async () => {
    const response = await getUser(user.localAccountId);
    setUserData(response.data);
  };

  return (
    <div>
      <Button onClick={() => setPreferencesOpen(true)}>
        Edit Preferences
      </Button>
      <Button onClick={() => setNotificationsOpen(true)}>
        Configure Notifications
      </Button>

      <PreferencesDialog
        open={preferencesOpen}
        onOpenChange={setPreferencesOpen}
        userId={user?.localAccountId}
        currentTopics={userData?.topics || []}
        currentNewsletterFormat={userData?.preferences?.newsletter_format || "concise"}
        onSaveSuccess={refreshUserData}
      />

      <NotificationsDialog
        open={notificationsOpen}
        onOpenChange={setNotificationsOpen}
        userId={user?.localAccountId}
        currentSettings={{
          emailNotifications: userData?.preferences?.email_notifications,
          newsletterFrequency: userData?.preferences?.newsletter_frequency,
          breakingNews: userData?.preferences?.breaking_news,
        }}
        onSaveSuccess={refreshUserData}
      />
    </div>
  );
};
```

## Component APIs

### PreferencesDialog

**Required props:**
- `open: boolean` - Whether dialog is visible
- `onOpenChange: (open: boolean) => void` - Open/close handler

**Optional props:**
- `userId?: string` - User ID for save (required to actually save)
- `currentTopics?: string[]` - Initial topics (defaults to [])
- `currentNewsletterFormat?: "concise" | "detailed"` - Initial format (defaults to "concise")
- `onSaveSuccess?: () => void` - Called after successful save

### NotificationsDialog

**Required props:**
- `open: boolean`
- `onOpenChange: (open: boolean) => void`

**Optional props:**
- `userId?: string`
- `currentSettings?: object` - Initial notification settings
- `onSaveSuccess?: () => void`

## Styling

**Both dialogs use:**
- `sm:max-w-[500px]` - Max width on larger screens
- `space-y-6` / `space-y-3` - Consistent vertical spacing
- `py-4` - Padding in content area
- `text-muted-foreground` - Secondary text color for descriptions

**Interactive elements:**
- Badges use `gap-1 px-3 py-1` for consistent padding
- Hover states on suggestion badges (`hover:bg-primary/10`)
- Disabled states properly styled (grayed out, cursor-not-allowed)

## Common Issues

**Issue**: Dialog doesn't show updated data after external changes
**Solution**: Parent must call `getUser()` after external updates

**Issue**: Saving with no userId shows generic error
**Solution**: Validation in handleSave:
```typescript
if (!userId) {
  toast.error("User not authenticated");
  return;
}
```

**Issue**: User closes dialog without saving, local state persists
**Solution**: State initialized from props, so reopening resets to current values

**Issue**: Suggestion loading state doesn't show
**Solution**: `loadingSuggestions` state controls button text and disabled state

## Testing

**Manual testing checklist:**
- [ ] Open/close both dialogs
- [ ] Add/remove topics in Preferences
- [ ] Get AI suggestions with query
- [ ] Get AI suggestions without query
- [ ] Add suggestion to topics
- [ ] Change newsletter format
- [ ] Toggle email notifications (verify cascade disable)
- [ ] Change newsletter frequency
- [ ] Toggle breaking news
- [ ] Save preferences (verify success toast)
- [ ] Save notifications (verify success toast)
- [ ] Cancel without saving (verify no changes)
- [ ] Validation: Try to save with no topics

## Related Knowledge

- [User Preferences Management](../features/user-preferences-management.md) - Feature these components support
- [AI Topic Suggestions](../features/ai-topic-suggestions.md) - AI integration in Preferences dialog
- [Web App Structure](../frontend/web-app-structure.md) - Overall frontend architecture

## Future Ideas

- [ ] Keyboard shortcuts (Cmd+S to save, Esc to cancel)
- [ ] Unsaved changes warning on close
- [ ] Undo/redo for topic changes
- [ ] Drag-to-reorder topics (priority order)
- [ ] Topic usage stats (articles per topic)
- [ ] Notification preview (show example email)
- [ ] Bulk topic operations (remove all, import list)
- [ ] Topic search/filter in Preferences (for long lists)
- [ ] Dark mode specific styling (already inherits theme)
- [ ] Animation on suggestion add (smooth transition)
- [ ] Mobile optimization (full-screen on small screens)
