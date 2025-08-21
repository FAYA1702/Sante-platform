import React from 'react';

// Simple, dependency-free SVG icons (outline style) inspired by Heroicons
// Usage: <UserGroupIcon className="h-5 w-5" />

type IconProps = React.SVGProps<SVGSVGElement> & { className?: string };

export const UserGroupIcon: React.FC<IconProps> = ({ className = 'h-5 w-5', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M18 20a4 4 0 00-4-4H6a4 4 0 00-4 4" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M14 7a4 4 0 11-8 0 4 4 0 018 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M22 20a4 4 0 00-3-3.87M16.24 3.53A4 4 0 0120 7a4 4 0 01-.53 2" />
  </svg>
);

export const WrenchScrewdriverIcon: React.FC<IconProps> = ({ className = 'h-5 w-5', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 21l6-6M3 15l6 6" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l8-4-4 8-8 4 4-8z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M14 6l4 4" />
  </svg>
);

export const StethoscopeIcon: React.FC<IconProps> = ({ className = 'h-5 w-5', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 4v4a4 4 0 108 0V4" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 8a6 6 0 006 6 6 6 0 006-6" />
    <circle cx="20" cy="16" r="2" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M20 18v2a4 4 0 01-4 4h-2" />
  </svg>
);

export const CheckIcon: React.FC<IconProps> = ({ className = 'h-5 w-5', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
  </svg>
);

export const XMarkIcon: React.FC<IconProps> = ({ className = 'h-5 w-5', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
  </svg>
);

export const HeartIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 10-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 000-7.78z" />
  </svg>
);

export const LungsIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v7M12 10c-2 0-4-2-4-4v14M12 10c2 0 4-2 4-4v14" />
  </svg>
);

export const ClipboardMedicalIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <rect x="7" y="3" width="10" height="4" rx="2" />
    <rect x="5" y="7" width="14" height="14" rx="2" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 11v6M9 14h6" />
  </svg>
);

export const BadgeCheckIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 22a10 10 0 100-20 10 10 0 000 20z" />
  </svg>
);

export const PencilSquareIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M16 3l5 5M4 20l6-2 10-10-4-4L6 14l-2 6z" />
  </svg>
);

export const TrashIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M6 6l1 14a2 2 0 002 2h6a2 2 0 002-2l1-14" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M10 11v6M14 11v6" />
  </svg>
);

export const BellIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
  </svg>
);

export const ExclamationTriangleIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v4m0 4h.01" />
  </svg>
);

export const CalendarIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <rect x="3" y="4" width="18" height="18" rx="2" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M16 2v4M8 2v4M3 10h18" />
  </svg>
);

export const RefreshIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v6h6M20 20v-6h-6" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M20 8a8 8 0 10-3.3 6.5" />
  </svg>
);

export const ChartLineIcon: React.FC<IconProps> = ({ className = 'h-4 w-4', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 3v18h18" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M7 15l4-4 3 3 5-6" />
  </svg>
);

export const ArrowLeftIcon: React.FC<IconProps> = ({ className = 'h-5 w-5', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7 7-7" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 12h18" />
  </svg>
);

export const SparklesIcon: React.FC<IconProps> = ({ className = 'h-5 w-5', ...props }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423L16.5 15.75l.394 1.183a2.25 2.25 0 001.423 1.423L19.5 18.75l-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
  </svg>
);

export default {};
