import React from 'react';
import { Sparkles } from 'lucide-react';

const Navbar: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 glass w-full flex justify-center">
      <div className="max-w-7xl w-full px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-near-black pill flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-brand" />
          </div>
          <span className="font-semibold text-lg tracking-tight text-near-black">StepOne AI</span>
        </div>

        <nav className="hidden md:flex items-center gap-8">
          <a href="#" className="text-sm font-medium text-gray-700 hover:text-brand transition-colors">Sessions</a>
          <a href="#" className="text-sm font-medium text-gray-700 hover:text-brand transition-colors">Assets</a>
          <a href="#" className="text-sm font-medium text-gray-700 hover:text-brand transition-colors">Documentation</a>
        </nav>

        <div className="flex items-center gap-4">
          <button className="text-sm font-medium text-gray-700 hover:text-near-black transition-colors px-3 py-2">
            Sign In
          </button>
          <button className="bg-near-black text-white px-5 py-2 pill text-sm font-medium hover:opacity-90 transition-all shadow-sm">
            Get Started
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
