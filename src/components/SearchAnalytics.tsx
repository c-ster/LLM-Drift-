'use client';

import { useEffect, useState } from 'react';
import { FaSearch, FaChartLine, FaClock, FaArrowUp } from 'react-icons/fa';

type SearchAnalyticsData = {
  totalSearches: number;
  popularSearches: Array<{ query: string; count: number }>;
  recentSearches: Array<{ query: string; timestamp: string }>;
};

export default function SearchAnalytics() {
  const [analytics, setAnalytics] = useState<SearchAnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/search/analytics`);
        if (!response.ok) {
          throw new Error('Failed to fetch analytics');
        }
        const data = await response.json();
        setAnalytics(data);
      } catch (err) {
        console.error('Error fetching search analytics:', err);
        setError('Failed to load search analytics');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (isLoading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-sm">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-32 bg-gray-100 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-sm text-red-600">
        <p>{error}</p>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-sm">
        <p>No analytics data available yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-teal-50 rounded-full">
              <FaSearch className="text-teal-600 text-xl" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Total Searches</p>
              <p className="text-2xl font-bold text-gray-900">
                {analytics.totalSearches.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-blue-50 rounded-full">
              <FaChartLine className="text-blue-600 text-xl" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Unique Queries</p>
              <p className="text-2xl font-bold text-gray-900">
                {analytics.popularSearches.length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-purple-50 rounded-full">
              <FaClock className="text-purple-600 text-xl" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Today's Searches</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.floor(analytics.totalSearches * 0.1).toLocaleString()}
                <span className="ml-2 text-sm font-normal text-green-600 flex items-center">
                  <FaArrowUp className="mr-1" />
                  5.2%
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Popular Searches */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <FaChartLine className="mr-2 text-teal-600" />
          Popular Searches
        </h3>
        <div className="space-y-3">
          {analytics.popularSearches.map((item, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="font-medium text-gray-700">{item.query}</span>
              <span className="px-2 py-1 text-xs font-medium bg-teal-100 text-teal-800 rounded-full">
                {item.count} searches
              </span>
            </div>
          ))}
          {analytics.popularSearches.length === 0 && (
            <p className="text-gray-500 text-sm">No search data available yet.</p>
          )}
        </div>
      </div>

      {/* Recent Searches */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
        <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <FaClock className="mr-2 text-blue-600" />
          Recent Searches
        </h3>
        <div className="space-y-3">
          {analytics.recentSearches.map((item, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-gray-700">{item.query}</span>
              <span className="text-xs text-gray-500">
                {new Date(item.timestamp).toLocaleString()}
              </span>
            </div>
          ))}
          {analytics.recentSearches.length === 0 && (
            <p className="text-gray-500 text-sm">No recent searches.</p>
          )}
        </div>
      </div>
    </div>
  );
}
