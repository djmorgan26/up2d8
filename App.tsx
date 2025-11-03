
import React, { useState } from 'react';
import { ThemeSwitcher } from './components/ThemeSwitcher';
import Nav from './components/Nav';
import ChatPage from './pages/ChatPage';
import BrowsePage from './pages/BrowsePage';
import SubscribePage from './pages/SubscribePage';
import { LandingPage } from './pages/LandingPage';

// Define the available pages
export type Page = 'chat' | 'browse' | 'subscribe';

const App: React.FC = () => {
  const [activePage, setActivePage] = useState<Page>('chat');
  const [appLaunched, setAppLaunched] = useState(false);

  const renderPage = () => {
    switch (activePage) {
      case 'browse':
        return <BrowsePage />;
      case 'subscribe':
        return <SubscribePage />;
      case 'chat':
      default:
        return <ChatPage />;
    }
  };

  if (!appLaunched) {
    return <LandingPage onLaunch={() => setAppLaunched(true)} />;
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white min-h-screen flex flex-col items-center justify-center p-2 sm:p-4 font-sans transition-colors duration-300">
      <div className="w-full max-w-3xl h-[98vh] md:h-[95vh] flex flex-col border border-gray-200 dark:border-gray-700 rounded-2xl shadow-2xl bg-white dark:bg-gray-800">
        <header className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center flex-shrink-0">
          <div className="text-left">
            <h1 className="text-xl font-bold tracking-wide">UP2D8 Digest</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">Your AI-powered news assistant</p>
          </div>
          <ThemeSwitcher />
        </header>
        <Nav activePage={activePage} setActivePage={setActivePage} />
        <main className="flex-grow overflow-y-auto relative">
          {renderPage()}
        </main>
      </div>
       <footer className="text-center pt-4 text-gray-500 dark:text-gray-400 text-xs">
          Powered by Gemini
      </footer>
    </div>
  );
};

export default App;
