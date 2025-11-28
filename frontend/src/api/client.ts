// frontend/src/api/client.ts
import axios from 'axios';
import { SpeechAnalyzeResponse } from '../types/api';
import { API_BASE_URL } from '../config';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for audio processing
});

export const analyzeSpeech = async (
  file: File,
  taskId: number
): Promise<SpeechAnalyzeResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('task_id', taskId.toString());

  const response = await apiClient.post<SpeechAnalyzeResponse>(
    '/api/speech/analyze',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data;
};

export const checkHealth = async (): Promise<{ status: string }> => {
  const response = await apiClient.get('/health');
  return response.data;
};
