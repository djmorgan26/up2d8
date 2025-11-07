
import React from 'react';
import { BrowseCategoryTopic } from '../types';

interface TopicActionModalProps {
  topic: BrowseCategoryTopic | null;
  onClose: () => void;
  onChat: (topicName: string) => void;
  onSubscribe: (topicName: string) => void;
}

const TopicActionModal: React.FC<TopicActionModalProps> = ({ topic, onClose, onChat, onSubscribe }) => {
  if (!topic) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-sm w-full mx-4">
        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          {topic.name}
        </h3>
        <p className="text-gray-700 dark:text-gray-300 mb-6">
          What would you like to do with this topic?
        </p>
        <div className="flex flex-col space-y-4">
          <button
            onClick={() => onChat(topic.name)}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md transition duration-300"
          >
            Chat
          </button>
          <button
            onClick={() => onSubscribe(topic.name)}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-md transition duration-300"
          >
            Subscribe
          </button>
          <button
            onClick={onClose}
            className="w-full bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-md transition duration-300 dark:bg-gray-600 dark:hover:bg-gray-700 dark:text-gray-100"
          >
            Back
          </button>
        </div>
      </div>
    </div>
  );
};

export default TopicActionModal;
