import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { neon } from '@neondatabase/serverless';

interface BetaSignupPopupProps {
  onSignupSuccess: () => void;
}

const BetaSignupPopup: React.FC<BetaSignupPopupProps> = ({ onSignupSuccess }) => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [alreadyRegistered, setAlreadyRegistered] = useState(false);
  const [subscribeNewsletter, setSubscribeNewsletter] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      toast.error('Please enter your email address');
      return;
    }

    if (!isValidEmail(email)) {
      toast.error('Please enter a valid email address');
      return;
    }

    setIsSubmitting(true);

    try {
      const dbUrl = process.env.REACT_APP_NEON_DATABASE_URL;

      if (!dbUrl) {
        console.error('Missing REACT_APP_NEON_DATABASE_URL');
        toast.error('Configuration error. Please contact support.');
        setIsSubmitting(false);
        return;
      }

      const sql = neon(dbUrl);

      // Check if email already exists for this product
      const existing = await sql`
        SELECT s.id, sp.beta_access
        FROM signups s
        LEFT JOIN signup_products sp ON s.id = sp.signup_id AND sp.product_name = 'ComChat'
        WHERE s.email = ${email}
      `;

      if (existing.length > 0 && existing[0].beta_access) {
        setAlreadyRegistered(true);
        setIsSubmitting(false);
        return;
      }

      // Insert or get signup
      let signupId: number;

      if (existing.length > 0) {
        // Email exists, just add product
        signupId = existing[0].id;
      } else {
        // New signup
        const newSignup = await sql`
          INSERT INTO signups (email, created_at)
          VALUES (${email}, NOW())
          RETURNING id
        `;
        signupId = newSignup[0].id;
      }

      // Insert product signup
      await sql`
        INSERT INTO signup_products (signup_id, product_name, beta_access, newsletter_subscribe, signed_up_at)
        VALUES (${signupId}, 'ComChat', true, ${subscribeNewsletter}, NOW())
        ON CONFLICT (signup_id, product_name)
        DO UPDATE SET beta_access = true, newsletter_subscribe = ${subscribeNewsletter}
      `;

      // Send email notification via Web3Forms
      const formData = new FormData();
      formData.append('access_key', process.env.REACT_APP_WEB3FORMS_KEY || '');
      formData.append('subject', 'New Beta Signup - ComChat');
      formData.append('from_name', 'ComChat Beta');
      formData.append('message', `New beta signup from: ${email}\n\nTimestamp: ${new Date().toISOString()}`);

      await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        body: formData
      });

      toast.success('Thanks for signing up! We\'ll be in touch soon.');
      onSignupSuccess();
    } catch (error) {
      console.error('Signup error:', error);
      toast.error('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-8 animate-scale-in">
        {alreadyRegistered ? (
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-2xl mx-auto flex items-center justify-center mb-6">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-medium text-black mb-3">
              You're already on the list!
            </h2>
            <p className="text-gray-600 leading-relaxed mb-8">
              We've got your email. We'll notify you as soon as ComChat is ready for you.
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="w-full bg-black text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-800 transition-colors"
            >
              Back to homepage
            </button>
          </div>
        ) : (
          <>
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-black rounded-2xl mx-auto flex items-center justify-center mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h2 className="text-2xl font-medium text-black mb-3">
                Join the beta
              </h2>
              <p className="text-gray-600 leading-relaxed">
                ComChat is currently in beta. Enter your email to get early access and be the first to experience truly human-like chatbots.
              </p>
            </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email address
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-500"
              disabled={isSubmitting}
              autoFocus
            />
          </div>

          <div className="flex items-start">
            <input
              type="checkbox"
              id="newsletter"
              checked={subscribeNewsletter}
              onChange={(e) => setSubscribeNewsletter(e.target.checked)}
              className="mt-1 w-4 h-4 text-black border-gray-300 rounded focus:ring-black"
              disabled={isSubmitting}
            />
            <label htmlFor="newsletter" className="ml-3 text-sm text-gray-700">
              Subscribe to Zonda newsletter for updates and product news
            </label>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-black text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isSubmitting ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                Signing up...
              </>
            ) : (
              'Join the beta'
            )}
          </button>
        </form>
          </>
        )}
      </div>
    </div>
  );
};

export default BetaSignupPopup;