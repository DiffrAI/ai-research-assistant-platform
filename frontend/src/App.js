import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Login from './pages/Login';
import Research from './pages/Research';
import Subscription from './pages/Subscription';
import useAuthStore from './store/authStore';

// Placeholder components for other pages
const SavedResearch = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-gray-900">Saved Research</h1>
    <p className="text-gray-600">Your saved research will appear here.</p>
  </div>
);

const Analytics = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
    <p className="text-gray-600">Your research analytics will appear here.</p>
  </div>
);

const Trending = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-gray-900">Trending Topics</h1>
    <p className="text-gray-600">Trending research topics will appear here.</p>
  </div>
);

const Profile = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
    <p className="text-gray-600">Your profile settings will appear here.</p>
  </div>
);

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="App">
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
        
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout>
                  <Research />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/saved"
            element={
              <ProtectedRoute>
                <Layout>
                  <SavedResearch />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <Layout>
                  <Analytics />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/trending"
            element={
              <ProtectedRoute>
                <Layout>
                  <Trending />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/subscription"
            element={
              <ProtectedRoute>
                <Layout>
                  <Subscription />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Layout>
                  <Profile />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          {/* Redirect to home for unknown routes */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 