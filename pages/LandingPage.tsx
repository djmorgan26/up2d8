
import React from 'react';

interface LandingPageProps {
  onLaunch: () => void;
}

const FeatureIcon1 = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 12h6M7 8h6" />
  </svg>
);

const FeatureIcon2 = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
  </svg>
);

const FeatureIcon3 = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
  </svg>
);

export const LandingPage: React.FC<LandingPageProps> = ({ onLaunch }) => {
  return (
    <div className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white min-h-screen flex flex-col font-sans transition-colors duration-300">
      <main className="flex-grow flex flex-col items-center justify-center text-center p-4">
        
        {/* Hero Section */}
        <section className="w-full max-w-4xl">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-gray-800 to-gray-500 dark:from-gray-100 dark:to-gray-400">
            Your Daily News, Intelligently Distilled.
          </h1>
          <p className="mt-6 max-w-2xl mx-auto text-lg text-gray-600 dark:text-gray-300">
            UP2D8 delivers personalized news digests powered by Gemini. Subscribe to any topic and get smart summaries, then chat with an AI that's always up-to-date.
          </p>
          <button
            onClick={onLaunch}
            className="mt-10 px-8 py-4 bg-blue-600 text-white font-bold text-lg rounded-full hover:bg-blue-700 transition-all duration-300 shadow-lg hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-500 focus:ring-opacity-50 transform hover:-translate-y-1"
          >
            Launch App
          </button>
        </section>

        {/* Features Section */}
        <section className="w-full max-w-5xl mt-24 sm:mt-32">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-12">
            <div className="flex flex-col items-center">
              <div className="bg-blue-100 dark:bg-blue-900/50 p-4 rounded-full">
                <FeatureIcon1 />
              </div>
              <h3 className="mt-4 text-xl font-bold">Personalized Digests</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Subscribe to any industry, company, or niche interest. Your news, your way, delivered daily.
              </p>
            </div>
            <div className="flex flex-col items-center">
              <div className="bg-blue-100 dark:bg-blue-900/50 p-4 rounded-full">
                <FeatureIcon2 />
              </div>
              <h3 className="mt-4 text-xl font-bold">AI-Powered Summaries</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Gemini reads and summarizes the day's top stories, so you get the key insights, fast.
              </p>
            </div>
            <div className="flex flex-col items-center">
              <div className="bg-blue-100 dark:bg-blue-900/50 p-4 rounded-full">
                <FeatureIcon3 />
              </div>
              <h3 className="mt-4 text-xl font-bold">Interactive Chat</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Go beyond the digest. Ask follow-up questions and get real-time, sourced answers from the web.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="py-8 text-center text-gray-500 dark:text-gray-400 text-sm">
        <p>&copy; {new Date().getFullYear()} UP2D8. Powered by Gemini.</p>
      </footer>
    </div>
  );
};
