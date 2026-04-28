import React from 'react';
import { motion } from 'framer-motion';
import { Rocket, BarChart3, ShieldCheck, Zap } from 'lucide-react';

const MissionControl: React.FC = () => {
  return (
    <main className="w-full">
      {/* Hero Section */}
      <section className="hero-gradient pt-24 pb-16 px-6 flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-3xl"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-brand-light text-brand-deep pill mono-label mb-6">
            <Rocket className="w-3.5 h-3.5" />
            <span>Autonomous Engine v1.0</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-semibold text-near-black leading-[1.1] tight-tracking mb-6">
            Experience, <span className="text-brand">Automated.</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-500 max-w-2xl mx-auto leading-relaxed mb-10">
            Transform raw event media into platform-ready marketing assets. Driven by multimodal agents, curated by mathematics.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button className="bg-near-black text-white px-8 py-3.5 pill text-base font-medium hover:opacity-90 transition-all shadow-md flex items-center gap-2">
              <Zap className="w-5 h-5 fill-brand text-brand" />
              New Session
            </button>
            <button className="bg-white border border-gray-200 text-near-black px-8 py-3.5 pill text-base font-medium hover:bg-gray-50 transition-all shadow-sm">
              View Analytics
            </button>
          </div>
        </motion.div>
      </section>

      {/* Stats/Features Grid */}
      <section className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          {
            icon: <BarChart3 className="w-6 h-6 text-brand" />,
            title: "Live Telemetry",
            desc: "Monitor aesthetic scores, saliency heatmaps, and agent reasoning in real-time."
          },
          {
            icon: <ShieldCheck className="w-6 h-6 text-brand" />,
            title: "QA Safeguards",
            desc: "Zero-shot confidence scoring flags low-quality assets for human review."
          },
          {
            icon: <Rocket className="w-6 h-6 text-brand" />,
            title: "Multi-Platform",
            desc: "Native outputs for LinkedIn, Instagram Reels, Stories, and Case Studies."
          }
        ].map((feature, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * (i + 1) }}
            className="p-8 bg-white border border-border-subtle card-rounded shadow-card hover:border-border-medium transition-all group"
          >
            <div className="w-12 h-12 bg-gray-50 pill flex items-center justify-center mb-6 group-hover:bg-brand-light transition-colors">
              {feature.icon}
            </div>
            <h3 className="text-xl font-semibold mb-3 text-near-black">{feature.title}</h3>
            <p className="text-gray-500 leading-relaxed text-sm">
              {feature.desc}
            </p>
          </motion.div>
        ))}
      </section>

      {/* Placeholder for Recent Sessions */}
      <section className="max-w-7xl mx-auto px-6 py-12">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-semibold text-near-black">Recent Sessions</h2>
          <button className="text-sm font-medium text-brand hover:text-brand-deep transition-colors">
            View all sessions →
          </button>
        </div>
        
        <div className="grid grid-cols-1 gap-4">
          {[1, 2].map((session) => (
            <div key={session} className="flex items-center justify-between p-5 bg-white border border-border-subtle card-rounded hover:border-border-medium transition-all cursor-pointer">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-gray-100 pill flex items-center justify-center font-mono text-xs font-bold">
                  S{session}
                </div>
                <div>
                  <h4 className="font-medium text-near-black">Google India SMB Summit</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="mono-label text-[10px] text-gray-400">Apr 28, 2026</span>
                    <span className="w-1 h-1 bg-gray-300 pill"></span>
                    <span className="text-[11px] text-brand-deep font-medium">Completed</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right hidden sm:block">
                  <div className="text-sm font-semibold text-near-black">128 Assets</div>
                  <div className="text-[11px] text-gray-400">4 Outputs Generated</div>
                </div>
                <button className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-near-black hover:bg-gray-50 pill transition-all">
                  <Zap className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
};

export default MissionControl;
