
import React from 'react';
import { TopicCard } from '../components/TopicCard';
import { BrowseCategory } from '../types';

const mockCategories: BrowseCategory[] = [
  {
    title: 'Trending in Tech',
    topics: [
      { name: 'Generative AI', imageUrl: 'https://images.unsplash.com/photo-1677756119517-756a188d2d94?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
      { name: 'Quantum Computing', imageUrl: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
      { name: 'Cybersecurity', imageUrl: 'https://images.unsplash.com/photo-1544890225-2f3faec4cd60?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
      { name: 'Cloud Native', imageUrl: 'https://images.unsplash.com/photo-1534972195531-d756b9bfa9f2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
      { name: 'Web3 & Blockchain', imageUrl: 'https://images.unsplash.com/photo-1642104704074-907126278d15?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
    ]
  },
  {
    title: 'Business & Finance',
    topics: [
      { name: 'Market Analysis', imageUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
      { name: 'Venture Capital', imageUrl: 'https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
      { name: 'Fintech', imageUrl: 'https://images.unsplash.com/photo-1620714223084-8fcacc6dfd8d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
      { name: 'Global Economics', imageUrl: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
      { name: 'Corporate Strategy', imageUrl: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
    ]
  },
  {
    title: 'Science & Health',
    topics: [
        { name: 'Bioengineering', imageUrl: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
        { name: 'Space Exploration', imageUrl: 'https://images.unsplash.com/photo-1454789548928-9efd52dc4031?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
        { name: 'Neuroscience', imageUrl: 'https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
        { name: 'Climate Science', imageUrl: 'https://images.unsplash.com/photo-1504221507732-5246c0db2387?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
        { name: 'Personalized Medicine', imageUrl: 'https://images.unsplash.com/photo-1530497610242-d4a3c15c8263?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=400' },
    ]
  }
];

const BrowsePage: React.FC = () => {
  return (
    <div className="p-4 md:p-6 space-y-8 h-full">
      <header>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Discover Topics</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Browse popular categories to add to your digest.</p>
      </header>
      <div className="space-y-8">
        {mockCategories.map(category => (
          <section key={category.title}>
            <h3 className="text-lg font-semibold mb-3 text-gray-700 dark:text-gray-200">{category.title}</h3>
            <div className="flex gap-4 overflow-x-auto pb-4 -mb-4 snap-x snap-mandatory">
              {category.topics.map(topic => (
                <div key={topic.name} className="snap-start">
                  <TopicCard topic={topic} />
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
};

export default BrowsePage;
