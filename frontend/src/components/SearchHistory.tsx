import React, { useState, useEffect } from 'react';
import { Clock, Search, Trash2, Star } from 'lucide-react';
import { Button, Card } from './ui';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { formatRelativeTime } from '../utils/helpers';

interface SearchHistoryItem {
  id: string;
  query: string;
  timestamp: string;
  resultsCount: number;
  starred: boolean;
}

interface SearchHistoryProps {
  onSelectQuery: (query: string) => void;
  className?: string;
}

interface SearchHistoryRef {
  addToHistory: (query: string, resultsCount?: number) => void;
}

const SearchHistory = React.forwardRef<SearchHistoryRef, SearchHistoryProps>(({ onSelectQuery, className = '' }, ref) => {
  const [searchHistory, setSearchHistory] = useLocalStorage<SearchHistoryItem[]>('searchHistory', []);
  const [filter, setFilter] = useState<'all' | 'starred'>('all');

  const addToHistory = (query: string, resultsCount: number = 0) => {
    const newItem: SearchHistoryItem = {
      id: Date.now().toString(),
      query,
      timestamp: new Date().toISOString(),
      resultsCount,
      starred: false,
    };

    setSearchHistory(prev => {
      // Remove duplicate queries
      const filtered = prev.filter(item => item.query !== query);
      // Add new item at the beginning and limit to 50 items
      return [newItem, ...filtered].slice(0, 50);
    });
  };

  const toggleStar = (id: string) => {
    setSearchHistory(prev =>
      prev.map(item =>
        item.id === id ? { ...item, starred: !item.starred } : item
      )
    );
  };

  const removeItem = (id: string) => {
    setSearchHistory(prev => prev.filter(item => item.id !== id));
  };

  const clearHistory = () => {
    setSearchHistory([]);
  };

  const filteredHistory = searchHistory.filter(item =>
    filter === 'all' || (filter === 'starred' && item.starred)
  );

  // Expose addToHistory method to parent components
  React.useImperativeHandle(ref, () => ({
    addToHistory,
  }));

  if (searchHistory.length === 0) {
    return (
      <Card className={`p-4 ${className}`}>
        <div className="text-center text-gray-500">
          <Clock className="h-8 w-8 mx-auto mb-2 text-gray-400" />
          <p className="text-sm">No search history yet</p>
          <p className="text-xs text-gray-400 mt-1">
            Your recent searches will appear here
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Clock className="h-5 w-5 mr-2" />
          Search History
        </h3>
        <div className="flex items-center space-x-2">
          <div className="flex rounded-lg border border-gray-200 p-1">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1 text-sm rounded transition-colors ${filter === 'all'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-600 hover:text-gray-900'
                }`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('starred')}
              className={`px-3 py-1 text-sm rounded transition-colors ${filter === 'starred'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-600 hover:text-gray-900'
                }`}
            >
              Starred
            </button>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={clearHistory}
            className="text-gray-500 hover:text-red-600"
          >
            Clear All
          </Button>
        </div>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredHistory.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
          >
            <div className="flex-1 min-w-0">
              <button
                onClick={() => onSelectQuery(item.query)}
                className="text-left w-full"
              >
                <div className="flex items-center space-x-2">
                  <Search className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {item.query}
                  </p>
                </div>
                <div className="flex items-center space-x-4 mt-1">
                  <span className="text-xs text-gray-500">
                    {formatRelativeTime(item.timestamp)}
                  </span>
                  {item.resultsCount > 0 && (
                    <span className="text-xs text-gray-500">
                      {item.resultsCount} results
                    </span>
                  )}
                </div>
              </button>
            </div>

            <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => toggleStar(item.id)}
                className={`p-1 ${item.starred
                  ? 'text-yellow-500 hover:text-yellow-600'
                  : 'text-gray-400 hover:text-yellow-500'
                  }`}
              >
                <Star className={`h-4 w-4 ${item.starred ? 'fill-current' : ''}`} />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeItem(item.id)}
                className="p-1 text-gray-400 hover:text-red-500"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
});

SearchHistory.displayName = 'SearchHistory';

export default SearchHistory;