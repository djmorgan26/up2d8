import React from 'react';
import { Link } from 'react-router-dom';
import { Logo } from '../common/Logo';
import { useAuthStore } from '../../stores/authStore';
import { Button } from '../ui/Button';

export const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuthStore();

  return (
    <header className="bg-white/95 backdrop-blur-sm border-b border-border-light sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to={isAuthenticated ? '/dashboard' : '/'}>
            <Logo />
          </Link>

          <nav className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <span className="text-sm text-text-secondary">
                  {user?.full_name}
                </span>
                <Link to="/preferences">
                  <Button variant="ghost" size="sm">
                    Settings
                  </Button>
                </Link>
                <Button variant="outline" size="sm" onClick={logout}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" size="sm">
                    Login
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button variant="primary" size="sm">
                    Sign Up
                  </Button>
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};
