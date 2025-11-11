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

      <main className="flex-1 overflow-auto">
        <div className="container mx-auto px-3 pb-3 pt-6 md:p-6 max-w-7xl">
          {/* Mobile Navigation - Inline at top */}
          <div className="md:hidden mb-6">
            <MobileNav open={mobileMenuOpen} onOpenChange={setMobileMenuOpen} />
          </div>

          {children}
        </div>
      </main>
    </div>
  );
};
