import { Home, Rss, MessageSquare, Settings, LogIn, LogOut, User } from "lucide-react";
import { NavLink } from "./NavLink";
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "@/config/msalConfig";
import { Button } from "./ui/button";
import { useNavigate } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

interface SidebarProps {
  className?: string;
}

export const Sidebar = ({ className = "" }: SidebarProps) => {
  const { instance, accounts } = useMsal();
  const navigate = useNavigate();
  const isAuthenticated = accounts.length > 0;
  const user = accounts[0];

  const handleLogin = async () => {
    try {
      await instance.loginPopup(loginRequest);
      navigate("/onboarding");
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const handleLogout = () => {
    instance.logoutPopup();
  };

  const navItems = [
    { to: "/", label: "Dashboard", icon: Home },
    { to: "/feeds", label: "Feeds", icon: Rss },
    { to: "/chat", label: "Chat", icon: MessageSquare },
    { to: "/settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside className={`glass-sidebar w-64 min-h-screen p-6 flex flex-col animate-slide-in ${className}`}>
      <div className="mb-8">
        <h1 className="text-3xl font-bold gradient-text">UP2D8</h1>
        <p className="text-sm text-muted-foreground mt-1">Your personalized news digest</p>
      </div>

      <nav className="flex-1 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-foreground/80 hover:text-foreground hover:bg-white/20 dark:hover:bg-white/5"
            activeClassName="bg-white/30 dark:bg-white/10 text-foreground font-medium shadow-sm"
          >
            <item.icon className="h-5 w-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto pt-6 border-t border-white/20 dark:border-white/10">
        {isAuthenticated ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="w-full justify-start gap-3 px-4 py-3 h-auto">
                <div className="h-8 w-8 rounded-full bg-gradient-to-r from-primary to-accent flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
                <div className="flex-1 text-left overflow-hidden">
                  <p className="text-sm font-medium truncate">{user?.name || "User"}</p>
                  <p className="text-xs text-muted-foreground truncate">{user?.username}</p>
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 glass-card">
              <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
                <LogOut className="mr-2 h-4 w-4" />
                <span>Logout</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <Button
            onClick={handleLogin}
            className="w-full gradient-primary text-white shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <LogIn className="mr-2 h-4 w-4" />
            Login
          </Button>
        )}
      </div>
    </aside>
  );
};
