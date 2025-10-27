import React from 'react';

export const Logo: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`font-bold text-2xl text-primary ${className}`}>
      UP2D8
    </div>
  );
};
