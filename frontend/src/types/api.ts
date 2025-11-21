// frontend/src/types/api.ts

export interface STTResult {
  text: string;
  confidence: number;
}

export interface PronunciationDetails {
  segments?: Array<{
    start: number;
    end: number;
    score: number;
    word?: string;
  }>;
}

export interface PronunciationResult {
  overall: number;
  fluency: number;
  details?: PronunciationDetails;
}

export interface EvaluationScores {
  fluency: number;  // 0.0-4.0, 소수점 1자리
  pronunciation: number;  // 0.0-4.0, 소수점 1자리
  content: number;  // 0.0-4.0, 소수점 1자리
  grammar: number;  // 0.0-4.0, 소수점 1자리
  total: number;  // 0.0-4.0, 소수점 1자리 (평균)
}

export interface EvaluationResult {
  scores: EvaluationScores;
  feedback: string;
  tips: string[];
}

export interface SpeechAnalyzeResponse {
  task_id: number;
  stt: STTResult;
  pronunciation: PronunciationResult;
  evaluation: EvaluationResult;
}
