
import React from 'react';
import { NavLink } from 'react-router-dom';

// Placeholder icons - In a real app, these would be imported from an icon library
const ChatIcon = () => <span className="text-xl">💬</span>;
const BrowseIcon = () => <span className="text-xl">📚</span>;
const SubscribeIcon = () => <span className="text-xl">✨</span>;

interface NavProps {
  showNav: boolean;
}

const Nav: React.FC<NavProps> = ({ showNav }) => {
  const navItems = [
    { path: '/chat', label: 'Chat', icon: ChatIcon },
    { path: '/browse', label: 'Browse', icon: BrowseIcon },
    { path: '/subscribe', label: 'Subscribe', icon: SubscribeIcon },
  ];

  return (
    // Fixed bottom navigation bar
    <nav className={`fixed bottom-0 left-0 right-0 bg-surface z-50 transform transition-transform duration-300 ease-in-out ${showNav ? 'translate-y-0' : 'translate-y-full'}`}>
      <ul className="flex justify-evenly h-16">
        {navItems.map(item => (
          <li key={item.path} className="flex-1">
            <NavLink
              to={item.path}
              className="flex flex-col items-center justify-center h-full text-xs font-medium transition-colors duration-200"
              style={({ isActive }) => ({
                color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
              })}
            >
              {/* Icon */}
              <item.icon />
              {/* Label */}
              <span className="mt-1" style={{ fontWeight: '500' }}>{item.label}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Nav;
