import { useEffect } from 'react';

type SearchEvent = {
  query: string;
  filters?: Record<string, unknown>;
  resultCount: number;
};

export const trackSearch = async (event: SearchEvent) => {
  try {
    await fetch('/api/search/analytics', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...event,
        userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : '',
      }),
    });
  } catch (error) {
    console.error('Error tracking search:', error);
  }
};

export const useTrackSearch = (query: string, resultCount: number, filters = {}) => {
  useEffect(() => {
    if (query && resultCount >= 0) {
      trackSearch({
        query,
        filters,
        resultCount,
      });
    }
  }, [query, resultCount, filters]);
};
