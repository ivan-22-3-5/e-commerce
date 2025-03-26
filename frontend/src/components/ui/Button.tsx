"use client";

import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outlined';
  className?: string;
}

const baseStyles = 'rounded-sm px-2 py-0.5 transition-all duration-200';

const variantStyles = {
  primary: 'bg-primary-light dark:bg-primary-dark hover:bg-primary-dark dark:hover:bg-primary-light',
  outlined: `
  border border-primary-light dark:border-primary-dark 
  text-primary-light dark:text-primary-dark hover:text-white 
  bg-transparent hover:bg-primary-light dark:hover:bg-primary-dark
  `,
};

const Button: React.FC<ButtonProps> = ({
                                         children,
                                         variant = 'primary',
                                         className = '',
                                         ...props
                                       }) => {

  const combinedStyles = [
    baseStyles,
    variantStyles[variant],
    className,
  ].filter(Boolean).join(' ');

  return (
    <button className={combinedStyles} {...props}>
      {children}
    </button>
  );
};

export default Button;