/**
 * TypeScript interfaces for audio transcription application
 */

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  audio_files?: AudioFile[];
  created_at: string;
  updated_at: string;
}

export interface AudioFile {
  id: number;
  project_id: number;
  original_filename: string;
  stored_filename: string;
  file_format: string;
  file_size_bytes: number;
  duration_seconds?: number;
  upload_status: 'pending' | 'uploaded' | 'preprocessing' | 'ready' | 'failed';
  processing_error?: string;
  created_at: string;
  updated_at: string;
}

export interface TranscriptWord {
  id: number;
  word_text: string;
  start_time: number;
  end_time: number;
  confidence_score?: number;
  word_index: number;
}

export interface TranscriptSentence {
  id: number;
  sentence_text: string;
  start_time: number;
  end_time: number;
  confidence_score?: number;
  sentence_index: number;
  words: TranscriptWord[];
}

export interface Transcript {
  id: number;
  audio_file_id: number;
  full_text: string;
  language_code: string;
  confidence_score?: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  sentence_count: number;
  word_count: number;
  sentences: TranscriptSentence[];
  created_at: string;
  updated_at: string;
}

export interface Export {
  id: number;
  transcript_id: number;
  export_format: 'txt' | 'json' | 'csv' | 'srt' | 'vtt';
  file_path: string;
  file_size_bytes: number;
  download_count: number;
  created_at: string;
}

export interface SearchResult {
  sentence_id: number;
  sentence_text: string;
  start_time: number;
  end_time: number;
  context?: string;
}

export interface SearchResponse {
  query: string;
  total_results: number;
  results: SearchResult[];
}

export interface TranscriptionStatus {
  audio_file_id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  transcript_id?: number;
  completed_at?: string;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface ApiErrorResponse {
  error_code: string;
  message: string;
  details?: Record<string, any>;
}

export interface PaginatedResponse<T> {
  total: number;
  skip: number;
  limit: number;
  items: T[];
}
