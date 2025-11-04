
import React from 'react';
import { Page } from '../App';

interface NavProps {
  activePage: Page;
  setActivePage: (page: Page) => void;
}

const Nav: React.FC<NavProps> = ({ activePage, setActivePage }) => {
  const navItems: { id: Page, label: string }[] = [
    { id: 'chat', label: 'Chat' },
    { id: 'browse', label: 'Browse' },
    { id: 'subscribe', label: 'Subscribe' },
  ];

  return (
    <nav className="border-b flex-shrink-0" style={{ borderColor: 'var(--border)' }}>
      <ul className="flex items-center justify-center -mb-px">
        {navItems.map(item => (
          <li key={item.id} className="flex-1 text-center">
            <button
              onClick={() => setActivePage(item.id)}
              className={`w-full p-4 text-sm font-medium border-b-2 transition-colors duration-200 focus:outline-none focus:ring-1 focus:ring-inset`}
              style={{
                borderColor: activePage === item.id ? 'var(--primary)' : 'transparent',
                color: activePage === item.id ? 'var(--primary)' : 'var(--text-secondary)',
                ringColor: 'var(--primary)'
              }}
               aria-current={activePage === item.id ? 'page' : undefined}
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Nav;
