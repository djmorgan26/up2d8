import React from 'react';

export const Logo: React.FC = () => {
  return (
    <div className="flex items-center justify-center w-16 h-16 rounded-full">
      <img src="/logo.png" alt="UP2D8 Digest Logo" className="w-full h-full object-contain" />
    </div>
  );
};
