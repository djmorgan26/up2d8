
import React from 'react';
import { BrowseCategoryTopic } from '../types';

interface TopicCardProps {
  topic: BrowseCategoryTopic;
}

export const TopicCard: React.FC<TopicCardProps> = ({ topic }) => {
  return (
    <div className="flex-shrink-0 w-48 h-32 rounded-lg overflow-hidden relative group cursor-pointer shadow-md hover:shadow-xl transition-shadow duration-300">
      <img src={topic.imageUrl} alt={topic.name} className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110" />
      <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" />
      <h4 className="absolute bottom-0 left-0 p-3 text-white font-bold text-base">{topic.name}</h4>
    </div>
  );
};
