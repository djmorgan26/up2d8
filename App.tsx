
import React, { useState } from 'react';
import { Logo } from './components/Logo';
import Nav from './components/Nav';
import ChatPage from './pages/ChatPage';
import BrowsePage from './pages/BrowsePage';
import SubscribePage from './pages/SubscribePage';
import { LandingPage } from './pages/LandingPage';
import { useTheme } from './hooks/useTheme';

// Define the available pages
export type Page = 'chat' | 'browse' | 'subscribe';

const App: React.FC = () => {
  const [activePage, setActivePage] = useState<Page>('chat');
  const [appLaunched, setAppLaunched] = useState(false);
  const { theme } = useTheme();

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
    <div className="min-h-screen flex flex-col items-center justify-center p-2 sm:p-4 font-sans transition-colors duration-300" style={{ backgroundColor: 'var(--background)' }}>
      <div className="w-full max-w-3xl h-[98vh] md:h-[95vh] flex flex-col border rounded-2xl shadow-2xl" style={{ borderColor: 'var(--border)', backgroundColor: 'var(--surface)' }}>
        <header className="p-4 border-b flex justify-between items-center flex-shrink-0" style={{ borderColor: 'var(--border)' }}>
          <div className="text-left">
            <h1 className="text-xl font-bold tracking-wide" style={{ color: 'var(--text-primary)' }}>UP2D8 Digest</h1>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Your AI-powered news assistant</p>
          </div>
          <div className="flex-grow"></div> {/* This will push the logo to the right */}
          <Logo />
        </header>
        <Nav activePage={activePage} setActivePage={setActivePage} />
        <main className="flex-grow overflow-y-auto relative">
          {renderPage()}
        </main>
      </div>
       <footer className="text-center pt-4 text-xs" style={{ color: 'var(--text-secondary)' }}>
          Powered by Gemini
      </footer>
    </div>
  );
};

export default App;
