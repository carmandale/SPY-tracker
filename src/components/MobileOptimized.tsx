import React, { ReactNode } from 'react';

interface MobileOptimizedProps {
  children: ReactNode;
  className?: string;
}

/**
 * Mobile-optimized container with proper viewport constraints
 * and safe area handling for iOS devices
 */
export const MobileOptimized: React.FC<MobileOptimizedProps> = ({ 
  children, 
  className = '' 
}) => {
  return (
    <div className={`
      min-h-screen 
      w-full 
      bg-[#0B0D12]
      pb-safe
      ${className}
    `}>
      <div className="
        max-w-7xl 
        mx-auto 
        px-safe
        sm:px-4
        md:px-6
        lg:px-8
      ">
        {children}
      </div>
    </div>
  );
};

/**
 * Mobile-responsive card component with touch-friendly spacing
 */
export const MobileCard: React.FC<{
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}> = ({ children, className = '', onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`
        bg-[#12161D] 
        rounded-xl 
        p-3 sm:p-4 
        border border-white/8
        ${onClick ? 'cursor-pointer active:scale-[0.98] transition-transform' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
};

/**
 * Touch-friendly button with proper hit targets (min 44x44px)
 */
export const MobileButton: React.FC<{
  children: ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  disabled?: boolean;
}> = ({ 
  children, 
  onClick, 
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false
}) => {
  const variants = {
    primary: 'bg-[#006072] text-white hover:bg-[#006072]/80',
    secondary: 'bg-white/10 text-white hover:bg-white/20',
    ghost: 'text-[#A7B3C5] hover:bg-white/5'
  };

  const sizes = {
    sm: 'min-h-[44px] px-3 py-2 text-sm',
    md: 'min-h-[48px] px-4 py-2.5 text-base',
    lg: 'min-h-[52px] px-6 py-3 text-lg'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${variants[variant]}
        ${sizes[size]}
        rounded-lg
        font-medium
        transition-all
        active:scale-95
        disabled:opacity-50
        disabled:cursor-not-allowed
        touch-manipulation
        ${className}
      `}
    >
      {children}
    </button>
  );
};

/**
 * Responsive grid that adapts to screen size
 */
export const ResponsiveGrid: React.FC<{
  children: ReactNode;
  cols?: {
    default?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: number;
  className?: string;
}> = ({ 
  children, 
  cols = { default: 1, sm: 1, md: 2, lg: 3, xl: 4 },
  gap = 4,
  className = ''
}) => {
  const gridCols = [
    cols.default && `grid-cols-${cols.default}`,
    cols.sm && `sm:grid-cols-${cols.sm}`,
    cols.md && `md:grid-cols-${cols.md}`,
    cols.lg && `lg:grid-cols-${cols.lg}`,
    cols.xl && `xl:grid-cols-${cols.xl}`
  ].filter(Boolean).join(' ');

  return (
    <div className={`grid ${gridCols} gap-${gap} ${className}`}>
      {children}
    </div>
  );
};

/**
 * Swipeable container for mobile gestures
 */
export const SwipeableContainer: React.FC<{
  children: ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  className?: string;
}> = ({ children, onSwipeLeft, onSwipeRight, className = '' }) => {
  const [touchStart, setTouchStart] = React.useState<number | null>(null);
  const [touchEnd, setTouchEnd] = React.useState<number | null>(null);

  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;
    
    if (isLeftSwipe && onSwipeLeft) {
      onSwipeLeft();
    }
    if (isRightSwipe && onSwipeRight) {
      onSwipeRight();
    }
  };

  return (
    <div
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
      className={className}
    >
      {children}
    </div>
  );
};