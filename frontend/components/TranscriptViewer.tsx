'use client';

/**
 * Enhanced TranscriptViewer component with sentence/word timestamps, search, and exports
 */

import React, { useState, useMemo } from 'react';
import { apiClient } from '@/services/api';

interface Word {
  id: number;
  text: string;
  start_time: number;
  end_time: number;
}

interface Sentence {
  id: number;
  text: string;
  start_time: number;
  end_time: number;
  words?: Word[];
}

interface TranscriptViewerProps {
  transcript?: {
    id: number;
    text: string;
    language: string;
    sentences?: Sentence[];
    words?: Word[];
  } | null;
  isLoading?: boolean;
  onSelectTimestamp?: (startTime: number, endTime: number) => void;
}

export function TranscriptViewer({
  transcript,
  isLoading,
  onSelectTimestamp,
}: TranscriptViewerProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'sentences' | 'words' | 'raw'>('sentences');
  const [exportingFormat, setExportingFormat] = useState<string | null>(null);
  const [selectedWord, setSelectedWord] = useState<Word | null>(null);

  const formatTime = (seconds: number) => {
    if (seconds == null || isNaN(seconds)) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 100);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
  };

  // Filter sentences by search query
  const filteredSentences = useMemo(() => {
    if (!transcript?.sentences) return [];
    if (!searchQuery.trim()) return transcript.sentences;
    const q = searchQuery.toLowerCase();
    return transcript.sentences.filter((s) => s.text.toLowerCase().includes(q));
  }, [transcript?.sentences, searchQuery]);

  // Filter words by search query
  const filteredWords = useMemo(() => {
    if (!transcript?.words) return [];
    if (!searchQuery.trim()) return transcript.words;
    const q = searchQuery.toLowerCase();
    return transcript.words.filter((w) => w.text.toLowerCase().includes(q));
  }, [transcript?.words, searchQuery]);

  const handleExport = async (format: 'txt' | 'json' | 'csv' | 'srt' | 'vtt') => {
    if (!transcript?.id) return;
    setExportingFormat(format);

    try {
      const res = await apiClient.exportTranscript(transcript.id, format);
      const downloadUrl = res.data?.download_url || `/api/v1/exports/${res.data?.export_id || res.data?.id}/download`;

      // Trigger file download
      const link = document.createElement('a');
      link.href = downloadUrl.startsWith('http') ? downloadUrl : `${apiClient.getBaseURL()}${downloadUrl}`;
      link.setAttribute('download', `transcript_${transcript.id}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Export failed:', err);
      // Fallback client download if API endpoint export is pure text
      const content = transcript.text;
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `transcript_${transcript.id}.${format}`;
      link.click();
      URL.revokeObjectURL(url);
    } finally {
      setExportingFormat(null);
    }
  };

  if (isLoading) {
    return (
      <div className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-8 text-center glass-panel">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-400 mb-3">
          <svg className="h-6 w-6 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
        <p className="text-sm font-medium text-slate-300">Loading transcript data...</p>
      </div>
    );
  }

  if (!transcript || !transcript.id) {
    return (
      <div className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-8 text-center glass-panel">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-800 text-slate-400 mb-3">
          <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h4 className="text-base font-semibold text-slate-200">No Transcript Generated Yet</h4>
        <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
          Select an uploaded audio file on the left and click &quot;Transcribe Audio&quot; to generate text timestamps.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-5 rounded-2xl border border-slate-700/60 bg-slate-900/80 p-6 shadow-2xl backdrop-blur-md">
      {/* Header & Meta */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-100">Transcript</h2>
            <span className="rounded-full bg-blue-500/10 px-3 py-0.5 text-xs font-mono font-semibold text-blue-400 border border-blue-500/20 uppercase">
              {transcript.language || 'en'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Click any sentence or word timestamp to jump to audio playback
          </p>
        </div>

        {/* Export Formats Dropdown / Bar */}
        <div className="flex items-center gap-1.5 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
          <span className="px-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">Export:</span>
          {(['txt', 'json', 'csv', 'srt', 'vtt'] as const).map((fmt) => (
            <button
              key={fmt}
              onClick={() => handleExport(fmt)}
              disabled={!!exportingFormat}
              className="rounded-lg bg-slate-800/80 px-2.5 py-1 text-xs font-mono uppercase font-semibold text-slate-300 hover:bg-blue-600 hover:text-white transition-all disabled:opacity-50"
            >
              {exportingFormat === fmt ? '...' : fmt}
            </button>
          ))}
        </div>
      </div>

      {/* Toolbar: View mode tabs & Search query input */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800">
          <button
            onClick={() => setViewMode('sentences')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'sentences'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sentences ({transcript.sentences?.length || 0})
          </button>
          <button
            onClick={() => setViewMode('words')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'words'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Word Timeline ({transcript.words?.length || 0})
          </button>
          <button
            onClick={() => setViewMode('raw')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'raw'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Raw Text
          </button>
        </div>

        {/* Search input */}
        <div className="relative flex-1 max-w-xs">
          <input
            type="text"
            placeholder="Search transcript..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-slate-700/80 bg-slate-950 px-3.5 py-1.5 pl-9 text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
          />
          <svg className="absolute left-3 top-2 h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-2 text-xs text-slate-500 hover:text-slate-300"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Main View Area */}
      {viewMode === 'raw' && (
        <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-5 leading-relaxed text-slate-200 text-sm max-h-[450px] overflow-y-auto font-sans">
          {transcript.text}
        </div>
      )}

      {viewMode === 'sentences' && (
        <div className="space-y-3 max-h-[480px] overflow-y-auto pr-1">
          {filteredSentences.length > 0 ? (
            filteredSentences.map((sentence) => (
              <div
                key={sentence.id}
                onClick={() => onSelectTimestamp?.(sentence.start_time, sentence.end_time)}
                className="group relative cursor-pointer rounded-xl border border-slate-800 bg-slate-950/50 p-3.5 transition-all hover:border-blue-500/40 hover:bg-slate-900"
              >
                <div className="mb-1.5 flex items-center justify-between">
                  <span className="rounded bg-blue-500/10 px-2 py-0.5 font-mono text-[11px] font-semibold text-blue-400 border border-blue-500/20 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    {formatTime(sentence.start_time)} → {formatTime(sentence.end_time)}
                  </span>
                  <span className="text-[10px] text-slate-500 group-hover:text-slate-400">Jump to audio</span>
                </div>
                <p className="text-sm leading-relaxed text-slate-200 group-hover:text-white">
                  {sentence.text}
                </p>
              </div>
            ))
          ) : (
            <div className="py-8 text-center text-xs text-slate-400">
              No sentence timestamps found matching query &quot;{searchQuery}&quot;
            </div>
          )}
        </div>
      )}

      {viewMode === 'words' && (
        <div className="space-y-4 max-h-[480px] overflow-y-auto pr-1">
          <div className="flex flex-wrap gap-1.5">
            {filteredWords.map((word) => (
              <button
                key={word.id}
                onClick={() => {
                  setSelectedWord(word);
                  onSelectTimestamp?.(word.start_time, word.end_time);
                }}
                className={`rounded-lg border px-2.5 py-1 text-xs font-medium transition-all ${
                  selectedWord?.id === word.id
                    ? 'border-blue-500 bg-blue-600 text-white shadow-md shadow-blue-500/20'
                    : 'border-slate-800 bg-slate-950/80 text-slate-300 hover:border-blue-500/50 hover:bg-slate-900 hover:text-white'
                }`}
              >
                <span>{word.text}</span>
                <span className="ml-1.5 font-mono text-[9px] opacity-60">
                  {word.start_time.toFixed(1)}s
                </span>
              </button>
            ))}
          </div>

          {selectedWord && (
            <div className="rounded-xl border border-blue-500/30 bg-blue-500/10 p-3 text-xs text-blue-300 flex items-center justify-between">
              <div>
                Selected word: <span className="font-bold text-white">&quot;{selectedWord.text}&quot;</span>
              </div>
              <div className="font-mono text-blue-200">
                {formatTime(selectedWord.start_time)} to {formatTime(selectedWord.end_time)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
