'use client';

/**
 * Modern Project Detail / Workspace page with media management, WaveSurfer player, and interactive transcript engine
 */

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useProject, useProjectAudio, useTranscribeAudio, useProjectTranscript } from '@/hooks/useProjects';
import { FileUpload } from '@/components/FileUpload';
import { AudioPlayer } from '@/components/AudioPlayer';
import { TranscriptViewer } from '@/components/TranscriptViewer';
import { apiClient } from '@/services/api';

function ProjectDetailContent() {
  const params = useParams();
  const projectId = Number(params.projectId);

  const [selectedAudioId, setSelectedAudioId] = useState<number | null>(null);
  const [highlightWord, setHighlightWord] = useState<{ startTime: number; endTime: number } | null>(null);

  const { data: project, isLoading: isProjectLoading, isError: isProjectError } = useProject(projectId);
  const { data: audioData, isLoading: isAudioLoading, refetch: refetchAudio } = useProjectAudio(projectId);
  const { data: transcriptData, isLoading: isTranscriptLoading, refetch: refetchTranscript } = useProjectTranscript(projectId, selectedAudioId);
  const transcribeMutation = useTranscribeAudio();

  const audioFiles = audioData?.items || [];

  // Auto-select first audio file when loaded if none selected
  useEffect(() => {
    if (audioFiles.length > 0 && !selectedAudioId) {
      setSelectedAudioId(audioFiles[0].id);
    }
  }, [audioFiles, selectedAudioId]);

  const selectedAudio = audioFiles.find((audio) => audio.id === selectedAudioId) || audioFiles[0] || null;

  const handleTranscribe = () => {
    if (!selectedAudio) return;
    transcribeMutation.mutate(selectedAudio.id, {
      onSuccess: () => {
        refetchAudio();
        refetchTranscript();
      },
    });
  };

  const handleTimestampSelect = (startTime: number, endTime: number) => {
    setHighlightWord({ startTime, endTime });
  };

  const constructAudioUrl = (storedFilename: string) => apiClient.getAudioUrl(storedFilename);

  if (isProjectLoading) {
    return (
      <div className="py-24 text-center space-y-3">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-400">
          <svg className="h-6 w-6 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
        <p className="text-sm font-medium text-slate-400">Loading project workspace...</p>
      </div>
    );
  }

  if (isProjectError || !project) {
    return (
      <div className="py-20 text-center space-y-4">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-red-500/10 text-red-400 border border-red-500/20">
          ⚠️
        </div>
        <h3 className="text-lg font-bold text-slate-200">Project Not Found</h3>
        <p className="text-xs text-slate-400">The project you are trying to view does not exist or was deleted.</p>
        <Link
          href="/projects"
          className="inline-block rounded-xl bg-blue-600 px-5 py-2 text-xs font-semibold text-white hover:bg-blue-500"
        >
          ← Back to Projects
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 py-2">
      {/* Workspace Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <Link
            href="/projects"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors mb-2"
          >
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>Back to Projects</span>
          </Link>

          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold text-slate-100">{project.name}</h1>
            <span className="rounded-full bg-blue-500/10 px-3 py-0.5 text-xs font-mono font-semibold text-blue-400 border border-blue-500/20">
              Project #{project.id}
            </span>
          </div>

          {project.description && (
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">{project.description}</p>
          )}
        </div>

        <div className="flex items-center gap-3">
          <div className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-2 text-xs text-slate-300">
            <span className="text-slate-500 font-semibold mr-1.5">Audio Files:</span>
            <span className="font-mono font-bold text-blue-400">{audioFiles.length}</span>
          </div>
        </div>
      </div>

      {/* Main Workspace Split Grid */}
      <div className="grid gap-8 lg:grid-cols-12 items-start">
        {/* Left Column: Upload & Audio Player (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* File Upload Dropzone */}
          <FileUpload
            projectId={projectId}
            onUploadSuccess={() => {
              refetchAudio();
            }}
          />

          {/* Audio Files & Selector List */}
          <div className="rounded-2xl border border-slate-700/60 bg-slate-900/80 p-5 shadow-xl backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                Audio Files ({audioFiles.length})
              </h3>
              <span className="text-[11px] text-slate-500">Select file to play/transcribe</span>
            </div>

            {isAudioLoading ? (
              <div className="py-6 text-center text-xs text-slate-400">Loading audio files...</div>
            ) : audioFiles.length > 0 ? (
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {audioFiles.map((audio) => {
                  const isSelected = selectedAudio?.id === audio.id;
                  return (
                    <div
                      key={audio.id}
                      onClick={() => setSelectedAudioId(audio.id)}
                      className={`flex items-center justify-between rounded-xl border p-3 cursor-pointer transition-all ${
                        isSelected
                          ? 'border-blue-500/60 bg-blue-500/10 text-white shadow-sm'
                          : 'border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700 hover:bg-slate-900'
                      }`}
                    >
                      <div className="flex items-center gap-3 overflow-hidden">
                        <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${isSelected ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400'}`}>
                          🎙️
                        </div>
                        <div className="truncate">
                          <p className="text-xs font-semibold truncate">{audio.original_filename || audio.stored_filename}</p>
                          <p className="text-[10px] text-slate-500 uppercase font-mono">
                            {audio.file_format || 'audio'} • {audio.duration_seconds ? `${Math.round(audio.duration_seconds)}s` : 'Unknown duration'}
                          </p>
                        </div>
                      </div>

                      <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-mono font-medium ${
                        audio.upload_status === 'ready'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {audio.upload_status}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="py-6 text-center text-xs text-slate-500">
                No audio files uploaded yet. Drag & drop a file above.
              </div>
            )}
          </div>

          {/* WaveSurfer Player & Transcribe Trigger */}
          {selectedAudio && (
            <div className="space-y-4">
              <AudioPlayer
                audioUrl={constructAudioUrl(selectedAudio.stored_filename)}
                highlightWord={highlightWord}
              />

              <button
                onClick={handleTranscribe}
                disabled={transcribeMutation.isPending}
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 py-3 font-semibold text-white shadow-lg shadow-blue-500/20 hover:from-blue-500 hover:to-indigo-500 active:scale-[0.99] transition-all disabled:opacity-50 text-sm"
              >
                {transcribeMutation.isPending ? (
                  <>
                    <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Transcribing with Whisper AI...</span>
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Transcribe Audio File</span>
                  </>
                )}
              </button>

              {transcribeMutation.isError && (
                <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
                  {(transcribeMutation.error as any)?.response?.data?.detail || 'Transcription failed.'}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Transcript Engine Workspace (7 cols) */}
        <div className="lg:col-span-7">
          <TranscriptViewer
            transcript={transcriptData}
            isLoading={isTranscriptLoading}
            onSelectTimestamp={handleTimestampSelect}
          />
        </div>
      </div>
    </div>
  );
}

export default function ProjectDetailPage() {
  return <ProjectDetailContent />;
}
