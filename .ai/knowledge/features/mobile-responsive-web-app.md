---
type: feature
name: Mobile Responsive Web App
status: implemented
created: 2025-11-09
updated: 2025-11-09
files:
  - packages/web-app/src/components/Layout.tsx:1-27
  - packages/web-app/src/components/MobileNav.tsx:1-127
  - packages/web-app/src/components/Sidebar.tsx:14-45
  - packages/web-app/src/index.css:161-177
  - packages/web-app/src/pages/Dashboard.tsx:57-74
  - packages/web-app/src/pages/Feeds.tsx:111-120
  - packages/web-app/src/pages/Chat.tsx:69-77
  - packages/web-app/src/pages/Settings.tsx:70-78
related:
  - ../frontend/web-app-structure.md
tags: [responsive, mobile, ui, tailwind, shadcn-ui, hamburger-menu]
---

# Mobile Responsive Web App

## What It Does
Transforms the desktop-only web app into a fully responsive experience that works seamlessly on mobile devices (Safari, Chrome) while preserving the beautiful glassmorphism desktop design. Implements a mobile drawer navigation pattern with hamburger menu for screens under 768px.

## How It Works
The feature uses Tailwind CSS breakpoints (`md:` = 768px) to show/hide UI elements and shadcn/ui's Sheet component for mobile navigation:

**Key files:**
- `packages/web-app/src/components/Layout.tsx:1-27` - Main layout with conditional rendering
- `packages/web-app/src/components/MobileNav.tsx:1-127` - Mobile drawer navigation
- `packages/web-app/src/components/Sidebar.tsx:14-45` - Desktop sidebar with responsive className
- `packages/web-app/src/index.css:161-177` - Mobile performance optimizations

### Architecture

**Desktop (≥768px):**
```
┌─────────────────────────────────┐
│ Sidebar (256px) │ Main Content  │
│  - Fixed width  │               │
│  - Always shown │               │
└─────────────────────────────────┘
```

**Mobile (<768px):**
```
┌───────────────────────────┐
│ 🍔 Hamburger  Main Content│
│                            │
│  (Sidebar hidden)          │
└────────────────────────────┘

   (Tap hamburger)
        ↓
┌────────────────────────────┐
│ ← Sidebar Drawer    [✕]   │
│   - Navigation links        │
│   - User profile            │
│   - Login/Logout            │
└────────────────────────────┘
```

### Implementation Strategy

1. **Hide Desktop Sidebar on Mobile**
   ```tsx
   <Sidebar className="hidden md:flex" />
   ```

2. **Add Mobile Hamburger Menu**
   ```tsx
   <MobileNav open={mobileMenuOpen} onOpenChange={setMobileMenuOpen} />
   ```

3. **Responsive Container Padding**
   ```tsx
   <div className="container mx-auto p-3 md:p-6 max-w-7xl">
   ```

4. **Responsive Typography & Icons**
   ```tsx
   <h1 className="text-2xl md:text-3xl font-bold">
   <Icon className="h-5 w-5 md:h-6 md:w-6" />
   ```

5. **Mobile Performance Optimizations**
   ```css
   @media (max-width: 767px) {
     .glass-card {
       backdrop-blur-md; /* Reduced from xl for performance */
     }
     button, a {
       min-height: 44px; /* Touch-friendly targets */
     }
   }
   ```

## Important Decisions

- **Breakpoint at 768px**: Standard `md:` breakpoint balances tablet/mobile distinction
  - Tablets (iPad) show desktop layout
  - Phones show mobile drawer

- **shadcn/ui Sheet Component**: Chosen over custom drawer because:
  - Already installed in the project
  - Accessible by default (keyboard navigation, focus trap)
  - Smooth animations and overlay built-in
  - Consistent with other modals in the app

- **Preserve Desktop Design**: Zero changes to desktop layout
  - Desktop users see no difference
  - All glassmorphism effects maintained
  - 256px sidebar width unchanged

- **Reduce Mobile Blur Effects**: Performance optimization
  - Desktop: `backdrop-blur-2xl` (24px blur)
  - Mobile: `backdrop-blur-md` (8px blur)
  - Prevents lag on older devices, especially iOS Safari

## Usage Example

**Layout.tsx - Responsive Layout:**
```tsx
export const Layout = ({ children }: LayoutProps) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen w-full bg-gradient-to-br ...">
      {/* Desktop Sidebar - Hidden on mobile */}
      <Sidebar className="hidden md:flex" />

      {/* Mobile Navigation */}
      <MobileNav open={mobileMenuOpen} onOpenChange={setMobileMenuOpen} />

      <main className="flex-1 overflow-auto">
        <div className="container mx-auto p-3 md:p-6 max-w-7xl">
          {children}
        </div>
      </main>
    </div>
  );
};
```

**MobileNav.tsx - Sheet Drawer:**
```tsx
export const MobileNav = ({ open, onOpenChange }: MobileNavProps) => {
  return (
    <div className="md:hidden fixed top-4 left-4 z-50">
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetTrigger asChild>
          <Button variant="outline" size="icon" className="glass-card">
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="glass-sidebar w-64 p-6">
          {/* Same content as desktop Sidebar */}
        </SheetContent>
      </Sheet>
    </div>
  );
};
```

**Responsive Page Headers:**
```tsx
<div className="flex items-center justify-between flex-wrap gap-4">
  <div className="flex items-center gap-3">
    <div className="h-10 w-10 md:h-12 md:w-12 rounded-xl ...">
      <Icon className="h-5 w-5 md:h-6 md:w-6" />
    </div>
    <div>
      <h1 className="text-2xl md:text-3xl font-bold">Title</h1>
      <p className="text-sm text-muted-foreground hidden md:block">
        Subtitle
      </p>
    </div>
  </div>
</div>
```

## Testing

**Testing Checklist:**
- [x] Chrome DevTools mobile emulation (iPhone, Android)
- [ ] Real iOS Safari testing (recommended)
- [ ] Real Android Chrome testing (recommended)
- [x] Dark mode on mobile
- [ ] Landscape orientation
- [ ] Notched devices (safe-area-inset)
- [x] Desktop layout unchanged
- [x] Hamburger menu opens/closes
- [x] Navigation links work in drawer
- [x] Touch targets ≥44px
- [x] Drawer closes on navigation

**Test on these viewports:**
- 320px (iPhone SE)
- 375px (iPhone 12/13)
- 390px (iPhone 14)
- 768px (iPad Mini - desktop)
- 1024px (Desktop)

## Common Issues

### Issue: Sidebar still showing on mobile
**Cause**: `hidden md:flex` classes not applied to Sidebar

**Solution**: Update Sidebar instantiation:
```tsx
<Sidebar className="hidden md:flex" />
```

### Issue: Hamburger menu not appearing
**Cause**: MobileNav not added or has wrong responsive class

**Solution**: Ensure fixed positioning and mobile-only display:
```tsx
<div className="md:hidden fixed top-4 left-4 z-50">
```

### Issue: Glass effects lagging on mobile
**Cause**: High blur values are intensive for mobile GPUs

**Solution**: Add mobile-specific blur reduction in CSS:
```css
@media (max-width: 767px) {
  .glass-card {
    backdrop-blur-md; /* Instead of backdrop-blur-xl */
  }
}
```

### Issue: Touch targets too small
**Cause**: Buttons/links designed for mouse clicks

**Solution**: Enforce 44px minimum:
```css
@media (max-width: 767px) {
  button, a {
    min-height: 44px;
  }
}
```

## Related Knowledge
- [Web App Structure](../frontend/web-app-structure.md) - Overall web app architecture

## Future Ideas
- [ ] Add swipe-to-open gesture for drawer
- [ ] Implement safe-area-inset for notched devices
- [ ] Add haptic feedback on mobile navigation
- [ ] Progressive Web App (PWA) manifest for mobile install
- [ ] Test and optimize for landscape orientation
- [ ] Add pull-to-refresh gesture on mobile
- [ ] Consider bottom navigation bar for mobile (alternative to drawer)
- [ ] Add mobile-specific font sizes for better readability
- [ ] Test accessibility with screen readers on mobile
