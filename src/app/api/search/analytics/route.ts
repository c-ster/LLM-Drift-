import { NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs/promises';
import { v4 as uuidv4 } from 'uuid';

const ANALYTICS_FILE = path.join(process.cwd(), 'data/search-analytics.json');

type SearchEvent = {
  id: string;
  query: string;
  timestamp: string;
  filters?: Record<string, unknown>;
  resultCount: number;
  sessionId?: string;
  userAgent?: string;
};

export async function POST(request: Request) {
  try {
    const event: Omit<SearchEvent, 'id' | 'timestamp'> = await request.json();
    
    // Read existing analytics
    let analytics: SearchEvent[] = [];
    try {
      const data = await fs.readFile(ANALYTICS_FILE, 'utf-8');
      analytics = JSON.parse(data);
    } catch (error) {
      // File doesn't exist yet, will be created
    }

    // Add new event
    const newEvent: SearchEvent = {
      id: uuidv4(),
      timestamp: new Date().toISOString(),
      ...event,
    };

    analytics.push(newEvent);
    
    // Keep only the last 1000 events to prevent file from growing too large
    const recentAnalytics = analytics.slice(-1000);
    
    // Save back to file
    await fs.writeFile(ANALYTICS_FILE, JSON.stringify(recentAnalytics, null, 2));
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error saving search analytics:', error);
    return NextResponse.json(
      { error: 'Failed to save search analytics' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // Read analytics data
    const data = await fs.readFile(ANALYTICS_FILE, 'utf-8');
    const analytics = JSON.parse(data);
    
    // Calculate popular searches
    const searchCounts: Record<string, number> = {};
    analytics.forEach((event: SearchEvent) => {
      if (event.query) {
        searchCounts[event.query] = (searchCounts[event.query] || 0) + 1;
      }
    });
    
    // Get top 10 popular searches
    const popularSearches = Object.entries(searchCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([query, count]) => ({ query, count }));
    
    // Get recent searches (last 10 unique)
    const recentSearches = Array.from(
      new Map(analytics
        .filter(event => event.query)
        .reverse()
        .map(event => [event.query, event]))
      .values()
    ).slice(0, 10);
    
    return NextResponse.json({
      totalSearches: analytics.length,
      popularSearches,
      recentSearches,
    });
  } catch (error) {
    console.error('Error reading search analytics:', error);
    return NextResponse.json(
      { 
        totalSearches: 0,
        popularSearches: [],
        recentSearches: []
      },
      { status: 200 }
    );
  }
}
