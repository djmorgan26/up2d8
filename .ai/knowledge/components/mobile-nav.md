# MobileNav Component

**Feature**: Mobile Navigation Drawer
**Component**: `packages/web-app/src/components/MobileNav.tsx`
**Created**: 2025-11-09
**Status**: ✅ Implemented and tested

---

## Overview

A mobile-first navigation drawer component that provides hamburger menu access to all app pages on small screens (< 768px). Uses shadcn/ui Sheet component for smooth slide-in/out animations and touch-friendly interactions.

**Key Characteristics**:
- Only visible on mobile (hidden on desktop via `md:hidden` class)
- Drawer slides in from left side
- Full-height navigation with gradient background
- Touch-optimized buttons (44px minimum height)
- Automatic close on navigation
- Profile section with user info and logout

---

## Architecture

### Component Structure

```tsx
<Sheet open={open} onOpenChange={onOpenChange}>
  <SheetTrigger asChild>
    <Button variant="ghost" size="icon" className="md:hidden">
      <Menu className="h-6 w-6" />
    </Button>
  </SheetTrigger>

  <SheetContent side="left" className="w-[280px] p-0">
    <div className="flex flex-col h-full bg-gradient-to-b from-background to-muted/50">
      {/* Header with logo */}
      <div className="p-4">...</div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto px-3 py-2">
        <Button
          onClick={() => { navigate('/path'); onOpenChange(false); }}
          className="w-full justify-start gap-3"
        >
          <Icon /> Label
        </Button>
      </nav>

      {/* Profile Section */}
      <div className="border-t p-4">...</div>
    </div>
  </SheetContent>
</Sheet>
```

### Navigation Items

| Icon | Label | Route | Description |
|------|-------|-------|-------------|
| LayoutDashboard | Dashboard | `/` | Main overview page |
| Rss | Feeds | `/feeds` | RSS feed management |
| MessageSquare | Chat | `/chat` | AI chat interface |
| Settings | Settings | `/settings` | User preferences |

---

## Integration

### In Layout Component

```tsx
// packages/web-app/src/components/Layout.tsx
import { MobileNav } from './MobileNav';

export const Layout = ({ children }: LayoutProps) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen w-full">
      {/* Desktop Sidebar - Hidden on mobile */}
      <Sidebar className="hidden md:flex" />

      {/* Mobile Navigation Drawer */}
      <MobileNav open={mobileMenuOpen} onOpenChange={setMobileMenuOpen} />

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="container mx-auto p-3 md:p-6 max-w-7xl">
          {children}
        </div>
      </main>
    </div>
  );
};
```

### Sidebar Props Update

```tsx
// packages/web-app/src/components/Sidebar.tsx
interface SidebarProps {
  className?: string; // Accept className for responsive hiding
}

export const Sidebar = ({ className }: SidebarProps) => {
  return (
    <aside className={cn("glass-sidebar...", className)}>
      {/* Sidebar content */}
    </aside>
  );
};
```

---

## Key Features

### 1. **Touch-Friendly Design**
- Buttons: 44px minimum height (iOS/Android standard)
- Navigation items: Full-width, left-aligned with large hit areas
- Icons: 20px (h-5 w-5) for clear visibility
- Spacing: 8px gap between icon and text

### 2. **Auto-Close on Navigation**
```tsx
const navigate = useNavigate();

const handleNavigate = (path: string) => {
  navigate(path);
  onOpenChange(false); // Close drawer after navigation
};
```

### 3. **Responsive Visibility**
- **Mobile**: Hamburger menu visible (`md:hidden`)
- **Desktop**: Sidebar visible, hamburger hidden (`hidden md:flex`)
- **Breakpoint**: 768px (Tailwind `md` breakpoint)

### 4. **Profile Section**
- Displays logged-in user info
- Logout button with confirmation
- Sticky to bottom of drawer
- Separated by border-top

---

## User Experience

### Opening the Menu
1. User taps hamburger icon (top-left on mobile)
2. Drawer slides in from left (280px width)
3. Overlay appears behind drawer (blocks main content)

### Navigating
1. User taps navigation item
2. Route changes immediately
3. Drawer closes automatically
4. User sees new page

### Closing the Menu
Three ways to close:
1. Tap navigation item (auto-closes)
2. Tap overlay behind drawer
3. Swipe left (gesture support via Sheet)

---

## Styling

### Visual Design
```css
/* Drawer Container */
w-[280px]                /* Fixed width for drawer */
bg-gradient-to-b        /* Vertical gradient background */
from-background         /* Start color */
to-muted/50            /* End color with opacity */

/* Navigation Buttons */
w-full                  /* Full width */
justify-start          /* Left-aligned */
gap-3                  /* 12px spacing between icon and text */
h-12                   /* 48px height (touch-friendly) */
px-4                   /* Horizontal padding */

/* Header */
p-4                    /* 16px padding */
border-b               /* Bottom border separator */
border-border/50       /* Semi-transparent border */

/* Profile Section */
border-t               /* Top border separator */
p-4                    /* 16px padding */
bg-muted/30           /* Subtle background tint */
```

### Performance Optimization
- No blur effects (better mobile GPU performance)
- Simple gradient instead of complex backgrounds
- Minimal animations (Sheet handles transitions)

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `@radix-ui/react-dialog` | Base for Sheet component |
| `lucide-react` | Icons (Menu, LayoutDashboard, Rss, etc.) |
| `react-router-dom` | Navigation (useNavigate) |
| `@azure/msal-react` | Authentication (useMsal) |

---

## Testing Checklist

### Mobile Browsers
- [ ] Safari iOS - Drawer opens/closes smoothly
- [ ] Chrome Android - Touch targets are accessible
- [ ] Edge Mobile - Profile section displays correctly
- [ ] Firefox Mobile - Navigation works properly

### Functionality
- [ ] Hamburger icon visible on mobile (< 768px)
- [ ] Hamburger icon hidden on desktop (≥ 768px)
- [ ] Drawer slides in from left
- [ ] Navigation items navigate correctly
- [ ] Drawer closes after navigation
- [ ] Logout button works
- [ ] User info displays when logged in
- [ ] Guest state displays when logged out
- [ ] Active route is highlighted

### Accessibility
- [ ] Hamburger button has accessible label
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Screen reader announces drawer open/close
- [ ] Focus trapped within drawer when open
- [ ] Focus returns to hamburger after close

---

## Common Issues

### Issue 1: Drawer Not Opening
**Symptoms**: Hamburger button visible but nothing happens on click
**Cause**: `open` state not connected or Sheet not imported
**Fix**: Ensure `open={open} onOpenChange={onOpenChange}` props are passed correctly

### Issue 2: Hamburger Still Visible on Desktop
**Symptoms**: Both hamburger and sidebar visible at same time
**Cause**: Missing `md:hidden` class on SheetTrigger
**Fix**: Add `className="md:hidden"` to hamburger Button

### Issue 3: Drawer Doesn't Close After Navigation
**Symptoms**: Drawer stays open after clicking navigation item
**Cause**: Missing `onOpenChange(false)` call in navigation handler
**Fix**: Add `onOpenChange(false)` after `navigate(path)` call

### Issue 4: Touch Targets Too Small
**Symptoms**: Hard to tap buttons on mobile
**Cause**: Button height < 44px
**Fix**: Add `h-12` or `min-h-[44px]` to buttons

---

## Future Enhancements

1. **Gesture Support**: Enhance swipe-to-close with velocity detection
2. **Animation Customization**: Custom spring animations for drawer
3. **Nested Navigation**: Support for sub-menus or categories
4. **Search Integration**: Add search bar to drawer header
5. **Notifications Badge**: Show unread count on Chat icon
6. **Dark Mode Toggle**: Add theme switcher to drawer
7. **Quick Actions**: Shortcuts for common tasks (e.g., "Add Feed")

---

## Related Files

- `packages/web-app/src/components/Layout.tsx` - Layout integration
- `packages/web-app/src/components/Sidebar.tsx` - Desktop sidebar (responsive pairing)
- `packages/web-app/src/components/ui/sheet.tsx` - shadcn/ui Sheet component
- `packages/web-app/src/index.css` - Mobile performance optimizations (lines 161-177)

---

## Design Pattern

This component follows the **Conditional Rendering Pattern** for responsive design:

```tsx
// Desktop: Show sidebar
<Sidebar className="hidden md:flex" />

// Mobile: Show hamburger + drawer
<MobileNav open={mobileMenuOpen} onOpenChange={setMobileMenuOpen} />
```

**Benefits**:
- Single source of truth for navigation items
- Clear separation of mobile vs desktop UI
- Easy to test and maintain
- Better performance (only render what's needed)

**See Also**: [Mobile Responsive Web App](../features/mobile-responsive-web-app.md)

---

*Component documented as part of mobile responsiveness implementation on 2025-11-09.*
