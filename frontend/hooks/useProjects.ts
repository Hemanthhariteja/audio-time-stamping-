/**
 * React hooks for managing API data
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import type { Project, AudioFile, Transcript, PaginatedResponse } from '@/types';

// The list endpoints return plain arrays; wrap them in the paginated shape the pages consume
function toPage<T>(data: T[] | PaginatedResponse<T>, skip: number, limit: number): PaginatedResponse<T> {
  if (Array.isArray(data)) {
    return { items: data, total: data.length, skip, limit };
  }
  return data;
}

export function useProjects(skip: number = 0, limit: number = 100) {
  return useQuery({
    queryKey: ['projects', skip, limit],
    queryFn: () => apiClient.listProjects(skip, limit).then((r) => toPage(r.data, skip, limit)),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useProject(projectId: number) {
  return useQuery({
    queryKey: ['project', projectId],
    queryFn: () => apiClient.getProject(projectId).then((r) => r.data),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ name, description }: { name: string; description?: string }) =>
      apiClient.createProject(name, description).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectId,
      name,
      description,
    }: {
      projectId: number;
      name?: string;
      description?: string;
    }) => apiClient.updateProject(projectId, name, description),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (projectId: number) => apiClient.deleteProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useUploadAudio() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectId,
      file,
      onProgress,
    }: {
      projectId: number;
      file: File;
      onProgress?: (progress: number) => void;
    }) => apiClient.uploadAudio(projectId, file, onProgress),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
      queryClient.invalidateQueries({ queryKey: ['projectAudio', variables.projectId] });
    },
  });
}

export function useAudioFile(audioFileId: number) {
  return useQuery({
    queryKey: ['audioFile', audioFileId],
    queryFn: () => apiClient.getAudioFile(audioFileId).then((r) => r.data),
    staleTime: 5 * 60 * 1000,
  });
}

export function useProjectAudio(projectId: number) {
  return useQuery({
    queryKey: ['projectAudio', projectId],
    queryFn: () => apiClient.getProjectAudioFiles(projectId).then((r) => toPage(r.data, 0, 50)),
    staleTime: 5 * 60 * 1000,
    enabled: !!projectId,
  });
}

export function useProjectTranscript(projectId: number, audioFileId?: number | null) {
  return useQuery({
    queryKey: ['projectTranscript', projectId, audioFileId ?? null],
    queryFn: () => apiClient.getProjectTranscript(projectId, audioFileId).then((r) => r.data),
    staleTime: 5 * 60 * 1000,
    enabled: !!projectId,
  });
}

export function usePreprocessAudio() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (audioFileId: number) => apiClient.preprocessAudio(audioFileId),
    onSuccess: (_, audioFileId) => {
      queryClient.invalidateQueries({ queryKey: ['audioFile', audioFileId] });
    },
  });
}

export function useStartTranscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ audioFileId, language }: { audioFileId: number; language?: string }) =>
      apiClient.startTranscription(audioFileId, language),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['transcriptionStatus', variables.audioFileId],
      });
      queryClient.invalidateQueries({ queryKey: ['projectTranscript'] });
    },
  });
}

export function useTranscribeAudio() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: number | { audioFileId: number; language?: string }) => {
      const audioFileId = typeof payload === 'number' ? payload : payload.audioFileId;
      const language = typeof payload === 'number' ? undefined : payload.language;
      return apiClient.transcribeAudio(audioFileId, language);
    },
    onSuccess: (_, variables) => {
      const audioFileId = typeof variables === 'number' ? variables : variables.audioFileId;
      queryClient.invalidateQueries({ queryKey: ['transcriptionStatus', audioFileId] });
      queryClient.invalidateQueries({ queryKey: ['projectTranscript'] });
    },
  });
}

export function useTranscript(transcriptId: number) {
  return useQuery({
    queryKey: ['transcript', transcriptId],
    queryFn: () => apiClient.getTranscript(transcriptId).then((r) => r.data),
    staleTime: 5 * 60 * 1000,
  });
}

export function useTranscriptSearch(transcriptId: number, query: string) {
  return useQuery({
    queryKey: ['transcriptSearch', transcriptId, query],
    queryFn: () =>
      query
        ? apiClient.searchTranscript(transcriptId, query).then((r) => r.data)
        : Promise.resolve({ query: '', total_results: 0, results: [] }),
    staleTime: 2 * 60 * 1000,
    enabled: !!query && !!transcriptId,
  });
}

export function useExportTranscript() {
  return useMutation({
    mutationFn: ({
      transcriptId,
      format,
    }: {
      transcriptId: number;
      format: 'txt' | 'json' | 'csv' | 'srt' | 'vtt';
    }) => apiClient.exportTranscript(transcriptId, format),
  });
}

export function useTranscriptionStatus(audioFileId: number) {
  return useQuery({
    queryKey: ['transcriptionStatus', audioFileId],
    queryFn: () => apiClient.getTranscriptionStatus(audioFileId).then((r) => r.data),
    refetchInterval: 2000, // Poll every 2 seconds
    enabled: !!audioFileId,
  });
}
