import React, { useState, useEffect } from 'react';
import { 
  Search, 
  BookOpen, 
  TrendingUp, 
  Clock, 
  BarChart3,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { Card, Button } from './ui';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { formatRelativeTime } from '../utils/helpers';
import useAuthStore from '../store/authStore';

interface DashboardProps {
  onStartResearch: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onStartResearch }) => {
  const { user } = useAuthStore();
  const [recentSearches] = useLocalStorage('searchHistory', []);
  const [stats, setStats] = useState({
    totalSearches: 0,
    savedResearch: 0,
    avgResultsPerSearch: 0,
  });

  useEffect(() => {
    // Calculate stats from search history
    if (recentSearches.length > 0) {
      const totalResults = recentSearches.reduce((sum: number, search: any) => 
        sum + (search.resultsCount || 0), 0
      );
      
      setStats({
        totalSearches: recentSearches.length,
        savedResearch: recentSearches.filter((search: any) => search.starred).length,
        avgResultsPerSearch: Math.round(totalResults / recentSearches.length) || 0,
      });
    }
  }, [recentSearches]);

  const quickActions = [
    {
      title: 'Start Research',
      description: 'Begin a new AI-powered research session',
      icon: Search,
      color: 'bg-primary-500',
      action: onStartResearch,
    },
    {
      title: 'View History',
      description: 'Browse your previous research queries',
      icon: Clock,
      color: 'bg-blue-500',
      action: () => console.log('View history'),
    },
    {
      title: 'Saved Research',
      description: 'Access your bookmarked research',
      icon: BookOpen,
      color: 'bg-green-500',
      action: () => console.log('Saved research'),
    },
    {
      title: 'Analytics',
      description: 'View your research insights',
      icon: BarChart3,
      color: 'bg-purple-500',
      action: () => console.log('Analytics'),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="text-center py-8">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Sparkles className="h-8 w-8 text-primary-600" />
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''}!
          </h1>
        </div>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Ready to dive into intelligent research? Let's discover insights together with AI-powered search.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="text-center p-6">
          <div className="flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg mx-auto mb-4">
            <Search className="h-6 w-6 text-primary-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{stats.totalSearches}</div>
          <div className="text-sm text-gray-600">Total Searches</div>
        </Card>

        <Card className="text-center p-6">
          <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mx-auto mb-4">
            <BookOpen className="h-6 w-6 text-green-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{stats.savedResearch}</div>
          <div className="text-sm text-gray-600">Saved Research</div>
        </Card>

        <Card className="text-center p-6">
          <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-4">
            <TrendingUp className="h-6 w-6 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{stats.avgResultsPerSearch}</div>
          <div className="text-sm text-gray-600">Avg Results/Search</div>
        </Card>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickActions.map((action, index) => (
            <Card
              key={index}
              className="p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={action.action}
            >
              <div className="flex items-center space-x-4">
                <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center`}>
                  <action.icon className="h-6 w-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{action.title}</h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400" />
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      {recentSearches.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <Card>
            <div className="divide-y divide-gray-200">
              {recentSearches.slice(0, 5).map((search: any, index: number) => (
                <div key={index} className="p-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Search className="h-4 w-4 text-gray-400" />
                    <div>
                      <div className="font-medium text-gray-900">{search.query}</div>
                      <div className="text-sm text-gray-500">
                        {search.resultsCount} results • {formatRelativeTime(search.timestamp)}
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onStartResearch()}
                  >
                    Search Again
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Usage Stats */}
      {user && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage This Month</h3>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {user.searches_used_this_month}
              </div>
              <div className="text-sm text-gray-600">
                of {user.searches_limit} searches used
              </div>
            </div>
            <div className="w-32 bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{
                  width: `${Math.min(
                    (user.searches_used_this_month / user.searches_limit) * 100,
                    100
                  )}%`,
                }}
              />
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;