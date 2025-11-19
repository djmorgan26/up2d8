import { ReactNode, useState } from "react";
import { Sidebar } from "./Sidebar";
import { MobileNav } from "./MobileNav";

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen w-full bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900">
      {/* Desktop Sidebar - Hidden on mobile */}
      <Sidebar className="hidden md:flex" />

      {/* Mobile Header - Fixed at top with safe area support */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 glass-card border-b border-white/20 dark:border-white/10 backdrop-blur-xl safe-top">
        <div className="flex items-center justify-between gap-3 px-4 py-3">
          <MobileNav open={mobileMenuOpen} onOpenChange={setMobileMenuOpen} />
          <h1 className="text-lg font-bold gradient-text flex-shrink-0">UP2D8</h1>
          <div className="w-10" /> {/* Spacer for visual balance */}
        </div>
      </div>

      <main className="flex-1 overflow-auto">
        <div className="container mx-auto px-4 pb-4 pt-[72px] md:p-6 max-w-7xl">
          {children}
        </div>
      </main>
    </div>
  );
};
