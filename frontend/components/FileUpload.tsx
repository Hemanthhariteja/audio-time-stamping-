'use client';

/**
 * Foolproof FileUpload using Tailwind file input styling
 */

import React, { useCallback, useState } from 'react';
import { useUploadAudio } from '@/hooks/useProjects';

interface FileUploadProps {
  projectId: number;
  onUploadSuccess?: (fileId: number) => void;
  onUploadError?: (error: string) => void;
}

const ALLOWED_EXTENSIONS = ['mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac', 'mp4'];

export function FileUpload({ projectId, onUploadSuccess, onUploadError }: FileUploadProps) {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [validationError, setValidationError] = useState<string | null>(null);
  const uploadMutation = useUploadAudio();
  const inputId = `file-input-${projectId}`;

  const isAudioFile = (file: File) => {
    if (file.type.startsWith('audio/')) return true;
    const ext = file.name.split('.').pop()?.toLowerCase();
    return ext ? ALLOWED_EXTENSIONS.includes(ext) : false;
  };

  const handleUpload = useCallback(
    (file: File) => {
      setValidationError(null);

      if (!isAudioFile(file)) {
        const err = `Invalid file format: ${file.name}. Supported formats: MP3, WAV, M4A, AAC, OGG, FLAC, MP4.`;
        setValidationError(err);
        onUploadError?.(err);
        return;
      }

      uploadMutation.mutate(
        {
          projectId,
          file,
          onProgress: (progress) => setUploadProgress(progress),
        },
        {
          onSuccess: (response) => {
            setUploadProgress(0);
            onUploadSuccess?.(response.data.id);
          },
          onError: (error: any) => {
            setUploadProgress(0);
            const message = error?.response?.data?.detail || error?.message || 'Upload failed';
            const cleanMsg = typeof message === 'string' ? message : 'Upload failed';
            setValidationError(cleanMsg);
            onUploadError?.(cleanMsg);
          },
        }
      );
    },
    [projectId, uploadMutation, onUploadSuccess, onUploadError]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.currentTarget.files;
      if (files && files.length > 0) {
        handleUpload(files[0]);
      }
      e.target.value = '';
    },
    [handleUpload]
  );

  return (
    <div className="relative overflow-hidden rounded-2xl border-2 border-dashed p-8 text-center transition-all duration-300 border-slate-700/60 bg-slate-950/40">
      
      {uploadMutation.isPending ? (
        <div className="py-4 space-y-4">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-400">
            <svg className="h-7 w-7 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
          <div>
            <h4 className="text-base font-semibold text-slate-100">Uploading Audio File...</h4>
            <p className="text-xs text-slate-400 mt-1">{Math.round(uploadProgress)}% completed</p>
          </div>
          <div className="mx-auto max-w-xs bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700">
            <div
              className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      ) : (
        <div>
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-400 border border-blue-500/20 shadow-inner">
            <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
          </div>

          <h3 className="text-lg font-semibold text-slate-100 mb-1">
            Upload Audio for Timestamping
          </h3>
          <p className="text-sm text-slate-400 max-w-sm mx-auto mb-5">
            Click the button below to browse for an audio file
          </p>

          <div className="flex flex-wrap justify-center gap-2 text-xs text-slate-400 mb-6">
            {ALLOWED_EXTENSIONS.map((ext) => (
              <span key={ext} className="rounded-full bg-slate-800/80 px-2.5 py-0.5 border border-slate-700/50 uppercase font-mono">
                .{ext}
              </span>
            ))}
            <span className="rounded-full bg-slate-800/80 px-2.5 py-0.5 border border-slate-700/50">Max 100MB</span>
          </div>

          <div className="mx-auto max-w-sm flex justify-center">
            {/* 100% Native Standard Visible Input, styled beautifully */}
            <input
              id={inputId}
              type="file"
              accept="audio/*"
              onChange={handleFileSelect}
              className="block w-full cursor-pointer text-sm text-slate-400
                file:mr-4 file:py-2.5 file:px-6
                file:rounded-xl file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-600 file:text-white
                file:shadow-lg file:shadow-blue-500/20
                hover:file:bg-blue-500 hover:file:cursor-pointer
                focus:outline-none"
            />
          </div>
        </div>
      )}

      {(validationError || uploadMutation.isError) && (
        <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-left">
          <p className="text-xs font-medium text-red-400 flex items-center gap-2">
            <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{validationError || (uploadMutation.error as any)?.message || 'Upload failed'}</span>
          </p>
        </div>
      )}
    </div>
  );
}
