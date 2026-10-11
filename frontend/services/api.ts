/**
 * API Client for audio transcription backend
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import type {
  Project,
  AudioFile,
  Transcript,
  SearchResponse,
  TranscriptionStatus,
  PaginatedResponse,
} from '@/types';

export class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response error interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Health endpoints
  async getHealth() {
    return this.client.get('/api/v1/health');
  }

  // Project endpoints
  async listProjects(skip: number = 0, limit: number = 100, user_id?: number) {
    const params: Record<string, any> = { skip, limit };
    if (user_id) params.user_id = user_id;
    return this.client.get<Project[]>('/api/v1/projects', { params });
  }

  async getProject(projectId: number) {
    return this.client.get<Project>(`/api/v1/projects/${projectId}`);
  }

  async createProject(name: string, description?: string) {
    return this.client.post<Project>('/api/v1/projects', {
      name,
      description,
      user_id: 1, // TODO: Get from auth context
    });
  }

  async updateProject(projectId: number, name?: string, description?: string) {
    return this.client.put<Project>(`/api/v1/projects/${projectId}`, {
      name,
      description,
    });
  }

  async deleteProject(projectId: number) {
    return this.client.delete(`/api/v1/projects/${projectId}`);
  }

  // Audio file endpoints
  async uploadAudio(
    projectId: number,
    file: File,
    onProgress?: (progress: number) => void
  ) {
    const formData = new FormData();
    formData.append('file', file);

    return this.client.post<AudioFile>(
      `/api/v1/audio/upload/${projectId}`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (event) => {
          if (event.total) {
            const progress = (event.loaded / event.total) * 100;
            onProgress?.(progress);
          }
        },
      }
    );
  }

  async getAudioFile(audioFileId: number) {
    return this.client.get<AudioFile>(`/api/v1/audio/${audioFileId}`);
  }

  async getProjectAudioFiles(projectId: number, skip: number = 0, limit: number = 50) {
    return this.client.get<AudioFile[]>(`/api/v1/projects/${projectId}/audio`, {
      params: { skip, limit },
    });
  }

  async getProjectTranscript(projectId: number, audioFileId?: number | null) {
    const params: Record<string, any> = {};
    if (audioFileId) params.audio_file_id = audioFileId;
    return this.client.get(`/api/v1/projects/${projectId}/transcript`, { params });
  }

  getAudioUrl(storedFilename: string) {
    return `${this.baseURL}/uploads/audio/${encodeURIComponent(storedFilename)}`;
  }

  async preprocessAudio(audioFileId: number) {
    return this.client.post(`/api/v1/audio/${audioFileId}/preprocess`);
  }

  // Transcription endpoints
  async startTranscription(audioFileId: number, language?: string) {
    const params: Record<string, any> = {};
    if (language) params.language = language;
    return this.client.post(`/api/v1/transcripts/audio/${audioFileId}/transcribe`, null, {
      params,
    });
  }

  async getTranscript(transcriptId: number) {
    return this.client.get<Transcript>(`/api/v1/transcripts/${transcriptId}`);
  }

  async getTranscriptSentences(transcriptId: number) {
    return this.client.get(`/api/v1/transcripts/${transcriptId}/sentences`);
  }

  async getTranscriptWords(transcriptId: number) {
    return this.client.get(`/api/v1/transcripts/${transcriptId}/words`);
  }

  async searchTranscript(transcriptId: number, query: string, caseSensitive: boolean = false) {
    return this.client.post<SearchResponse>(
      `/api/v1/transcripts/${transcriptId}/search`,
      null,
      {
        params: {
          query,
          case_sensitive: caseSensitive,
        },
      }
    );
  }

  async exportTranscript(transcriptId: number, format: 'txt' | 'json' | 'csv' | 'srt' | 'vtt') {
    return this.client.post(
      `/api/v1/transcripts/${transcriptId}/export/${format}`,
      null
    );
  }

  async transcribeAudio(audioFileId: number, language?: string) {
    return this.startTranscription(audioFileId, language);
  }

  async getTranscriptionStatus(audioFileId: number) {
    return this.client.get<TranscriptionStatus>(
      `/api/v1/transcripts/transcription-status/${audioFileId}`
    );
  }

  async deleteTranscript(transcriptId: number) {
    return this.client.delete(`/api/v1/transcripts/${transcriptId}`);
  }

  // Utility methods
  async downloadExport(exportId: number) {
    return this.client.get(`/api/v1/exports/${exportId}/download`, {
      responseType: 'blob',
    });
  }

  setAuthToken(token: string) {
    localStorage.setItem('auth_token', token);
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  clearAuthToken() {
    localStorage.removeItem('auth_token');
    delete this.client.defaults.headers.common['Authorization'];
  }

  getBaseURL() {
    return this.baseURL;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
