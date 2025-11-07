
import React, { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Logo } from './components/Logo';
import Nav from './components/Nav';
import ChatPage from './pages/ChatPage';
import BrowsePage from './pages/BrowsePage';
import SubscribePage from './pages/SubscribePage';
import { LandingPage } from './pages/LandingPage';
import { useTheme } from './hooks/useTheme';
import ContextPrompt from './components/ContextPrompt';

const App: React.FC = () => {
  const { theme } = useTheme();
  const navigate = useNavigate();
  const showNav = true; // Nav is always shown now

  const handleLaunch = () => {
    navigate('/chat'); // Navigate to chat page after launching
  };

  return (
    <div className="min-h-screen flex flex-col items-center p-2 sm:p-4 font-sans transition-colors duration-300" style={{ backgroundColor: 'var(--background)' }}>
      <Routes>
        <Route path="/" element={<LandingPage onLaunch={handleLaunch} />} />
                <Route path="/*" element={
                  <>
                    <div className="w-full max-w-3xl flex flex-col border rounded-2xl shadow-2xl" style={{ borderColor: 'var(--border)', backgroundColor: 'var(--surface)' }}>
                      <header className="p-4 border-b flex justify-between items-center flex-shrink-0" style={{ borderColor: 'var(--border)' }}>
                        <div className="text-left">
                          <h1 className="text-xl font-bold tracking-wide" style={{ color: 'var(--text-primary)' }}>UP2D8 Digest</h1>
                          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Your AI-powered news assistant</p>
                        </div>
                        <div className="flex-grow"></div>
                        <Logo />
                      </header>
                      <main className="flex-grow overflow-y-auto relative pb-20">
                        {/* Example Context Prompt - This would be dynamic in a real app */}
                        <ContextPrompt
                          title="Welcome Back!"
                          message="Select a tab below to navigate, or use the chat to get your daily digest."
                        />
                                    <Routes className="h-full">
                                      <Route path="/chat" element={<ChatPage />} />
                                      <Route path="/browse" element="<BrowsePage />" />
                                      <Route path="/subscribe" element="<SubscribePage />" />
                                    </Routes>
                                    <footer className="text-center pt-4 text-xs" style={{ color: 'var(--text-secondary)' }}>
                                      Powered by Gemini
                                    </footer>
                                  </main>                    </div>
                    {/* Navigation Bar with conditional visibility and animation */}
                    <Nav showNav={showNav} />
                  </>
                } />
              </Routes>
            </div>
          );
        };

export default App;
