// frontend/src/pages/ExamPage.tsx
import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Question } from '../types/question';
import { theme, gradients, shadows } from '../theme';
import { API_BASE_URL } from '../config';

type ExamPhase = 'loading' | 'instructions' | 'reading' | 'listening' | 'preparation' | 'recording' | 'completed';

export default function ExamPage() {
  const { questionId } = useParams<{ questionId: string }>();
  const navigate = useNavigate();

  const [question, setQuestion] = useState<Question | null>(null);
  const [phase, setPhase] = useState<ExamPhase>('loading');
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string>('');

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    fetchQuestion();
  }, [questionId]);

  useEffect(() => {
    if (timeRemaining > 0) {
      timerRef.current = setTimeout(() => {
        setTimeRemaining(timeRemaining - 1);
      }, 1000);
    } else if (timeRemaining === 0 && phase === 'reading') {
      // Auto-transition to listening or preparation after reading time expires
      handleAfterReading();
    } else if (timeRemaining === 0 && phase === 'preparation') {
      startRecording();
    } else if (timeRemaining === 0 && phase === 'recording') {
      stopRecording();
    }

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [timeRemaining, phase]);

  const fetchQuestion = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/questions/${questionId}`);
      const data = await response.json();
      setQuestion(data);
      setPhase('instructions');
    } catch (error) {
      console.error('Failed to fetch question:', error);
      alert('Failed to load question');
      navigate('/exam-selection');
    }
  };

  const startInstructions = () => {
    if (!question) return;
    if (question.reading) {
      setPhase('reading');
      setTimeRemaining(question.readingTime || 45);
    } else if (question.audioFile) {
      setPhase('listening');
    } else {
      startPreparation();
    }
  };

  const handleAfterReading = () => {
    if (!question) return;
    if (question.audioFile) {
      setPhase('listening');
      // Auto-play audio after a short delay
      setTimeout(() => {
        if (audioRef.current) {
          audioRef.current.play().catch(err => {
            console.error('Failed to auto-play audio:', err);
          });
        }
      }, 500);
    } else {
      startPreparation();
    }
  };

  const handleAudioEnded = () => {
    // Auto-start preparation when audio ends
    startPreparation();
  };

  const startPreparation = () => {
    if (!question) return;
    setPhase('preparation');
    setTimeRemaining(question.preparationTime);
  };

  const startRecording = async () => {
    if (!question) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        setAudioUrl(URL.createObjectURL(audioBlob));
        setPhase('completed');
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setPhase('recording');
      setTimeRemaining(question.responseTime);
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Failed to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const submitResponse = async () => {
    if (!audioBlob || !question) return;
    const formData = new FormData();
    formData.append('file', audioBlob, 'response.wav');

    try {
      const response = await fetch(`${API_BASE_URL}/speech/evaluate`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', errorData);
        throw new Error(errorData.detail || 'Failed to evaluate response');
      }

      const result = await response.json();
      console.log('Evaluation result:', result);
      navigate('/results', { state: { question, result, audioUrl } });
    } catch (error) {
      console.error('Failed to submit response:', error);
      alert('답변 평가에 실패했습니다. 다시 시도해주세요.\n\n오류: ' + (error instanceof Error ? error.message : String(error)));
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getPhaseStyle = (currentPhase: ExamPhase): React.CSSProperties => {
    switch (currentPhase) {
      case 'reading': return { backgroundColor: '#dbeafe', color: '#1e40af' };
      case 'listening': return { backgroundColor: '#e9d5ff', color: '#7c3aed' };
      case 'preparation': return { backgroundColor: '#fef3c7', color: '#92400e' };
      case 'recording': return { backgroundColor: '#fee2e2', color: '#991b1b' };
      default: return { backgroundColor: '#f3f4f6', color: '#374151' };
    }
  };

  if (phase === 'loading' || !question) {
    return (
      <div style={styles.loadingContainer}>
        <div style={{ textAlign: 'center' }}>
          <div style={styles.spinner}></div>
          <p style={{ marginTop: '16px', color: theme.text.secondary }}>Loading question...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.maxWidth}>
        <div style={styles.header}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h1 style={styles.title}>{question.type}</h1>
            <span style={{ ...styles.phaseBadge, ...getPhaseStyle(phase) }}>
              {phase.charAt(0).toUpperCase() + phase.slice(1)}
            </span>
          </div>
          <h2 style={styles.subtitle}>{question.title}</h2>
        </div>

        {phase === 'instructions' && (
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>Instructions</h3>
            <div style={{ marginBottom: '16px' }}>
              <p style={styles.text}>You will be asked to speak about the following topic:</p>
              <div style={styles.questionBox}>
                <p style={{ fontWeight: '500', color: theme.text.primary }}>{question.question}</p>
              </div>
              {question.reading && (
                <p style={styles.smallText}>
                  You will have {question.readingTime || 45} seconds to read a passage, then {question.preparationTime} seconds to prepare your response.
                </p>
              )}
              {!question.reading && (
                <p style={styles.smallText}>
                  You will have {question.preparationTime} seconds to prepare your response.
                </p>
              )}
              <p style={styles.smallText}>
                After preparation, you will have {question.responseTime} seconds to record your response.
              </p>
              {question.tips && (
                <div style={{ marginTop: '24px' }}>
                  <h4 style={{ fontWeight: '600', color: theme.text.primary, marginBottom: '8px' }}>Tips:</h4>
                  <ul style={{ paddingLeft: '20px', color: theme.text.secondary, fontSize: '14px', lineHeight: '1.6' }}>
                    {question.tips.map((tip, index) => (
                      <li key={index}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <button onClick={startInstructions} style={styles.primaryButton}>
              Begin
            </button>
          </div>
        )}

        {phase === 'reading' && question.reading && (
          <div style={styles.card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h3 style={styles.cardTitle}>Reading Time</h3>
              <div style={styles.timer}>{formatTime(timeRemaining)}</div>
            </div>
            <div style={styles.readingBox}>
              <pre style={styles.readingText}>{question.reading}</pre>
            </div>
            <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '14px', color: theme.text.secondary }}>
              <p>Reading will automatically advance when timer reaches 0</p>
            </div>
          </div>
        )}

        {/* Listening Phase */}
        {phase === 'listening' && question.audioFile && (
          <div style={styles.card}>
            <div style={{ textAlign: 'center' }}>
              <h3 style={{ ...styles.cardTitle, marginBottom: '24px' }}>
                🎧 Listen to the {question.conversation ? 'Conversation' : 'Lecture'}
              </h3>

              <div style={{ backgroundColor: '#f3e8ff', padding: '32px', borderRadius: '12px', marginBottom: '24px' }}>
                <p style={{ color: theme.text.secondary, marginBottom: '16px', fontSize: '14px' }}>
                  {question.conversation ?
                    'You will now hear a conversation between two students. Listen carefully.' :
                    'You will now hear a lecture. Listen carefully and take notes if needed.'}
                </p>
                <audio
                  ref={audioRef}
                  controls
                  style={{ width: '100%', marginTop: '16px' }}
                  src={`${API_BASE_URL}${question.audioFile}`}
                  onEnded={handleAudioEnded}
                >
                  Your browser does not support the audio element.
                </audio>
                <p style={{ color: theme.text.secondary, marginTop: '16px', fontSize: '13px', fontStyle: 'italic' }}>
                  Audio will play automatically. Preparation will start when audio ends.
                </p>
              </div>
            </div>
          </div>
        )}

        {phase === 'preparation' && (
          <div style={styles.card}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: '24px' }}>
                <div style={{ ...styles.bigTimer, color: '#d97706' }}>{formatTime(timeRemaining)}</div>
                <p style={styles.text}>Preparation Time Remaining</p>
              </div>
              {/* Show question for all parts */}
              <div style={styles.questionBox}>
                <p style={{ fontWeight: '500', color: theme.text.primary }}>{question.question}</p>
              </div>
              <div style={styles.infoBox}>
                <p style={{ fontSize: '14px', color: theme.text.primary }}>
                  Prepare your thoughts. Recording will start automatically when time expires.
                </p>
              </div>
            </div>
          </div>
        )}

        {phase === 'recording' && (
          <div style={styles.card}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
                  <div style={styles.recordingDot}></div>
                  <span style={{ fontSize: '20px', fontWeight: '600', color: '#dc2626', marginLeft: '12px' }}>RECORDING</span>
                </div>
                <div style={{ ...styles.bigTimer, color: '#dc2626' }}>{formatTime(timeRemaining)}</div>
                <p style={styles.text}>Response Time Remaining</p>
              </div>
              <div style={styles.questionBox}>
                <p style={{ fontWeight: '500', color: theme.text.primary }}>{question.question}</p>
              </div>
              <button onClick={stopRecording} style={styles.stopButton}>
                Stop Recording Early
              </button>
            </div>
          </div>
        )}

        {phase === 'completed' && (
          <div style={styles.card}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: '24px' }}>
                <div style={{ fontSize: '64px', marginBottom: '16px' }}>✅</div>
                <h3 style={{ ...styles.cardTitle, marginBottom: '8px' }}>Recording Completed!</h3>
                <p style={styles.text}>Review your response before submitting for evaluation.</p>
              </div>
              {audioUrl && (
                <div style={{ ...styles.infoBox, marginBottom: '24px' }}>
                  <p style={{ fontSize: '14px', fontWeight: '600', color: theme.text.primary, marginBottom: '12px' }}>Your Response:</p>
                  <audio controls style={{ width: '100%' }} src={audioUrl}></audio>
                </div>
              )}
              <div style={{ display: 'flex', gap: '16px' }}>
                <button onClick={() => navigate('/exam-selection')} style={styles.secondaryButton}>
                  Discard & Try Another
                </button>
                <button onClick={submitResponse} style={styles.primaryButton}>
                  Submit for Evaluation
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
    backgroundColor: theme.background.tertiary,
    padding: '40px 20px',
  },
  maxWidth: {
    maxWidth: '900px',
    margin: '0 auto',
  },
  loadingContainer: {
    minHeight: '100vh',
    backgroundColor: theme.background.tertiary,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  spinner: {
    width: '48px',
    height: '48px',
    border: `4px solid ${theme.border.light}`,
    borderTopColor: theme.accent,
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: '0 auto',
  },
  header: {
    backgroundColor: theme.background.primary,
    borderRadius: '12px',
    boxShadow: shadows.medium,
    padding: '24px',
    marginBottom: '24px',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: theme.text.primary,
  },
  subtitle: {
    fontSize: '18px',
    color: theme.text.secondary,
  },
  phaseBadge: {
    padding: '8px 16px',
    borderRadius: '20px',
    fontSize: '14px',
    fontWeight: '600',
  },
  card: {
    backgroundColor: theme.background.primary,
    borderRadius: '12px',
    boxShadow: shadows.medium,
    padding: '32px',
  },
  cardTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: theme.text.primary,
  },
  text: {
    color: theme.text.primary,
    marginBottom: '16px',
  },
  smallText: {
    fontSize: '14px',
    color: theme.text.secondary,
    marginTop: '8px',
  },
  questionBox: {
    backgroundColor: '#dbeafe',
    borderLeft: `4px solid ${theme.accent}`,
    padding: '16px',
    borderRadius: '8px',
    margin: '16px 0',
  },
  readingBox: {
    backgroundColor: theme.background.secondary,
    padding: '24px',
    borderRadius: '8px',
    border: `2px solid ${theme.border.light}`,
  },
  readingText: {
    whiteSpace: 'pre-wrap',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    color: theme.text.primary,
    lineHeight: '1.6',
    margin: 0,
  },
  infoBox: {
    backgroundColor: '#fef3c7',
    padding: '16px',
    borderRadius: '8px',
    marginTop: '16px',
  },
  timer: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: theme.accent,
  },
  bigTimer: {
    fontSize: '64px',
    fontWeight: 'bold',
    marginBottom: '8px',
  },
  recordingDot: {
    width: '16px',
    height: '16px',
    backgroundColor: '#dc2626',
    borderRadius: '50%',
    animation: 'pulse 1s infinite',
  },
  primaryButton: {
    width: '100%',
    background: gradients.primary,
    color: theme.text.white,
    fontWeight: '600',
    padding: '12px 24px',
    borderRadius: '8px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    boxShadow: shadows.colored,
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: theme.background.secondary,
    color: theme.text.primary,
    fontWeight: '600',
    padding: '12px 24px',
    borderRadius: '8px',
    border: `2px solid ${theme.border.light}`,
    cursor: 'pointer',
    fontSize: '16px',
  },
  stopButton: {
    backgroundColor: '#dc2626',
    color: theme.text.white,
    fontWeight: '600',
    padding: '12px 32px',
    borderRadius: '8px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    marginTop: '16px',
  },
};
