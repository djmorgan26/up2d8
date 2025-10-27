import React from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'company' | 'category' | 'new';
}

export const Badge: React.FC<BadgeProps> = ({ className, variant = 'default', children, ...props }) => {
  const variantStyles = {
    default: 'bg-bg-soft text-text-secondary',
    company: 'bg-primary-pale text-primary font-semibold uppercase text-xs tracking-wide',
    category: 'bg-bg-soft text-text-secondary',
    new: 'bg-primary text-white',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-4 py-1.5 rounded-full text-sm font-medium shadow-sm',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
