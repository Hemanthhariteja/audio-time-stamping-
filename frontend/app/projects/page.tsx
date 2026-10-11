'use client';

/**
 * Projects page with search, creation modal, project deletion, and modern glass card design
 */

import React, { useState, useMemo } from 'react';
import { useProjects, useCreateProject, useDeleteProject } from '@/hooks/useProjects';
import Link from 'next/link';
import { QuickUploadModal } from '@/components/QuickUploadModal';

export default function ProjectsPage() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [deletingProjectId, setDeletingProjectId] = useState<number | null>(null);

  const { data, isLoading, error } = useProjects();
  const createMutation = useCreateProject();
  const deleteMutation = useDeleteProject();

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    createMutation.mutate(formData, {
      onSuccess: () => {
        setFormData({ name: '', description: '' });
        setShowCreateModal(false);
      },
    });
  };

  const handleDeleteConfirm = (projectId: number, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this project and all its audio files?')) {
      deleteMutation.mutate(projectId);
    }
  };

  const filteredProjects = useMemo(() => {
    const items = data?.items || [];
    if (!searchQuery.trim()) return items;
    const q = searchQuery.toLowerCase();
    return items.filter(
      (p) => p.name.toLowerCase().includes(q) || (p.description && p.description.toLowerCase().includes(q))
    );
  }, [data?.items, searchQuery]);

  if (isLoading) {
    return (
      <div className="py-20 text-center space-y-3">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-400">
          <svg className="h-6 w-6 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
        <p className="text-sm font-medium text-slate-400">Loading your project library...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-20 text-center space-y-4">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-red-500/10 text-red-400 border border-red-500/20">
          ⚠️
        </div>
        <h3 className="text-lg font-bold text-slate-200">Unable to load projects</h3>
        <p className="text-xs text-slate-400">Please ensure the backend FastAPI server is running on http://localhost:8000.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 py-4">
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-100">Projects</h1>
          <p className="text-xs text-slate-400 mt-1">Manage audio transcription projects and uploaded media</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center gap-2 rounded-xl border border-blue-500/30 bg-blue-500/10 px-4 py-2.5 text-xs font-semibold text-blue-400 hover:bg-blue-500/20 transition-colors"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span>Upload Audio File</span>
          </button>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-blue-500/20 hover:from-blue-500 hover:to-indigo-500 transition-all"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New Project</span>
          </button>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search projects by name or description..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full rounded-2xl border border-slate-700/80 bg-slate-900/80 px-4 py-3 pl-11 text-sm text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-inner"
        />
        <svg className="absolute left-4 top-3.5 h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <form
            onSubmit={handleCreate}
            className="relative w-full max-w-md overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl space-y-4"
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-slate-100">Create New Project</h3>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-slate-200"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Project Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g. Customer Feedback Calls"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  autoFocus
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Description (Optional)
                </label>
                <textarea
                  placeholder="Brief overview of project contents..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:outline-none resize-none"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="rounded-xl bg-blue-600 px-5 py-2 text-xs font-semibold text-white hover:bg-blue-500 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Project'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Projects Grid */}
      {filteredProjects.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <Link href={`/projects/${project.id}`} key={project.id}>
              <div className="glass-card rounded-2xl p-6 border border-slate-800 h-full flex flex-col justify-between group cursor-pointer">
                <div>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold text-xs">
                        #{project.id}
                      </div>
                      <h3 className="text-lg font-bold text-slate-100 group-hover:text-blue-400 transition-colors">
                        {project.name}
                      </h3>
                    </div>

                    <button
                      onClick={(e) => handleDeleteConfirm(project.id, e)}
                      className="opacity-0 group-hover:opacity-100 rounded-lg p-1.5 text-slate-500 hover:bg-red-500/10 hover:text-red-400 transition-all"
                      title="Delete project"
                    >
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>

                  {project.description && (
                    <p className="text-xs text-slate-400 line-clamp-3 mb-4 leading-relaxed">
                      {project.description}
                    </p>
                  )}
                </div>

                <div className="flex items-center justify-between text-xs text-slate-500 pt-4 border-t border-slate-800/80 mt-auto">
                  <span className="flex items-center gap-1.5 text-slate-400">
                    <svg className="h-4 w-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                    {project.audio_files?.length || 0} files
                  </span>
                  <span className="font-semibold text-blue-400 group-hover:translate-x-1 transition-transform">
                    Open Workspace →
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-12 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-800 text-slate-400 mb-3">
            📁
          </div>
          <h3 className="text-base font-bold text-slate-200">No matching projects</h3>
          <p className="text-xs text-slate-400 mt-1 mb-5">
            {searchQuery ? `No projects match "${searchQuery}"` : 'Create your first project to organize audio files.'}
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="rounded-xl bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white hover:bg-blue-500"
          >
            + Create New Project
          </button>
        </div>
      )}

      {/* Global Quick Upload Modal */}
      <QuickUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
      />
    </div>
  );
}
