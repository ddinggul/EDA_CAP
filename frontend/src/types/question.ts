// frontend/src/types/question.ts

export interface Question {
  id: string;
  part: number; // 2 or 3
  questionNumber: number;
  type: string;
  title: string;
  question: string;
  preparationTime: number; // seconds
  responseTime: number; // seconds
  sampleResponse?: string;
  tips?: string[];

  // For integrated tasks (Part 3)
  reading?: string;
  readingTime?: number; // seconds for reading passage
  conversation?: string;
  lecture?: string;
  audioFile?: string;
}

export interface ExamSession {
  questionId: string;
  question: Question;
  startTime: Date;
  audioBlob?: Blob;
  audioUrl?: string;
  evaluation?: EvaluationResult;
}

export interface EvaluationResult {
  pronunciation: {
    score: number;
    score_4point: number;
  };
  fluency: {
    score: number;
    score_4point: number;
  };
  content?: {
    score: number;
    feedback: string;
  };
  grammar?: {
    score: number;
    feedback: string;
  };
  overall: {
    score: number;
    feedback: string;
  };
}
