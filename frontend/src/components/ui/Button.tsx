import React from 'react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const variantStyles = {
      primary: 'bg-primary text-white hover:bg-primary-dark shadow-md hover:shadow-lg active:scale-[0.98]',
      outline: 'border-2 border-primary text-primary hover:bg-primary-pale active:scale-[0.98]',
      ghost: 'text-primary hover:bg-primary-pale active:scale-[0.98]',
      danger: 'bg-error text-white hover:bg-red-600 shadow-md hover:shadow-lg active:scale-[0.98]',
    };

    const sizeStyles = {
      sm: 'px-3 py-1.5 text-sm rounded-md',
      md: 'px-5 py-2.5 text-base rounded-lg',
      lg: 'px-6 py-3 text-lg rounded-lg',
    };

    return (
      <button
        ref={ref}
        className={cn(
          'font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
