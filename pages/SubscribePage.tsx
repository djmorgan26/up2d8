
import React, { useState, FormEvent, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { subscribeUser } from '../services/userService';

const popularTopics = ['Artificial Intelligence', 'Cybersecurity', 'Health Science', 'Fintech', 'Renewable Energy', 'Business'];

const SubscribePage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [selectedTopics, setSelectedTopics] = useState<Set<string>>(new Set());
  const [customTopic, setCustomTopic] = useState('');
  const [status, setStatus] = useState<{ type: 'idle' | 'loading' | 'success' | 'error', message: string }>({ type: 'idle', message: '' });

  const [searchParams] = useSearchParams();

  useEffect(() => {
    const topicFromUrl = searchParams.get('topic');
    if (topicFromUrl) {
      setSelectedTopics(prev => new Set(prev).add(topicFromUrl));
    }
  }, [searchParams]);

  const toggleTopic = (topic: string) => {
    setSelectedTopics(prev => {
      const newSet = new Set(prev);
      if (newSet.has(topic)) {
        newSet.delete(topic);
      } else {
        newSet.add(topic);
      }
      return newSet;
    });
  };

  const handleAddCustomTopic = () => {
    const trimmedTopic = customTopic.trim();
    if (trimmedTopic && !selectedTopics.has(trimmedTopic)) {
      setSelectedTopics(prev => new Set(prev).add(trimmedTopic));
      setCustomTopic('');
    }
  };

const handleCustomTopicKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddCustomTopic();
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!email || selectedTopics.size === 0) {
        setStatus({ type: 'error', message: 'Please provide an email and select at least one topic.'});
        return;
    }
    setStatus({ type: 'loading', message: 'Subscribing...' });
    try {
        const response = await subscribeUser(email, Array.from(selectedTopics));
        setStatus({ type: 'success', message: response.message || 'Successfully subscribed! Check your inbox for your first digest.' });
        setEmail('');
        setSelectedTopics(new Set());
    } catch (error) {
        const message = error instanceof Error ? error.message : "An unexpected error occurred.";
        setStatus({ type: 'error', message });
    }
  };

  return (
    <div className="p-4 md:p-6 h-full">
      <header className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Subscribe to Your Digest</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Get the latest news on topics you care about, delivered daily.</p>
      </header>
      
      <form onSubmit={handleSubmit} className="space-y-6 max-w-lg mx-auto">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email Address</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg py-2 px-4 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="you@example.com"
          />
        </div>

        <div>
            <h3 className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Select Topics</h3>
            <div className="flex flex-wrap gap-2">
                {popularTopics.map(topic => (
                    <button type="button" key={topic} onClick={() => toggleTopic(topic)} className={`px-3 py-1 text-sm rounded-full border transition-colors duration-200 ${selectedTopics.has(topic) ? 'bg-blue-500 text-white border-blue-500' : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'}`}>
                        {topic}
                    </button>
                ))}
            </div>
        </div>
         <div>
          <label htmlFor="customTopic" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Add a custom topic</label>
            <div className="flex gap-2">
                <input
                    type="text"
                    id="customTopic"
                    value={customTopic}
                    onChange={(e) => setCustomTopic(e.target.value)}
                    onKeyDown={handleCustomTopicKeyDown}
                    className="flex-grow bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg py-2 px-4 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 'SpaceX'"
                />
                <button type="button" onClick={handleAddCustomTopic} className="px-4 py-2 text-sm font-semibold bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-100 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors duration-200">Add</button>
            </div>
        </div>

        {selectedTopics.size > 0 && (
            <div>
                 <h4 className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Your topics:</h4>
                 <div className="flex flex-wrap gap-2">
                    {Array.from(selectedTopics).map(topic => (
                         <span key={topic} className="px-3 py-1 text-sm rounded-full border bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 border-blue-200 dark:border-blue-700 flex items-center gap-2">
                            {topic}
                            <button type="button" onClick={() => toggleTopic(topic)} className="text-blue-500 hover:text-blue-700 dark:text-blue-300 dark:hover:text-blue-100">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" /></svg>
                            </button>
                         </span>
                    ))}
                 </div>
            </div>
        )}

        <div>
            <button type="submit" disabled={status.type === 'loading'} className="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800">
                {status.type === 'loading' ? 'Subscribing...' : 'Subscribe'}
            </button>
        </div>

        {status.type !== 'idle' && (
            <div className={`p-3 rounded-lg text-sm text-center ${status.type === 'success' ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200' : status.type === 'error' ? 'bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-200' : ''}`}>
                {status.message}
            </div>
        )}
      </form>
    </div>
  );
};

export default SubscribePage;
