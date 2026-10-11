'use client';

/**
 * Enhanced WaveSurfer Audio Player with speed controls, timeline seek, and word synchronization
 */

import React, { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';

interface AudioPlayerProps {
  audioUrl: string;
  onTimeUpdate?: (currentTime: number) => void;
  onReady?: (duration: number) => void;
  highlightWord?: { startTime: number; endTime: number } | null;
}

export function AudioPlayer({
  audioUrl,
  onTimeUpdate,
  onReady,
  highlightWord,
}: AudioPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const waveSurferRef = useRef<WaveSurfer | null>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [volume, setVolume] = useState(1.0);
  const [isMuted, setIsMuted] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    setLoadError(null);

    try {
      const ws = WaveSurfer.create({
        container: containerRef.current,
        waveColor: '#334155',
        progressColor: '#3b82f6',
        cursorColor: '#60a5fa',
        cursorWidth: 2,
        barWidth: 2,
        barGap: 3,
        barRadius: 2,
        height: 80,
        normalize: true,
      });

      waveSurferRef.current = ws;

      ws.load(audioUrl);

      ws.on('ready', () => {
        const dur = ws.getDuration() || 0;
        setDuration(dur);
        onReady?.(dur);
      });

      ws.on('timeupdate', (time) => {
        setCurrentTime(time);
        onTimeUpdate?.(time);
      });

      ws.on('play', () => setIsPlaying(true));
      ws.on('pause', () => setIsPlaying(false));

      ws.on('error', (err) => {
        console.error('WaveSurfer error:', err);
        setLoadError('Failed to load audio stream. Please check file path or server.');
      });

      return () => {
        ws.destroy();
      };
    } catch (err: any) {
      setLoadError('Audio player initialization error.');
    }
  }, [audioUrl, onTimeUpdate, onReady]);

  // Handle Playback speed changes
  const changeSpeed = (speed: number) => {
    setPlaybackSpeed(speed);
    if (waveSurferRef.current) {
      waveSurferRef.current.setPlaybackRate(speed);
    }
  };

  // Handle Volume changes
  const handleVolumeChange = (newVol: number) => {
    setVolume(newVol);
    setIsMuted(newVol === 0);
    if (waveSurferRef.current) {
      waveSurferRef.current.setVolume(newVol);
    }
  };

  const toggleMute = () => {
    if (isMuted) {
      handleVolumeChange(volume || 1.0);
    } else {
      if (waveSurferRef.current) waveSurferRef.current.setVolume(0);
      setIsMuted(true);
    }
  };

  const togglePlayPause = () => {
    waveSurferRef.current?.playPause();
  };

  const skipSeconds = (seconds: number) => {
    if (!waveSurferRef.current || duration === 0) return;
    const target = Math.max(0, Math.min(duration, currentTime + seconds));
    waveSurferRef.current.seekTo(target / duration);
  };

  const formatTime = (seconds: number) => {
    if (isNaN(seconds) || seconds < 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Jump to word time when selected
  useEffect(() => {
    if (highlightWord && waveSurferRef.current && duration > 0) {
      const targetRatio = highlightWord.startTime / duration;
      if (targetRatio >= 0 && targetRatio <= 1) {
        waveSurferRef.current.seekTo(targetRatio);
        waveSurferRef.current.play();
      }
    }
  }, [highlightWord, duration]);

  return (
    <div className="rounded-2xl border border-slate-700/60 bg-slate-900/80 p-5 shadow-xl backdrop-blur-md">
      {loadError ? (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-xs font-medium text-amber-300">
          ⚠️ {loadError}
        </div>
      ) : (
        <>
          {/* Waveform Visualization Container */}
          <div className="relative mb-4 rounded-xl border border-slate-800 bg-slate-950/60 p-3 shadow-inner">
            <div ref={containerRef} />
            <div className="mt-1 flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span className="text-blue-400 font-semibold">{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>

          {/* Player Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            {/* Left Playback Controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => skipSeconds(-5)}
                className="rounded-xl border border-slate-700/60 bg-slate-800/60 p-2 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
                title="Rewind 5 seconds"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.334 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
                </svg>
              </button>

              <button
                onClick={togglePlayPause}
                className="flex items-center justify-center h-11 w-11 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20 hover:from-blue-500 hover:to-indigo-500 active:scale-95 transition-all"
              >
                {isPlaying ? (
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0V10a1 1 0 112 0v4zm4 0a1 1 0 11-2 0V10a1 1 0 112 0v4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="h-5 w-5 ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v8a1 1 0 001.555.832l6-4a1 1 0 000-1.664l-6-4z" clipRule="evenodd" />
                  </svg>
                )}
              </button>

              <button
                onClick={() => skipSeconds(5)}
                className="rounded-xl border border-slate-700/60 bg-slate-800/60 p-2 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
                title="Forward 5 seconds"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.934 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.334-4zM19.934 12.8a1 1 0 000-1.6l-5.334-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.334-4z" />
                </svg>
              </button>
            </div>

            {/* Right Speed & Volume Controls */}
            <div className="flex items-center gap-3">
              {/* Playback Speed Selector */}
              <div className="flex items-center rounded-xl bg-slate-950 p-1 border border-slate-800">
                {[0.75, 1.0, 1.25, 1.5].map((speed) => (
                  <button
                    key={speed}
                    onClick={() => changeSpeed(speed)}
                    className={`px-2 py-1 rounded-lg text-xs font-mono font-medium transition-all ${
                      playbackSpeed === speed
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {speed}x
                  </button>
                ))}
              </div>

              {/* Volume Slider */}
              <div className="flex items-center gap-2">
                <button
                  onClick={toggleMute}
                  className="text-slate-400 hover:text-slate-200"
                >
                  {isMuted || volume === 0 ? (
                    <svg className="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                    </svg>
                  ) : (
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                    </svg>
                  )}
                </button>
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.05}
                  value={isMuted ? 0 : volume}
                  onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                  className="w-16 h-1.5 bg-slate-800 accent-blue-500 rounded-lg cursor-pointer"
                />
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
