import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen hero-gradient">
      {/* Navigation */}
      <nav className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-display font-bold brand-gradient">
                ComChat
              </h1>
            </div>
            <div className="hidden sm:flex items-center space-x-8">
              <Link to="/chat" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Live Demo
              </Link>
              <Link to="/admin" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Analytics
              </Link>
              <button className="btn-primary">
                Get Quote
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center">
            <div className="animate-fade-in-up">
              <h1 className="text-6xl md:text-7xl lg:text-8xl font-display font-bold text-gradient mb-8 tracking-tight">
                ComChat Demo
              </h1>
              <p className="text-2xl md:text-3xl font-display font-medium text-gray-700 mb-8 max-w-4xl mx-auto leading-tight">
                Custom AI Chatbots for Any Industry
              </p>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed mb-12">
                Experience our intelligent chatbot platform in action. We build custom AI assistants 
                tailored to your business needs - from healthcare to e-commerce, finance to education. 
                Try our demo and see how AI can transform your customer interactions.
              </p>
            </div>

            <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-md mx-auto">
                <Link
                  to="/chat"
                  className="btn-primary w-full sm:w-auto flex justify-center items-center space-x-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <span>Try Live Demo</span>
                </Link>
                
                <Link
                  to="/admin"
                  className="btn-secondary w-full sm:w-auto flex justify-center items-center space-x-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <span>View Analytics</span>
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-32 h-32 bg-gradient-to-br from-brand-400/10 to-accent-blue/10 rounded-full blur-xl animate-pulse-subtle"></div>
        <div className="absolute top-40 right-20 w-24 h-24 bg-gradient-to-br from-accent-purple/10 to-accent-pink/10 rounded-full blur-xl animate-pulse-subtle" style={{ animationDelay: '1s' }}></div>
        <div className="absolute bottom-20 left-1/4 w-20 h-20 bg-gradient-to-br from-accent-green/10 to-accent-mint/10 rounded-full blur-xl animate-pulse-subtle" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Features Section */}
      <div className="py-24 bg-surface-primary/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-display font-bold text-gradient mb-6">
              Custom AI Chatbots for Every Industry
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We build intelligent conversational AI solutions tailored to your specific business needs and industry requirements
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="feature-card group animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              <div className="icon-wrapper bg-gradient-to-br from-brand-500 to-brand-600 mx-auto mb-6">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <h3 className="text-2xl font-display font-semibold text-gray-900 mb-4">Industry-Specific Training</h3>
              <p className="text-gray-600 leading-relaxed">
                Custom-trained AI models with deep knowledge of your industry, from healthcare compliance to financial regulations and e-commerce best practices.
              </p>
            </div>
            
            <div className="feature-card group animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="icon-wrapper bg-gradient-to-br from-accent-green to-accent-mint mx-auto mb-6">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
              </div>
              <h3 className="text-2xl font-display font-semibold text-gray-900 mb-4">Flexible Integration</h3>
              <p className="text-gray-600 leading-relaxed">
                Deploy across websites, mobile apps, WhatsApp, Telegram, and more. API-first design ensures seamless integration with your existing systems.
              </p>
            </div>
            
            <div className="feature-card group animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <div className="icon-wrapper bg-gradient-to-br from-accent-purple to-accent-pink mx-auto mb-6">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-2xl font-display font-semibold text-gray-900 mb-4">Enterprise Security</h3>
              <p className="text-gray-600 leading-relaxed">
                Bank-level security, GDPR compliance, and data privacy protection. Your customer data stays secure with end-to-end encryption.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div className="py-24 bg-surface-secondary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-display font-bold text-gradient mb-6">
              Choose Your Perfect Plan
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Transparent pricing for custom AI chatbot solutions. From startups to enterprise, we have a plan that scales with your business.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Starter Plan */}
            <div className="card p-8 relative animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              <div className="text-center">
                <h3 className="text-2xl font-display font-bold text-gray-900 mb-2">Starter</h3>
                <p className="text-gray-600 mb-6">Perfect for small businesses</p>
                <div className="mb-8">
                  <span className="text-5xl font-display font-bold text-gradient">$29</span>
                  <span className="text-gray-600 ml-2">/month</span>
                </div>
                
                <ul className="space-y-4 mb-8 text-left">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Up to 5,000 messages/month</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">500 active conversations</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Text-only conversations</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Basic analytics dashboard</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Web chat integration</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Email support</span>
                  </li>
                </ul>
                
                <button className="btn-secondary w-full">
                  Get Started
                </button>
              </div>
            </div>

            {/* Professional Plan - Featured */}
            <div className="card p-8 relative border-2 border-brand-500 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-gradient-to-r from-brand-500 to-brand-600 text-white px-6 py-2 rounded-full text-sm font-medium shadow-apple">
                  Most Popular
                </span>
              </div>
              
              <div className="text-center">
                <h3 className="text-2xl font-display font-bold text-gray-900 mb-2">Professional</h3>
                <p className="text-gray-600 mb-6">Ideal for growing companies</p>
                <div className="mb-8">
                  <span className="text-5xl font-display font-bold text-gradient">$79</span>
                  <span className="text-gray-600 ml-2">/month</span>
                </div>
                
                <ul className="space-y-4 mb-8 text-left">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Up to 25,000 messages/month</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">2,500 active conversations</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700"><strong>Multimodal support</strong> (text + images)</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Advanced analytics & insights</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Multi-channel integration</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Priority support & training</span>
                  </li>
                </ul>
                
                <button className="btn-primary w-full">
                  Start Free Trial
                </button>
              </div>
            </div>

            {/* Enterprise Plan */}
            <div className="card p-8 relative animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <div className="text-center">
                <h3 className="text-2xl font-display font-bold text-gray-900 mb-2">Enterprise</h3>
                <p className="text-gray-600 mb-6">For large organizations</p>
                <div className="mb-8">
                  <span className="text-5xl font-display font-bold text-gradient">Custom</span>
                  <span className="text-gray-600 ml-2">pricing</span>
                </div>
                
                <ul className="space-y-4 mb-8 text-left">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Unlimited messages & conversations</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700"><strong>Full multimodal AI</strong> (text, images, voice)</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Custom AI model training</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">White-label solution</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">Dedicated account manager</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 text-accent-green mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">24/7 premium support</span>
                  </li>
                </ul>
                
                <button className="btn-secondary w-full">
                  Contact Sales
                </button>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-16 text-center">
            <p className="text-gray-600 mb-4">
              All plans include: Custom branding, API access, webhook integrations, and 99.9% uptime SLA
            </p>
            <p className="text-sm text-gray-500">
              Need a custom solution? <button className="text-brand-600 hover:text-brand-700 font-medium underline">Contact us</button> for volume discounts and industry-specific packages.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20 bg-gradient-to-br from-brand-50 to-brand-100">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-display font-bold text-gradient mb-6">
            See ComChat in Action
          </h2>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            Try our interactive demo and discover how custom AI chatbots can revolutionize your customer interactions across any industry.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              to="/chat"
              className="btn-primary inline-flex items-center space-x-2 text-lg px-8 py-4"
            >
              <span>Experience Live Demo</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </Link>
            <button className="btn-secondary inline-flex items-center space-x-2 text-lg px-8 py-4">
              <span>Schedule Consultation</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;