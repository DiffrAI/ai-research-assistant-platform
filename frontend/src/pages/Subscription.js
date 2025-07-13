import React, { useState, useEffect, useRef } from 'react';
import { Check } from 'lucide-react';
import { paymentAPI } from '../services/api';
import useAuthStore from '../store/authStore';
import toast from 'react-hot-toast';
import { useSearchParams } from 'react-router-dom';

const Subscription = () => {
  const [plans, setPlans] = useState({});
  const [usage, setUsage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const { user } = useAuthStore();
  const [searchParams] = useSearchParams();
  const toastShownRef = useRef(false);

  useEffect(() => {
    fetchData();
    
    // Handle URL parameters for success/cancel scenarios
    const success = searchParams.get('success');
    const canceled = searchParams.get('canceled');
    const plan = searchParams.get('plan');
    const price = searchParams.get('price');
    const searches = searchParams.get('searches');
    
    if (!toastShownRef.current && (success === 'true' || canceled === 'true')) {
      toastShownRef.current = true;
      
      if (success === 'true') {
        if (plan && price && searches) {
          const priceDisplay = price === '0' ? 'Free' : `$${price}`;
          const searchesDisplay = searches === 'unlimited' ? 'Unlimited' : searches;
          toast.success(`Successfully upgraded to ${plan} plan! Price: ${priceDisplay}, Searches: ${searchesDisplay}`);
        } else {
          toast.success('Payment successful! Your subscription has been updated.');
        }
      } else if (canceled === 'true') {
        toast.error('Payment was canceled.');
      }
    }
  }, [searchParams]);

  const fetchData = async () => {
    try {
      const [plansResponse, usageResponse] = await Promise.all([
        paymentAPI.getPlans(),
        paymentAPI.getUsage(),
      ]);

      setPlans(plansResponse.data.data.plans);
      setUsage(usageResponse.data.data);
    } catch (error) {
      toast.error('Failed to load subscription data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpgrade = async (planName) => {
    try {
      const response = await paymentAPI.createCheckoutSession(
        planName,
        `${window.location.origin}/subscription?success=true`,
        `${window.location.origin}/subscription?canceled=true`
      );

      // Redirect to Stripe checkout
      window.location.href = response.data.data.checkout_url;
    } catch (error) {
      toast.error('Failed to create checkout session');
    }
  };

  const handleManageBilling = async () => {
    try {
      const response = await paymentAPI.createPortalSession(
        `${window.location.origin}/subscription`
      );
      window.location.href = response.data.data.portal_url;
    } catch (error) {
      toast.error('Failed to open billing portal');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const currentPlan = user?.subscription_plan || 'free';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Subscription Management</h1>
        <p className="text-gray-600">Manage your subscription and usage</p>
      </div>

      {/* Current Plan & Usage */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Plan</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Plan:</span>
              <span className="font-medium capitalize">{currentPlan}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Status:</span>
              <span className="text-green-600 font-medium">Active</span>
            </div>
            {user?.subscription_expires_at && (
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Expires:</span>
                <span className="text-gray-900">
                  {new Date(user.subscription_expires_at).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage This Month</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Searches Used:</span>
              <span className="font-medium">{usage?.searches_used || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Limit:</span>
              <span className="font-medium">{usage?.searches_limit || 10}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Remaining:</span>
              <span className="font-medium text-green-600">
                {Math.max(0, (usage?.searches_limit || 10) - (usage?.searches_used || 0))}
              </span>
            </div>
            {/* Progress bar */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{
                  width: `${Math.min(
                    100,
                    ((usage?.searches_used || 0) / (usage?.searches_limit || 10)) * 100
                  )}%`,
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Available Plans */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Available Plans</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Object.entries(plans).map(([planName, plan]) => (
            <div
              key={planName}
              className={`relative border rounded-lg p-6 ${
                currentPlan === planName
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 bg-white'
              }`}
            >
              {currentPlan === planName && (
                <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                  <span className="bg-primary-600 text-white px-3 py-1 rounded-full text-xs font-medium">
                    Current Plan
                  </span>
                </div>
              )}

              <div className="text-center">
                <h4 className="text-lg font-semibold text-gray-900 capitalize mb-2">
                  {planName}
                </h4>
                <div className="text-3xl font-bold text-gray-900 mb-4">
                  ${plan.price}
                  <span className="text-sm font-normal text-gray-500">/month</span>
                </div>

                <div className="space-y-3 mb-6">
                  <div className="flex items-center text-sm text-gray-600">
                    <Check className="h-4 w-4 text-green-500 mr-2" />
                    {plan.searches_limit === -1 ? 'Unlimited' : `${plan.searches_limit}`} searches/month
                  </div>
                  {plan.features.map((feature, index) => (
                    <div key={index} className="flex items-center text-sm text-gray-600">
                      <Check className="h-4 w-4 text-green-500 mr-2" />
                      {feature}
                    </div>
                  ))}
                </div>

                {currentPlan === planName ? (
                  <button
                    onClick={handleManageBilling}
                    className="w-full btn-secondary"
                  >
                    Manage Billing
                  </button>
                ) : (
                  <button
                    onClick={() => handleUpgrade(planName)}
                    className="w-full btn-primary"
                  >
                    {plan.price === 0 ? 'Get Started' : 'Upgrade'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Plan Comparison */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Plan Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-900">Feature</th>
                <th className="text-center py-3 px-4 font-medium text-gray-900">Free</th>
                <th className="text-center py-3 px-4 font-medium text-gray-900">Pro</th>
                <th className="text-center py-3 px-4 font-medium text-gray-900">Academic</th>
                <th className="text-center py-3 px-4 font-medium text-gray-900">Enterprise</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr>
                <td className="py-3 px-4 text-gray-900">Monthly Searches</td>
                <td className="py-3 px-4 text-center">10</td>
                <td className="py-3 px-4 text-center">100</td>
                <td className="py-3 px-4 text-center">500</td>
                <td className="py-3 px-4 text-center">Unlimited</td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-900">AI Summaries</td>
                <td className="py-3 px-4 text-center">✓</td>
                <td className="py-3 px-4 text-center">✓</td>
                <td className="py-3 px-4 text-center">✓</td>
                <td className="py-3 px-4 text-center">✓</td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-900">Export Options</td>
                <td className="py-3 px-4 text-center">Basic</td>
                <td className="py-3 px-4 text-center">Advanced</td>
                <td className="py-3 px-4 text-center">Advanced</td>
                <td className="py-3 px-4 text-center">All Formats</td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-900">Analytics</td>
                <td className="py-3 px-4 text-center">-</td>
                <td className="py-3 px-4 text-center">✓</td>
                <td className="py-3 px-4 text-center">✓</td>
                <td className="py-3 px-4 text-center">Advanced</td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-900">API Access</td>
                <td className="py-3 px-4 text-center">-</td>
                <td className="py-3 px-4 text-center">-</td>
                <td className="py-3 px-4 text-center">-</td>
                <td className="py-3 px-4 text-center">✓</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Subscription; 