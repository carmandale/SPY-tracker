import React from 'react';
import { motion } from 'framer-motion';

const shimmer = {
  initial: { backgroundPosition: '-200% 0' },
  animate: { 
    backgroundPosition: '200% 0',
    transition: {
      repeat: Infinity,
      duration: 1.5,
      ease: 'linear'
    }
  }
};

const SkeletonBase: React.FC<{ className?: string }> = ({ className = '' }) => (
  <motion.div
    className={`bg-gradient-to-r from-[#12161D] via-[#1a1f29] to-[#12161D] bg-[length:200%_100%] ${className}`}
    variants={shimmer}
    initial="initial"
    animate="animate"
  />
);

export const PredictionCardSkeleton: React.FC = () => (
  <div className="bg-[#12161D] rounded-xl p-4 border border-white/8">
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center gap-3">
        <SkeletonBase className="h-6 w-32 rounded" />
        <SkeletonBase className="h-5 w-16 rounded-full" />
      </div>
      <SkeletonBase className="h-5 w-5 rounded" />
    </div>
    
    <div className="flex items-center gap-4 mb-3">
      <div className="text-center">
        <SkeletonBase className="h-3 w-8 rounded mb-1" />
        <SkeletonBase className="h-7 w-20 rounded" />
      </div>
      <SkeletonBase className="flex-1 h-px" />
      <div className="text-center">
        <SkeletonBase className="h-3 w-8 rounded mb-1" />
        <SkeletonBase className="h-7 w-20 rounded" />
      </div>
    </div>
    
    <SkeletonBase className="h-16 w-full rounded-lg" />
  </div>
);

export const KeyTimesSkeleton: React.FC = () => (
  <div>
    <SkeletonBase className="h-4 w-24 rounded mb-3" />
    <div className="grid grid-cols-2 gap-3">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
          <div className="flex items-center justify-between mb-2">
            <SkeletonBase className="h-3 w-16 rounded" />
            <SkeletonBase className="h-3 w-12 rounded" />
          </div>
          <SkeletonBase className="h-6 w-20 rounded" />
        </div>
      ))}
    </div>
  </div>
);

export const ChartSkeleton: React.FC = () => (
  <div className="bg-[#12161D] rounded-xl p-4 border border-white/8">
    <div className="flex items-center justify-between mb-4">
      <SkeletonBase className="h-4 w-24 rounded" />
      <SkeletonBase className="h-8 w-8 rounded-lg" />
    </div>
    <SkeletonBase className="h-48 w-full rounded" />
  </div>
);

export const SuggestionCardsSkeleton: React.FC = () => (
  <div>
    <SkeletonBase className="h-4 w-32 rounded mb-3" />
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-[#12161D] rounded-xl p-4 border border-white/8">
          <div className="flex items-center justify-between mb-3">
            <SkeletonBase className="h-5 w-12 rounded-full" />
            <SkeletonBase className="h-5 w-16 rounded-full" />
          </div>
          <div className="space-y-2 mb-3">
            <SkeletonBase className="h-4 w-full rounded" />
            <SkeletonBase className="h-4 w-3/4 rounded" />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <SkeletonBase className="h-12 rounded" />
            <SkeletonBase className="h-12 rounded" />
          </div>
        </div>
      ))}
    </div>
  </div>
);

export const MetricsSkeleton: React.FC = () => (
  <div className="bg-[#12161D] rounded-xl p-4 border border-white/8">
    <div className="flex items-center justify-between mb-3">
      <div className="text-center">
        <SkeletonBase className="h-3 w-20 rounded mb-1 mx-auto" />
        <SkeletonBase className="h-6 w-12 rounded mx-auto" />
      </div>
      <div className="text-center">
        <SkeletonBase className="h-3 w-24 rounded mb-1 mx-auto" />
        <SkeletonBase className="h-6 w-16 rounded mx-auto" />
      </div>
    </div>
    <SkeletonBase className="h-12 w-full rounded-lg" />
  </div>
);

export const HistoryRowSkeleton: React.FC = () => (
  <div className="flex items-center gap-4 p-3 bg-[#12161D] rounded-lg border border-white/8">
    <SkeletonBase className="h-4 w-20 rounded" />
    <SkeletonBase className="h-4 w-24 rounded" />
    <SkeletonBase className="h-4 w-16 rounded" />
    <SkeletonBase className="h-4 w-12 rounded" />
    <SkeletonBase className="flex-1 h-4 rounded" />
  </div>
);

export const FullDashboardSkeleton: React.FC = () => (
  <div className="p-4 space-y-6">
    <PredictionCardSkeleton />
    <KeyTimesSkeleton />
    <ChartSkeleton />
    <SuggestionCardsSkeleton />
    <MetricsSkeleton />
  </div>
);