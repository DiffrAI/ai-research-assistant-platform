import React, { useState, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Search,
  User,
  CreditCard,
  BarChart3,
  LogOut,
  Menu,
  X,
  BookOpen,
  TrendingUp,
  Settings,
  Bell,
} from 'lucide-react';
import useAuthStore from '../store/authStore';
import { Button } from './ui';
import { NavigationItem } from '../types';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, isAuthenticated, logout } = useAuthStore();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = useCallback(async () => {
    await logout();
    navigate('/login');
  }, [logout, navigate]);

  const closeSidebar = useCallback(() => {
    setSidebarOpen(false);
  }, []);

  const navigation: NavigationItem[] = [
    { name: 'Research', href: '/', icon: Search, description: 'Conduct AI-powered research' },
    { name: 'Saved Research', href: '/saved', icon: BookOpen, description: 'View your saved research' },
    { name: 'Analytics', href: '/analytics', icon: BarChart3, description: 'Research insights and stats' },
    { name: 'Trending', href: '/trending', icon: TrendingUp, description: 'Popular research topics' },
    { name: 'Subscription', href: '/subscription', icon: CreditCard, description: 'Manage your plan' },
    { name: 'Profile', href: '/profile', icon: User, description: 'Account settings' },
  ];

  if (!isAuthenticated) {
    return <div className="min-h-screen bg-gray-50">{children}</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <div
        className={`fixed inset-0 z-50 lg:hidden transition-opacity duration-300 ${
          sidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
      >
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 transition-opacity"
          onClick={closeSidebar}
        />
        <div className={`fixed inset-y-0 left-0 flex w-64 flex-col bg-white shadow-xl transform transition-transform duration-300 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}>
          <div className="flex h-16 items-center justify-between px-4 border-b border-gray-200">
            <h1 className="text-xl font-bold text-gray-900">AI Research</h1>
            <Button
              onClick={closeSidebar}
              variant="ghost"
              size="sm"
              icon={X}
              className="text-gray-400 hover:text-gray-600"
              aria-label="Close sidebar"
            />
          </div>
          <nav
            aria-label="Mobile navigation"
            className="flex-1 space-y-1 px-2 py-4 overflow-y-auto"
          >
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-100 text-primary-900 border-r-2 border-primary-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                  onClick={closeSidebar}
                >
                  <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                  <div className="flex-1">
                    <div>{item.name}</div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {item.description}
                    </div>
                  </div>
                </Link>
              );
            })}
          </nav>
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center px-3 py-2 text-sm text-gray-600 mb-2">
              <User className="mr-3 h-5 w-5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{user?.full_name}</p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>
            <Button
              onClick={handleLogout}
              variant="ghost"
              icon={LogOut}
              className="w-full justify-start text-gray-600 hover:text-gray-900"
            >
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200 shadow-sm">
          <div className="flex h-16 items-center px-4 border-b border-gray-200">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center mr-3">
                <Search className="h-5 w-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">AI Research</h1>
            </div>
          </div>
          <nav
            aria-label="Desktop navigation"
            className="flex-1 space-y-1 px-3 py-4 overflow-y-auto"
          >
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-100 text-primary-900 border-r-2 border-primary-600 shadow-sm'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 hover:shadow-sm'
                  }`}
                >
                  <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                  <div className="flex-1">
                    <div>{item.name}</div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {item.description}
                    </div>
                  </div>
                </Link>
              );
            })}
          </nav>
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center px-3 py-2 text-sm text-gray-600 mb-3">
              <div className="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center mr-3">
                <User className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{user?.full_name}</p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>
            <div className="space-y-1">
              <Button
                variant="ghost"
                size="sm"
                icon={Settings}
                className="w-full justify-start text-gray-600 hover:text-gray-900"
              >
                Settings
              </Button>
              <Button
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                icon={LogOut}
                className="w-full justify-start text-gray-600 hover:text-gray-900"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Mobile header */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm lg:hidden">
          <Button
            onClick={() => setSidebarOpen(true)}
            variant="ghost"
            size="sm"
            icon={Menu}
            className="text-gray-700 hover:text-gray-900"
            aria-label="Open sidebar"
          />
          <div className="flex flex-1 items-center justify-between">
            <div className="flex items-center">
              <div className="h-6 w-6 bg-primary-600 rounded flex items-center justify-center mr-2">
                <Search className="h-4 w-4 text-white" />
              </div>
              <h1 className="text-lg font-semibold text-gray-900">AI Research</h1>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                icon={Bell}
                className="text-gray-500 hover:text-gray-700"
              />
              <div className="h-6 w-6 bg-gray-200 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-gray-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
