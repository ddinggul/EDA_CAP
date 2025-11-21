// frontend/src/pages/AnalyzePage.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TaskSelector from '../components/TaskSelector';
import AudioRecorder from '../components/AudioRecorder';
import FileUploader from '../components/FileUploader';
import ResultView from '../components/ResultView';
import { analyzeSpeech } from '../api/client';
import { SpeechAnalyzeResponse } from '../types/api';
import { theme, gradients, shadows } from '../theme';

const AnalyzePage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedTask, setSelectedTask] = useState<number>(1);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<SpeechAnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRecordingComplete = (blob: Blob) => {
    const file = new File([blob], 'recording.webm', { type: 'audio/webm' });
    setSelectedFile(file);
  };

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      alert('먼저 음성을 녹음하거나 파일을 업로드해주세요');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const analysisResult = await analyzeSpeech(selectedFile, selectedTask);
      setResult(analysisResult);
    } catch (err: any) {
      console.error('Analysis error:', err);
      setError(
        err.response?.data?.detail ||
        err.message ||
        '음성 분석에 실패했습니다. 다시 시도해주세요.'
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setSelectedFile(null);
    setError(null);
  };

  if (result) {
    return <ResultView result={result} onReset={handleReset} />;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <button onClick={() => navigate('/')} style={styles.backButton}>
          ← 홈으로 돌아가기
        </button>
        <h1 style={styles.title}>스피킹 분석</h1>
      </div>

      <div style={styles.content}>
        <TaskSelector selectedTask={selectedTask} onTaskChange={setSelectedTask} />

        <div style={styles.inputSection}>
          <AudioRecorder onRecordingComplete={handleRecordingComplete} />
          <div style={styles.divider}>
            <span style={styles.dividerText}>또는</span>
          </div>
          <FileUploader onFileSelect={handleFileSelect} selectedFile={selectedFile} />
        </div>

        {error && (
          <div style={styles.errorBox}>
            <strong>오류:</strong> {error}
          </div>
        )}

        <div style={styles.actionSection}>
          <button
            onClick={handleAnalyze}
            disabled={!selectedFile || isAnalyzing}
            style={{
              ...styles.analyzeButton,
              ...((!selectedFile || isAnalyzing) ? styles.analyzeButtonDisabled : {}),
            }}
          >
            {isAnalyzing ? (
              <>
                <span style={styles.spinner}></span>
                분석 중...
              </>
            ) : (
              '스피킹 분석 시작'
            )}
          </button>
          {selectedFile && (
            <p style={styles.fileSelectedText}>
              선택된 파일: {selectedFile.name}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '20px',
  },
  header: {
    marginBottom: '30px',
  },
  backButton: {
    padding: '8px 16px',
    fontSize: '14px',
    backgroundColor: theme.background.secondary,
    border: `1px solid ${theme.border.medium}`,
    borderRadius: '6px',
    cursor: 'pointer',
    marginBottom: '15px',
    transition: 'all 0.3s ease',
    color: theme.text.primary,
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: theme.text.primary,
    margin: 0,
  },
  content: {
    backgroundColor: theme.background.primary,
    padding: '30px',
    borderRadius: '12px',
    boxShadow: shadows.medium,
  },
  inputSection: {
    marginBottom: '30px',
  },
  divider: {
    textAlign: 'center',
    margin: '20px 0',
    position: 'relative',
  },
  dividerText: {
    backgroundColor: theme.background.primary,
    padding: '0 15px',
    color: theme.text.light,
    fontSize: '14px',
    fontWeight: '600',
    position: 'relative',
    zIndex: 1,
  },
  errorBox: {
    padding: '15px',
    backgroundColor: '#ffebee',
    border: `1px solid ${theme.error}`,
    borderRadius: '6px',
    color: '#c62828',
    marginBottom: '20px',
  },
  actionSection: {
    textAlign: 'center',
  },
  analyzeButton: {
    padding: '16px 40px',
    fontSize: '18px',
    fontWeight: '600',
    background: gradients.primary,
    color: theme.text.white,
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: shadows.colored,
    display: 'inline-flex',
    alignItems: 'center',
    gap: '10px',
  },
  analyzeButtonDisabled: {
    background: '#cccccc',
    cursor: 'not-allowed',
    boxShadow: 'none',
  },
  spinner: {
    width: '16px',
    height: '16px',
    border: '2px solid #ffffff',
    borderTopColor: 'transparent',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  },
  fileSelectedText: {
    marginTop: '15px',
    fontSize: '14px',
    color: theme.text.secondary,
  },
};

export default AnalyzePage;
