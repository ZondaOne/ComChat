import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  ChatBubbleLeftIcon, 
  UserGroupIcon, 
  CurrencyDollarIcon,
  CogIcon,
  PhoneIcon,
  ComputerDesktopIcon,
  CircleStackIcon
} from '@heroicons/react/24/outline';
import { WorkflowManager } from '../workflows';

interface AnalyticsData {
  conversations: {
    total_conversations: number;
    active_conversations: number;
    conversations_today: number;
    conversations_this_week: number;
    avg_messages_per_conversation: number;
    avg_response_time_ms: number;
  };
  messages: {
    total_messages: number;
    messages_today: number;
    messages_this_week: number;
    messages_by_channel: Record<string, number>;
  };
  usage: {
    current_period_messages: number;
    current_period_ai_requests: number;
    total_cost_cents: number;
    model_usage: Record<string, number>;
  };
}

const AdminDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState('overview');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      // TODO: Replace with actual tenant ID from auth
      const response = await fetch('/api/v1/analytics/overview?tenant_id=demo');
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (cents: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(cents / 100);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="px-4 sm:px-6 lg:max-w-7xl lg:mx-auto lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  ComChat Dashboard
                </h1>
                <p className="mt-1 text-sm text-gray-500">
                  Monitor your chatbot performance and manage settings
                </p>
              </div>
              <div className="flex space-x-3">
                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
                  <CogIcon className="h-4 w-4 inline mr-2" />
                  Settings
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', name: 'Overview', icon: ChartBarIcon },
              { id: 'conversations', name: 'Conversations', icon: ChatBubbleLeftIcon },
              { id: 'workflows', name: 'Workflows', icon: CircleStackIcon },
              { id: 'channels', name: 'Channels', icon: ComputerDesktopIcon },
              { id: 'billing', name: 'Billing', icon: CurrencyDollarIcon },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                  selectedTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {selectedTab === 'overview' && analytics && (
          <div className="space-y-8">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChatBubbleLeftIcon className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Conversations
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatNumber(analytics.conversations.total_conversations)}
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="text-sm text-gray-600">
                    {analytics.conversations.conversations_today} today, {analytics.conversations.conversations_this_week} this week
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChatBubbleLeftIcon className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Messages Today
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatNumber(analytics.messages.messages_today)}
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="text-sm text-gray-600">
                    {formatNumber(analytics.messages.total_messages)} total messages
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <UserGroupIcon className="h-8 w-8 text-purple-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Active Conversations
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatNumber(analytics.conversations.active_conversations)}
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="text-sm text-gray-600">
                    Avg {analytics.conversations.avg_messages_per_conversation.toFixed(1)} messages/conversation
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CurrencyDollarIcon className="h-8 w-8 text-yellow-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Usage Cost
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatCurrency(analytics.usage.total_cost_cents)}
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="text-sm text-gray-600">
                    {formatNumber(analytics.usage.current_period_ai_requests)} AI requests
                  </div>
                </div>
              </div>
            </div>

            {/* Channel Performance */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Channel Performance</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {Object.entries(analytics.messages.messages_by_channel).map(([channel, count]) => (
                    <div key={channel} className="text-center">
                      <div className="text-2xl font-bold text-gray-900 mb-1">
                        {formatNumber(count)}
                      </div>
                      <div className="text-sm text-gray-500 capitalize">
                        {channel} Messages
                      </div>
                      <div className="mt-2">
                        <div className="bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full"
                            style={{ 
                              width: `${(count / analytics.messages.total_messages) * 100}%` 
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Model Usage */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">AI Model Usage</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {Object.entries(analytics.usage.model_usage).map(([model, count]) => (
                    <div key={model} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="text-sm font-medium text-gray-900">{model}</div>
                        <div className="ml-2 text-xs text-gray-500">
                          {model.includes('local') || model.includes('mistral') || model.includes('llava') ? 'Local' : 'OpenAI'}
                        </div>
                      </div>
                      <div className="flex items-center">
                        <div className="text-sm text-gray-900 mr-4">{formatNumber(count)} requests</div>
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full"
                            style={{ 
                              width: `${(count / Object.values(analytics.usage.model_usage).reduce((a, b) => a + b, 0)) * 100}%` 
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Response Time */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Performance Metrics</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900 mb-1">
                      {analytics.conversations.avg_response_time_ms.toFixed(0)}ms
                    </div>
                    <div className="text-sm text-gray-500">Average Response Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900 mb-1">
                      {(analytics.conversations.avg_response_time_ms < 2000 ? '🟢' : 
                        analytics.conversations.avg_response_time_ms < 5000 ? '🟡' : '🔴')}
                    </div>
                    <div className="text-sm text-gray-500">Performance Status</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'conversations' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Conversations</h3>
            </div>
            <div className="p-6">
              <div className="text-center text-gray-500">
                Conversation management interface coming soon...
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'workflows' && (
          <div className="bg-white rounded-lg shadow">
            <WorkflowManager domain="general" />
          </div>
        )}

        {selectedTab === 'channels' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Channel Configuration</h3>
            </div>
            <div className="p-6">
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center">
                    <ComputerDesktopIcon className="h-8 w-8 text-blue-600 mr-3" />
                    <div>
                      <div className="font-medium">Web Chat</div>
                      <div className="text-sm text-gray-500">Embedded chat widget</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="text-green-600 text-sm mr-3">Active</span>
                    <button className="bg-gray-100 text-gray-600 px-3 py-1 rounded text-sm">
                      Configure
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center">
                    <PhoneIcon className="h-8 w-8 text-green-600 mr-3" />
                    <div>
                      <div className="font-medium">WhatsApp Business</div>
                      <div className="text-sm text-gray-500">WhatsApp Business API integration</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="text-yellow-600 text-sm mr-3">Setup Required</span>
                    <button className="bg-primary-600 text-white px-3 py-1 rounded text-sm">
                      Setup
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center">
                    <ChatBubbleLeftIcon className="h-8 w-8 text-blue-500 mr-3" />
                    <div>
                      <div className="font-medium">Telegram</div>
                      <div className="text-sm text-gray-500">Telegram Bot API</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="text-yellow-600 text-sm mr-3">Setup Required</span>
                    <button className="bg-primary-600 text-white px-3 py-1 rounded text-sm">
                      Setup
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'billing' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Current Plan</h3>
              </div>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xl font-semibold text-gray-900">Free Plan</div>
                    <div className="text-sm text-gray-500">Perfect for getting started</div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">$0</div>
                    <div className="text-sm text-gray-500">per month</div>
                  </div>
                </div>
                <div className="mt-6">
                  <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
                    Upgrade Plan
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Usage This Month</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Messages</span>
                      <span>{analytics?.usage.current_period_messages || 0} / 1,000</span>
                    </div>
                    <div className="mt-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${((analytics?.usage.current_period_messages || 0) / 1000) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>AI Requests</span>
                      <span>{analytics?.usage.current_period_ai_requests || 0} / 500</span>
                    </div>
                    <div className="mt-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${((analytics?.usage.current_period_ai_requests || 0) / 500) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;