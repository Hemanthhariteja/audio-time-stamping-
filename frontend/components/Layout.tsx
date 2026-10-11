'use client';

/**
 * Main layout component for the application with navigation, global quick upload, and dark glass styling
 */

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { QuickUploadModal } from '@/components/QuickUploadModal';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const pathname = usePathname();
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === '/' && pathname === '/') return true;
    if (path !== '/' && pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col selection:bg-blue-500/30 selection:text-blue-200">
      {/* Navigation Header */}
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo & Brand */}
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white font-black text-base shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
                <span>AT</span>
                <div className="absolute inset-0 rounded-xl bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-base tracking-tight text-slate-100 group-hover:text-blue-400 transition-colors">
                  AudioTimestamp
                </span>
                <span className="text-[10px] font-mono tracking-widest text-slate-500 uppercase">
                  Whisper AI Engine
                </span>
              </div>
            </Link>

            {/* Navigation Links */}
            <nav className="hidden md:flex items-center space-x-1 bg-slate-900/60 p-1.5 rounded-xl border border-slate-800/80">
              <Link
                href="/"
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  isActive('/')
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                Dashboard
              </Link>
              <Link
                href="/projects"
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  isActive('/projects')
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                Projects
              </Link>
            </nav>

            {/* Right Action Controls */}
            <div className="flex items-center space-x-3">
              {/* Quick Upload CTA Button */}
              <button
                onClick={() => setIsUploadModalOpen(true)}
                className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-blue-500/20 hover:from-blue-500 hover:to-indigo-500 active:scale-95 transition-all"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>Upload Audio</span>
              </button>

              <div className="h-6 w-px bg-slate-800 hidden sm:block" />

              <div className="flex items-center space-x-2">
                <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700/60 flex items-center justify-center text-xs font-bold text-blue-400">
                  AI
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Page Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 bg-slate-950/60 text-slate-400 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div className="h-6 w-6 rounded-lg bg-blue-600 flex items-center justify-center text-white font-black text-xs">
                  AT
                </div>
                <span className="font-bold text-slate-200">AudioTimestamp AI</span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                High-precision Whisper AI audio transcription with sentence and word-level timestamps.
              </p>
            </div>
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">Platform</h4>
              <ul className="space-y-2 text-xs">
                <li>
                  <Link href="/projects" className="hover:text-blue-400 transition-colors">
                    My Projects
                  </Link>
                </li>
                <li>
                  <button onClick={() => setIsUploadModalOpen(true)} className="hover:text-blue-400 transition-colors">
                    Upload Audio File
                  </button>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">Export Formats</h4>
              <div className="flex flex-wrap gap-1.5 font-mono text-[10px]">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/50">TXT</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/50">JSON</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/50">CSV</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/50">SRT</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/50">VTT</span>
              </div>
            </div>
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">Engine</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                Powered by Faster-Whisper, PyTorch GPU acceleration, and Next.js 14.
              </p>
            </div>
          </div>
          <div className="border-t border-slate-800/40 mt-8 pt-6 text-xs text-center text-slate-600">
            <p>&copy; 2026 AudioTimestamp Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Global Quick Upload Modal */}
      <QuickUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
      />
    </div>
  );
}
