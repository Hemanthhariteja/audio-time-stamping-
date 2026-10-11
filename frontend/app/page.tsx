'use client';

/**
 * Modern Dashboard / Landing Page with quick audio dropzone and project hub
 */

import React, { useState } from 'react';
import Link from 'next/link';
import { useProjects } from '@/hooks/useProjects';
import { FileUpload } from '@/components/FileUpload';
import { QuickUploadModal } from '@/components/QuickUploadModal';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const { data: projectsData, isLoading: isProjectsLoading } = useProjects();
  const [isQuickUploadOpen, setIsQuickUploadOpen] = useState(false);

  const projects = projectsData?.items || [];

  const handleUploadSuccess = (fileId: number) => {
    if (projects.length > 0) {
      router.push(`/projects/${projects[0].id}`);
    } else {
      router.push('/projects');
    }
  };

  return (
    <div className="space-y-16 py-4">
      {/* Hero Section with Quick Dropzone */}
      <section className="relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-950/60 p-8 sm:p-12 shadow-2xl backdrop-blur-xl">
        <div className="absolute -left-20 -top-20 h-72 w-72 rounded-full bg-blue-600/20 blur-3xl" />
        <div className="absolute -right-20 -bottom-20 h-72 w-72 rounded-full bg-indigo-600/20 blur-3xl" />

        <div className="relative z-10 grid lg:grid-cols-12 gap-10 items-center">
          {/* Left Hero Text */}
          <div className="lg:col-span-7 space-y-6 text-left">
            <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1 text-xs font-semibold text-blue-400">
              <span className="flex h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
              Whisper AI Audio Timestamping Engine v1.0
            </div>

            <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-100 leading-tight">
              Turn Audio Files into <br />
              <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
                Precise Timestamps
              </span>
            </h1>

            <p className="text-base text-slate-400 max-w-xl leading-relaxed">
              Convert MP3, WAV, M4A, AAC, and FLAC audio files into accurate transcripts with word-level and sentence-level timing. Export directly to TXT, JSON, CSV, SRT, or VTT.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link
                href="/projects"
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 hover:from-blue-500 hover:to-indigo-500 active:scale-95 transition-all"
              >
                <span>View All Projects</span>
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </Link>

              <button
                onClick={() => setIsQuickUploadOpen(true)}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-6 py-3 text-sm font-semibold text-slate-200 hover:bg-slate-800 transition-colors"
              >
                <svg className="h-4 w-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span>Quick Upload</span>
              </button>
            </div>
          </div>

          {/* Right Direct File Dropzone Card */}
          <div className="lg:col-span-5">
            <div className="rounded-2xl border border-slate-700/80 bg-slate-900/90 p-4 shadow-xl backdrop-blur-md">
              <div className="mb-3 px-2 flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Fast Upload Zone</span>
                <span className="text-[11px] font-mono text-blue-400">Direct Drag & Drop</span>
              </div>
              <FileUpload
                projectId={projects[0]?.id || 1}
                onUploadSuccess={handleUploadSuccess}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Stats Counter Bar */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Accuracy Rate', value: '99.5%', icon: '🎯' },
          { label: 'Export Formats', value: '5 Formats', icon: '📄' },
          { label: 'Word Timestamps', value: 'Millisecond', icon: '⏱️' },
          { label: 'Supported Formats', value: 'MP3/WAV/M4A/FLAC', icon: '🎙️' },
        ].map((stat, i) => (
          <div key={i} className="glass-card rounded-2xl p-5 border border-slate-800 text-center">
            <div className="text-2xl mb-1">{stat.icon}</div>
            <div className="text-2xl font-black text-slate-100">{stat.value}</div>
            <div className="text-xs text-slate-400 font-medium">{stat.label}</div>
          </div>
        ))}
      </section>

      {/* Recent Projects Hub */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-100">Recent Projects</h2>
            <p className="text-xs text-slate-400">Select a project workspace to inspect files & transcripts</p>
          </div>

          <Link
            href="/projects"
            className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <span>View All</span>
            <span>→</span>
          </Link>
        </div>

        {isProjectsLoading ? (
          <div className="grid md:grid-cols-3 gap-6">
            {[1, 2, 3].map((n) => (
              <div key={n} className="h-36 animate-pulse rounded-2xl bg-slate-900 border border-slate-800" />
            ))}
          </div>
        ) : projects.length > 0 ? (
          <div className="grid md:grid-cols-3 gap-6">
            {projects.slice(0, 3).map((project) => (
              <Link href={`/projects/${project.id}`} key={project.id}>
                <div className="glass-card rounded-2xl p-6 border border-slate-800 h-full flex flex-col justify-between group cursor-pointer">
                  <div>
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-lg font-bold text-slate-100 group-hover:text-blue-400 transition-colors">
                        {project.name}
                      </h3>
                      <span className="rounded-full bg-blue-500/10 px-2.5 py-0.5 text-[11px] font-medium text-blue-400 border border-blue-500/20">
                        ID: {project.id}
                      </span>
                    </div>
                    {project.description && (
                      <p className="text-xs text-slate-400 line-clamp-2 mb-4">
                        {project.description}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center justify-between text-xs text-slate-500 pt-4 border-t border-slate-800/80">
                    <span className="flex items-center gap-1 text-slate-400">
                      <svg className="h-4 w-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                      {project.audio_files?.length || 0} audio files
                    </span>
                    <span className="font-semibold text-blue-400 group-hover:translate-x-1 transition-transform">
                      Open →
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-12 text-center">
            <p className="text-slate-400 text-sm mb-4">No projects created yet.</p>
            <button
              onClick={() => setIsQuickUploadOpen(true)}
              className="rounded-xl bg-blue-600 px-6 py-2.5 text-xs font-semibold text-white hover:bg-blue-500"
            >
              Upload Audio & Create Project
            </button>
          </div>
        )}
      </section>

      {/* Features Overview */}
      <section className="grid md:grid-cols-3 gap-6">
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400 mb-4 border border-blue-500/20">
            🎙️
          </div>
          <h3 className="text-base font-bold text-slate-100 mb-2">Multiple Audio Formats</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Upload MP3, WAV, M4A, AAC, OGG, FLAC, and MP4 audio files seamlessly with instant status readiness.
          </p>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10 text-purple-400 mb-4 border border-purple-500/20">
            ⏱️
          </div>
          <h3 className="text-base font-bold text-slate-100 mb-2">Word & Sentence Timing</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Gain millisecond-precise timing for individual words and full sentences synced with WaveSurfer playback.
          </p>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 mb-4 border border-emerald-500/20">
            📊
          </div>
          <h3 className="text-base font-bold text-slate-100 mb-2">Export in 5 Standard Formats</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Download your completed transcripts instantly in TXT, JSON, CSV, SRT subtitle, or VTT format.
          </p>
        </div>
      </section>

      <QuickUploadModal
        isOpen={isQuickUploadOpen}
        onClose={() => setIsQuickUploadOpen(false)}
      />
    </div>
  );
}
