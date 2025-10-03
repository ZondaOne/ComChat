import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import ComingSoonPopup from '../components/ComingSoonPopup';
import Logo from '../components/common/Logo';

const HomePage: React.FC = () => {
  const [isComingSoonPopupOpen, setIsComingSoonPopupOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Logo className="text-black" width="28" height="28" />
              <h1 className="text-lg font-medium text-black">
                ComChat
              </h1>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#how" className="text-gray-600 hover:text-black font-normal">How it works</a>
              <a href="#pricing" className="text-gray-600 hover:text-black font-normal">Pricing</a>
              <Link to="/chat" className="text-gray-600 hover:text-black font-normal">Try it</Link>
            </div>

            <div className="flex items-center space-x-4">
              <Link to="/chat" className="bg-black text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors">
                Start free
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="min-h-screen pt-16 bg-white flex items-center">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 w-full">
          <div className="grid lg:grid-cols-2 gap-8 lg:gap-16 items-center min-h-[85vh]">
            {/* Left - Copy */}
            <div className="space-y-6 lg:space-y-8 order-2 lg:order-1">
              <div className="space-y-4 lg:space-y-6">
                <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-medium text-black leading-tight">
                  Chatbots that actually
                  <br />
                  <span className="italic">sound human</span>
                </h1>
                
                <p className="text-lg sm:text-xl lg:text-2xl text-gray-600 leading-relaxed max-w-lg">
                  Your customers can't tell the difference. 
                  That's the point.
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
                <Link to="/chat" className="bg-black text-white px-6 sm:px-8 py-3 sm:py-4 rounded-lg font-medium hover:bg-gray-800 transition-colors w-full sm:w-auto text-center">
                  See it in action
                </Link>
                <span className="text-gray-400 text-sm">No signup required</span>
              </div>
            </div>
            
            {/* Right - Live Chat Demo */}
            <div className="relative order-1 lg:order-2">
              <div className="bg-white border border-gray-200 rounded-2xl shadow-lg overflow-hidden mx-auto max-w-md lg:max-w-none">
                {/* Chat Header */}
                <div className="bg-gray-50 px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium text-gray-900">Support Chat</span>
                  </div>
                </div>
                
                {/* Chat Messages - No scroll, shows full conversation */}
                <div className="p-4 sm:p-6 space-y-4 h-[500px] sm:h-[600px] lg:h-[650px] xl:h-[700px]">
                  <div className="flex items-start space-x-3">
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gray-200 rounded-full flex-shrink-0"></div>
                    <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-3 sm:px-4 py-2 sm:py-3 max-w-[250px] sm:max-w-xs">
                      <p className="text-xs sm:text-sm text-gray-900">Hi! I'm looking for a refund on my order from last week.</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3 justify-end">
                    <div className="bg-black text-white rounded-2xl rounded-tr-sm px-3 sm:px-4 py-2 sm:py-3 max-w-[250px] sm:max-w-xs">
                      <p className="text-xs sm:text-sm">I'd be happy to help with that! Let me pull up your recent orders. What's the email address on your account?</p>
                    </div>
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-black rounded-full flex-shrink-0"></div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gray-200 rounded-full flex-shrink-0"></div>
                    <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-3 sm:px-4 py-2 sm:py-3 max-w-[250px] sm:max-w-xs">
                      <p className="text-xs sm:text-sm text-gray-900">sarah.chen@email.com</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3 justify-end">
                    <div className="bg-black text-white rounded-2xl rounded-tr-sm px-3 sm:px-4 py-2 sm:py-3 max-w-[250px] sm:max-w-xs">
                      <p className="text-xs sm:text-sm">Perfect! I see your order #4729 from March 15th. That looks like it was for the wireless headphones, right? I can definitely process that refund for you.</p>
                    </div>
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-black rounded-full flex-shrink-0"></div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gray-200 rounded-full flex-shrink-0"></div>
                    <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-3 sm:px-4 py-2 sm:py-3 max-w-[250px] sm:max-w-xs">
                      <p className="text-xs sm:text-sm text-gray-900">Wow, that was fast! Yes, exactly. Thank you!</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3 justify-end">
                    <div className="bg-black text-white rounded-2xl rounded-tr-sm px-3 sm:px-4 py-2 sm:py-3 max-w-[250px] sm:max-w-xs">
                      <p className="text-xs sm:text-sm">You're welcome! I've processed your refund and you should see it back on your card within 3-5 business days. Is there anything else I can help you with today?</p>
                    </div>
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-black rounded-full flex-shrink-0"></div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-7 h-7 sm:w-8 sm:h-8 bg-gray-200 rounded-full flex-shrink-0"></div>
                    <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-3 sm:px-4 py-2 sm:py-3 max-w-[250px] sm:max-w-xs">
                      <p className="text-xs sm:text-sm text-gray-900">That's perfect, thank you so much for your help!</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 text-gray-400 mt-6">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-xs">Bot is typing...</span>
                  </div>
                </div>
              </div>
              
              {/* Floating indicator */}
              <div className="absolute -bottom-3 -right-3 sm:-bottom-4 sm:-right-4 bg-white border border-gray-200 rounded-full px-2 py-1 sm:px-3 sm:py-2 shadow-lg">
                <span className="text-xs font-medium text-gray-600">100% AI</span>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* How it Works */}
      <section id="how" className="py-16 sm:py-20 lg:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl font-medium text-black mb-4">
              How we make it sound human
            </h2>
            <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto">
              It's not just advanced AI. It's conversation design.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-10 lg:gap-12">
            <div className="text-center space-y-4">
              <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gray-100 rounded-xl flex items-center justify-center mx-auto">
                <svg className="w-7 h-7 sm:w-8 sm:h-8 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-base sm:text-lg font-medium text-black">Conversation Training</h3>
              <p className="text-gray-600 text-sm leading-relaxed max-w-xs mx-auto">
                We train our models on thousands of real customer service conversations, not generic chatbot responses.
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gray-100 rounded-xl flex items-center justify-center mx-auto">
                <svg className="w-7 h-7 sm:w-8 sm:h-8 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-base sm:text-lg font-medium text-black">Empathy Engine</h3>
              <p className="text-gray-600 text-sm leading-relaxed max-w-xs mx-auto">
                Our AI detects emotional context and responds with appropriate empathy, not just information.
              </p>
            </div>
            
            <div className="text-center space-y-4 sm:col-span-2 lg:col-span-1">
              <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gray-100 rounded-xl flex items-center justify-center mx-auto">
                <svg className="w-7 h-7 sm:w-8 sm:h-8 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-base sm:text-lg font-medium text-black">Natural Language</h3>
              <p className="text-gray-600 text-sm leading-relaxed max-w-xs mx-auto">
                We eliminate robotic phrases and corporate jargon. Every response sounds like something a real person would say.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-16 sm:py-20 lg:py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl font-medium text-black mb-4">
              Simple pricing
            </h2>
            <p className="text-base sm:text-lg text-gray-600">
              Choose the perfect plan for your business. Scale up or down anytime.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8 max-w-6xl mx-auto">
            {/* Starter Plan */}
            <div className="bg-white border border-gray-200 p-8 rounded-xl hover:-translate-y-1 transition-all duration-300">
              <div className="text-center">
                <h3 className="text-xl font-medium text-black mb-2">Starter</h3>
                <p className="text-gray-600 mb-6">Perfect for small businesses</p>
                <div className="mb-8">
                  <span className="text-4xl font-medium text-black">$49</span>
                  <span className="text-gray-500 ml-2">/month</span>
                </div>
                
                <ul className="space-y-3 mb-8 text-left">
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">1,000 conversations/month</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">Website integration</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">Basic analytics</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">Email support</span>
                  </li>
                </ul>
                
                <Link to="/chat" className="w-full border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors inline-block text-center">
                  Start Free Trial
                </Link>
              </div>
            </div>

            {/* Professional Plan - Featured */}
            <div className="bg-white border-2 border-black p-8 rounded-xl relative hover:-translate-y-1 transition-all duration-300">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-black text-white px-3 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </span>
              </div>
              
              <div className="text-center">
                <h3 className="text-xl font-medium text-black mb-2">Professional</h3>
                <p className="text-gray-600 mb-6">Ideal for growing companies</p>
                <div className="mb-8">
                  <span className="text-4xl font-medium text-black">$149</span>
                  <span className="text-gray-500 ml-2">/month</span>
                </div>
                
                <ul className="space-y-3 mb-8 text-left">
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">5,000 conversations/month</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">Multi-channel support</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">Advanced analytics</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">Priority support</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">Custom integrations</span>
                  </li>
                </ul>
                
                <Link to="/chat" className="w-full bg-black text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-800 transition-colors inline-block text-center">
                  Start Free Trial
                </Link>
              </div>
            </div>

            {/* Enterprise Plan */}
            <div className="bg-white border border-gray-200 p-8 rounded-xl hover:-translate-y-1 transition-all duration-300">
              <div className="text-center">
                <h3 className="text-xl font-medium text-black mb-2">Enterprise</h3>
                <p className="text-gray-600 mb-6">For large organizations</p>
                <div className="mb-8">
                  <span className="text-4xl font-medium text-black">Custom</span>
                </div>
                
                <ul className="space-y-3 mb-8 text-left">
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">Unlimited conversations</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">White-label solution</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">Custom model training</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">Dedicated account manager</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 text-sm">24/7 premium support</span>
                  </li>
                </ul>
                
                <a href="mailto:team@zonda.one" className="w-full border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors inline-block text-center">
                  Contact Sales
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 sm:py-20 lg:py-24 bg-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6">
          <h2 className="text-2xl sm:text-3xl font-medium text-black mb-4">
            Try it yourself
          </h2>
          <p className="text-base sm:text-lg text-gray-600 mb-8">
            See how natural our conversations feel. No setup required.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              to="/chat"
              className="bg-black text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-800 transition-colors w-full sm:w-auto"
            >
              Start chatting
            </Link>
            <span className="text-gray-400 hidden sm:block">or</span>
            <button
              onClick={() => setIsComingSoonPopupOpen(true)}
              className="text-gray-600 hover:text-black font-medium"
            >
              Watch a demo
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-50 border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <Logo className="text-black" width="24" height="24" />
              <a href="https://zonda.one" className="font-medium text-black hover:text-gray-700 transition-colors">ZONDA</a>
            </div>
            
            <div className="flex items-center flex-wrap justify-center md:justify-end space-x-6 sm:space-x-8 text-sm">
              <a href="mailto:team@zonda.one" className="text-gray-600 hover:text-black">Contact</a>
            </div>
          </div>
          
          <div className="mt-6 sm:mt-8 pt-6 sm:pt-8 border-t border-gray-100 text-center">
            <p className="text-gray-500 text-xs sm:text-sm">© 2025 ZONDA. Made with care for human conversations.</p>
          </div>
        </div>
      </footer>

      <ComingSoonPopup
        isOpen={isComingSoonPopupOpen}
        onClose={() => setIsComingSoonPopupOpen(false)}
      />
    </div>
  );
};

export default HomePage;