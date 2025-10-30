import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Mail,
  MessageCircle,
  Zap,
  ShieldCheck,
  Clock,
  ArrowRight,
  CheckCircle2
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                UP2D8
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="px-4 py-2 text-gray-700 hover:text-primary transition-colors font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="px-6 py-2 bg-gradient-to-r from-primary to-secondary text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Background decorations */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-secondary/10 rounded-full blur-3xl"></div>
        </div>

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-8">
              <Sparkles className="h-5 w-5 text-primary" />
              <span className="text-sm font-semibold text-primary">AI-Powered Industry Insights</span>
            </div>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Stay{' '}
              <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                Up-to-Date
              </span>
              {' '}with What Matters
            </h1>

            <p className="text-xl sm:text-2xl text-gray-600 mb-10 leading-relaxed">
              Get personalized daily digests of industry insights, powered by AI.
              No more information overload—just what you need to know, when you need it.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/signup"
                className="group px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 flex items-center gap-2"
              >
                Start Free Today
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/login"
                className="px-8 py-4 border-2 border-gray-300 text-gray-700 font-semibold rounded-xl hover:border-primary hover:text-primary transition-all duration-200"
              >
                Sign In
              </Link>
            </div>

            <p className="mt-6 text-sm text-gray-500">
              Free forever. No credit card required.
            </p>
          </div>

          {/* Hero Image/Mockup Placeholder */}
          <div className="mt-20 max-w-5xl mx-auto">
            <div className="relative rounded-2xl overflow-hidden shadow-2xl border border-gray-200">
              <div className="aspect-[16/9] bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                <div className="text-center p-8">
                  <Mail className="h-24 w-24 mx-auto text-primary/50 mb-4" />
                  <p className="text-gray-600 font-medium">Your daily digest preview goes here</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Stay Informed
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              UP2D8 combines AI-powered curation with personalized delivery to keep you ahead of the curve.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white rounded-xl p-8 shadow-card hover:shadow-card-hover transition-all duration-300">
              <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <Sparkles className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">AI-Powered Summarization</h3>
              <p className="text-gray-600 leading-relaxed">
                Our AI reads thousands of articles daily and distills them into concise, actionable insights tailored to your interests.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-xl p-8 shadow-card hover:shadow-card-hover transition-all duration-300">
              <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <Mail className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Daily Email Digests</h3>
              <p className="text-gray-600 leading-relaxed">
                Receive a beautifully formatted digest every morning with the most relevant news from your industry.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-xl p-8 shadow-card hover:shadow-card-hover transition-all duration-300">
              <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <MessageCircle className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Conversational AI Chat</h3>
              <p className="text-gray-600 leading-relaxed">
                Want to dive deeper? Chat with our AI to explore topics, ask questions, and get personalized insights.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-white rounded-xl p-8 shadow-card hover:shadow-card-hover transition-all duration-300">
              <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Lightning Fast</h3>
              <p className="text-gray-600 leading-relaxed">
                Get your digest in seconds. Our AI processes information faster than any human could.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-white rounded-xl p-8 shadow-card hover:shadow-card-hover transition-all duration-300">
              <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <ShieldCheck className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Trusted Sources</h3>
              <p className="text-gray-600 leading-relaxed">
                We only aggregate from reputable, verified sources in your industry—no spam, no noise.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-white rounded-xl p-8 shadow-card hover:shadow-card-hover transition-all duration-300">
              <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <Clock className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Save Time</h3>
              <p className="text-gray-600 leading-relaxed">
                Spend 5 minutes reading instead of 2 hours scrolling. Get back to what really matters.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Why UP2D8 Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
                Why UP2D8 Beats Generic Newsletters
              </h2>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Personalized to You</h3>
                    <p className="text-gray-600">Unlike one-size-fits-all newsletters, UP2D8 learns your interests and delivers content that matters to you.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">AI-Powered Summaries</h3>
                    <p className="text-gray-600">Get the key insights without reading entire articles. Our AI extracts what's important.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Interactive Exploration</h3>
                    <p className="text-gray-600">Ask questions and dive deeper with our conversational AI—something static newsletters can't do.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Always Current</h3>
                    <p className="text-gray-600">Real-time updates as news breaks, not just weekly roundups that are already outdated.</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-2xl p-8 lg:p-12">
              <div className="space-y-6">
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="h-10 w-10 bg-primary/20 rounded-full flex items-center justify-center">
                      <Sparkles className="h-5 w-5 text-primary" />
                    </div>
                    <h4 className="font-semibold text-gray-900">Your Daily Digest</h4>
                  </div>
                  <p className="text-sm text-gray-600">
                    5 key insights from AI, Tech, and Business
                  </p>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="h-10 w-10 bg-secondary/20 rounded-full flex items-center justify-center">
                      <MessageCircle className="h-5 w-5 text-secondary" />
                    </div>
                    <h4 className="font-semibold text-gray-900">Ask Anything</h4>
                  </div>
                  <p className="text-sm text-gray-600">
                    "Tell me more about the AI regulation update"
                  </p>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-lg">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="h-10 w-10 bg-primary/20 rounded-full flex items-center justify-center">
                      <Mail className="h-5 w-5 text-primary" />
                    </div>
                    <h4 className="font-semibold text-gray-900">Delivered Daily</h4>
                  </div>
                  <p className="text-sm text-gray-600">
                    Every morning at 8 AM in your inbox
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-primary to-secondary">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Stay Up-to-Date?
          </h2>
          <p className="text-xl text-white/90 mb-8">
            Join thousands of professionals who trust UP2D8 for their daily insights.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/signup"
              className="px-8 py-4 bg-white text-primary font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
            >
              Get Started Free
            </Link>
            <Link
              to="/login"
              className="px-8 py-4 border-2 border-white text-white font-semibold rounded-xl hover:bg-white/10 transition-all duration-200"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-4">
                UP2D8
              </div>
              <p className="text-gray-400 text-sm">
                AI-powered industry insights delivered daily.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">FAQ</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-gray-800 text-center text-sm text-gray-400">
            <p>&copy; 2025 UP2D8. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};
