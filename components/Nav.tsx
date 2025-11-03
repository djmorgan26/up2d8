
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
    <nav className="border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
      <ul className="flex items-center justify-center -mb-px">
        {navItems.map(item => (
          <li key={item.id} className="flex-1 text-center">
            <button
              onClick={() => setActivePage(item.id)}
              className={`w-full p-4 text-sm font-medium border-b-2 transition-colors duration-200 focus:outline-none focus:ring-1 focus:ring-inset focus:ring-blue-500 ${
                activePage === item.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
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
