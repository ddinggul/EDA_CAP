// frontend/src/components/AudioRecorder.tsx
import React, { useState, useRef } from 'react';
import { theme } from '../theme';

interface AudioRecorderProps {
  onRecordingComplete: (blob: Blob) => void;
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({ onRecordingComplete }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        onRecordingComplete(blob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('마이크에 접근할 수 없습니다. 권한을 확인해주세요.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div style={styles.container}>
      <h4 style={styles.title}>답변 녹음하기</h4>
      <div style={styles.recorderBox}>
        {isRecording && (
          <div style={styles.timer}>
            <span style={styles.recordingDot}></span>
            {formatTime(recordingTime)}
          </div>
        )}
        <button
          onClick={isRecording ? stopRecording : startRecording}
          style={{
            ...styles.button,
            ...(isRecording ? styles.stopButton : styles.startButton),
          }}
        >
          {isRecording ? '녹음 중지' : '녹음 시작'}
        </button>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    marginBottom: '20px',
  },
  title: {
    fontSize: '16px',
    fontWeight: '600',
    marginBottom: '10px',
    color: theme.text.primary,
  },
  recorderBox: {
    padding: '30px',
    border: `2px dashed ${theme.border.medium}`,
    borderRadius: '8px',
    textAlign: 'center',
    backgroundColor: theme.background.secondary,
  },
  timer: {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '15px',
    color: theme.error,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
  },
  recordingDot: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    backgroundColor: theme.error,
    animation: 'pulse 1.5s infinite',
  },
  button: {
    padding: '12px 30px',
    fontSize: '16px',
    fontWeight: '600',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  startButton: {
    backgroundColor: theme.accent,
    color: theme.text.white,
  },
  stopButton: {
    backgroundColor: theme.error,
    color: theme.text.white,
  },
};

export default AudioRecorder;
