'use client';

/**
 * Global Quick Upload Modal component for creating a project and uploading audio
 */

import React, { useState } from 'react';
import { useProjects, useCreateProject } from '@/hooks/useProjects';
import { FileUpload } from '@/components/FileUpload';
import { useRouter } from 'next/navigation';

interface QuickUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function QuickUploadModal({ isOpen, onClose }: QuickUploadModalProps) {
  const router = useRouter();
  const { data: projectsData } = useProjects();
  const createProjectMutation = useCreateProject();

  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [newProjectName, setNewProjectName] = useState('');
  const [isCreatingNew, setIsCreatingNew] = useState(false);

  if (!isOpen) return null;

  const projects = projectsData?.items || [];

  const handleCreateProject = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    createProjectMutation.mutate(
      { name: newProjectName.trim(), description: 'Created via quick upload' },
      {
        onSuccess: (newProject) => {
          setSelectedProjectId(newProject.id);
          setIsCreatingNew(false);
          setNewProjectName('');
        },
      }
    );
  };

  const handleUploadSuccess = (fileId: number) => {
    const targetProject = selectedProjectId || (projects.length > 0 ? projects[0].id : null);
    onClose();
    if (targetProject) {
      router.push(`/projects/${targetProject}`);
    } else {
      router.push('/projects');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-xl overflow-hidden rounded-2xl border border-slate-700/60 bg-slate-900 p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-100">Upload Audio File</h3>
              <p className="text-xs text-slate-400">Select a project or create one to upload your audio</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="py-5 space-y-4">
          {/* Project Selection / Creation Toggle */}
          {!isCreatingNew ? (
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Target Project
              </label>
              <div className="flex gap-2">
                <select
                  value={selectedProjectId || (projects[0]?.id || '')}
                  onChange={(e) => setSelectedProjectId(Number(e.target.value))}
                  className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  {projects.length > 0 ? (
                    projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.audio_files?.length || 0} files)
                      </option>
                    ))
                  ) : (
                    <option value="">No projects available (Create one)</option>
                  )}
                </select>

                <button
                  type="button"
                  onClick={() => setIsCreatingNew(true)}
                  className="rounded-xl border border-blue-500/30 bg-blue-500/10 px-4 py-2.5 text-sm font-medium text-blue-400 hover:bg-blue-500/20 transition-colors"
                >
                  + New Project
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleCreateProject} className="space-y-3 rounded-xl border border-blue-500/30 bg-blue-500/5 p-3.5">
              <label className="block text-xs font-semibold text-blue-300 uppercase tracking-wider">
                New Project Name
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g., Interview Audio Jan 2026"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  required
                  autoFocus
                  className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={createProjectMutation.isPending}
                  className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
                >
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setIsCreatingNew(false)}
                  className="rounded-xl border border-slate-700 bg-slate-800 px-3 py-2 text-sm font-medium text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* Audio Dropzone */}
          <FileUpload
            projectId={selectedProjectId || (projects[0]?.id || 1)}
            onUploadSuccess={handleUploadSuccess}
          />
        </div>
      </div>
    </div>
  );
}
