import React from 'react';

interface ContextPromptProps {
  title?: string;
  message: string;
}

const ContextPrompt: React.FC<ContextPromptProps> = ({ title, message }) => {
  return (
    <div className="p-4 bg-surface rounded-lg shadow-md mb-4" style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}>
      {title && <h3 className="font-bold text-lg mb-2">{title}</h3>}
      <p className="text-sm">{message}</p>
    </div>
  );
};

export default ContextPrompt;
