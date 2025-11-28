// frontend/src/pages/ResultsPage.tsx
import { useLocation, useNavigate } from 'react-router-dom';
import { Question } from '../types/question';
import { theme, gradients, shadows } from '../theme';

interface LocationState {
  question: Question;
  result: any;
  audioUrl: string;
}

export default function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { question, result, audioUrl } = (location.state as LocationState) || {};

  if (!question || !result) {
    return (
      <div style={styles.container}>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: theme.text.secondary, marginBottom: '16px' }}>평가 결과를 찾을 수 없습니다.</p>
          <button onClick={() => navigate('/exam-selection')} style={styles.primaryButton}>
            문제 선택으로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 3.5) return '#059669';
    if (score >= 2.5) return '#d97706';
    return '#dc2626';
  };

  const getScoreBackground = (score: number): React.CSSProperties => {
    if (score >= 3.5) return { backgroundColor: '#d1fae5', borderColor: '#10b981' };
    if (score >= 2.5) return { backgroundColor: '#fef3c7', borderColor: '#f59e0b' };
    return { backgroundColor: '#fee2e2', borderColor: '#ef4444' };
  };

  return (
    <div style={styles.container}>
      <div style={styles.maxWidth}>
        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>📊 평가 결과</h1>
          <p style={styles.subtitle}>{question.type} - {question.title}</p>
        </div>

        {/* Question */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>❓ 문제</h2>
          <div style={styles.questionBox}>
            <p style={{ color: theme.text.primary }}>{question.question}</p>
          </div>
        </div>

        {/* Audio */}
        {audioUrl && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>🎙️ 녹음된 답변</h2>
            <audio controls style={{ width: '100%' }} src={audioUrl}></audio>
          </div>
        )}

        {/* Scores */}
        <div style={styles.scoresGrid}>
          {result.pronunciation && (
            <div style={{ ...styles.scoreCard, ...getScoreBackground(result.pronunciation.score_4point) }}>
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>🎤</div>
              <h3 style={styles.scoreLabel}>발음 (Pronunciation)</h3>
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: getScoreColor(result.pronunciation.score_4point), marginBottom: '4px' }}>
                {result.pronunciation.score_4point.toFixed(1)}
              </div>
              <div style={{ fontSize: '14px', color: theme.text.secondary }}>out of 4.0</div>
            </div>
          )}

          {result.fluency && (
            <div style={{ ...styles.scoreCard, ...getScoreBackground(result.fluency.score_4point) }}>
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>⚡</div>
              <h3 style={styles.scoreLabel}>유창성 (Fluency)</h3>
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: getScoreColor(result.fluency.score_4point), marginBottom: '4px' }}>
                {result.fluency.score_4point.toFixed(1)}
              </div>
              <div style={{ fontSize: '14px', color: theme.text.secondary }}>out of 4.0</div>
            </div>
          )}

          {result.content && (
            <div style={{ ...styles.scoreCard, ...getScoreBackground(result.content.score) }}>
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>📝</div>
              <h3 style={styles.scoreLabel}>내용 (Content)</h3>
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: getScoreColor(result.content.score), marginBottom: '4px' }}>
                {result.content.score.toFixed(1)}
              </div>
              <div style={{ fontSize: '14px', color: theme.text.secondary }}>out of 4.0</div>
            </div>
          )}

          {result.grammar && (
            <div style={{ ...styles.scoreCard, ...getScoreBackground(result.grammar.score) }}>
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>📚</div>
              <h3 style={styles.scoreLabel}>문법 (Grammar)</h3>
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: getScoreColor(result.grammar.score), marginBottom: '4px' }}>
                {result.grammar.score.toFixed(1)}
              </div>
              <div style={{ fontSize: '14px', color: theme.text.secondary }}>out of 4.0</div>
            </div>
          )}

          {result.overall && (
            <div style={{ ...styles.scoreCard, ...getScoreBackground(result.overall.score) }}>
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>🏆</div>
              <h3 style={styles.scoreLabel}>종합 (Overall)</h3>
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: getScoreColor(result.overall.score), marginBottom: '4px' }}>
                {result.overall.score.toFixed(1)}
              </div>
              <div style={{ fontSize: '14px', color: theme.text.secondary }}>out of 4.0</div>
            </div>
          )}
        </div>

        {/* Transcript */}
        {result.speech_recognition && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>📄 전사본 (Transcript)</h2>
            <div style={styles.transcriptBox}>
              <p style={{ color: theme.text.primary, lineHeight: '1.6' }}>{result.speech_recognition.text}</p>
            </div>
            {result.speech_recognition.confidence && (
              <p style={{ marginTop: '8px', fontSize: '14px', color: theme.text.secondary }}>
                인식 정확도: {(result.speech_recognition.confidence * 100).toFixed(1)}%
              </p>
            )}
          </div>
        )}

        {/* AI Feedback */}
        {result.gpt_evaluation && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>💬 AI 평가 피드백</h2>
            <div style={styles.feedbackBox}>
              <p style={{ ...styles.feedbackText, whiteSpace: 'pre-wrap' }}>{result.gpt_evaluation}</p>
            </div>
          </div>
        )}

        {/* Tips */}
        {result.tips && result.tips.length > 0 && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>💡 개선을 위한 팁</h2>
            <div style={styles.tipsBox}>
              {result.tips.map((tip: string, index: number) => (
                <div key={index} style={styles.tipItem}>
                  <span style={styles.tipNumber}>{index + 1}</span>
                  <p style={styles.tipText}>{tip}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sample Response */}
        {question.sampleResponse && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>✨ 모범 답변 예시</h2>
            <div style={styles.sampleBox}>
              <p style={{ color: theme.text.primary, lineHeight: '1.6' }}>{question.sampleResponse}</p>
            </div>
            <p style={{ marginTop: '12px', fontSize: '14px', color: theme.text.secondary }}>
              자신의 답변과 비교하여 개선할 부분을 찾아보세요.
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div style={styles.buttonGroup}>
          <button onClick={() => navigate('/exam-selection')} style={styles.secondaryButton}>
            다른 문제 풀기
          </button>
          <button onClick={() => navigate(`/exam/${question.id}`)} style={styles.primaryButton}>
            이 문제 다시 풀기
          </button>
        </div>
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
    maxWidth: '1000px',
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
    fontSize: '32px',
    fontWeight: 'bold',
    color: theme.text.primary,
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '16px',
    color: theme.text.secondary,
  },
  card: {
    backgroundColor: theme.background.primary,
    borderRadius: '12px',
    boxShadow: shadows.medium,
    padding: '24px',
    marginBottom: '24px',
  },
  cardTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: theme.text.primary,
    marginBottom: '16px',
  },
  questionBox: {
    backgroundColor: '#dbeafe',
    borderLeft: `4px solid ${theme.accent}`,
    padding: '16px',
    borderRadius: '8px',
  },
  scoresGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '24px',
    marginBottom: '24px',
  },
  scoreCard: {
    borderRadius: '12px',
    boxShadow: shadows.medium,
    padding: '24px',
    textAlign: 'center',
    border: '2px solid',
  },
  scoreLabel: {
    fontSize: '16px',
    fontWeight: '600',
    color: theme.text.secondary,
    marginBottom: '8px',
  },
  transcriptBox: {
    backgroundColor: theme.background.secondary,
    padding: '16px',
    borderRadius: '8px',
    border: `2px solid ${theme.border.light}`,
  },
  feedbackBox: {
    backgroundColor: '#dbeafe',
    padding: '16px',
    borderRadius: '8px',
    border: '2px solid #93c5fd',
  },
  feedbackText: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    color: theme.text.primary,
    lineHeight: '1.8',
    margin: 0,
    fontSize: '15px',
  },
  tipsBox: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
  },
  tipItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    padding: '12px',
    backgroundColor: '#fef3c7',
    borderRadius: '8px',
    border: '1px solid #fbbf24',
  },
  tipNumber: {
    backgroundColor: '#f59e0b',
    color: theme.text.white,
    borderRadius: '50%',
    width: '24px',
    height: '24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
    fontSize: '14px',
    flexShrink: 0,
  },
  tipText: {
    color: theme.text.primary,
    lineHeight: '1.6',
    margin: 0,
    fontSize: '14px',
  },
  sampleBox: {
    backgroundColor: '#d1fae5',
    padding: '16px',
    borderRadius: '8px',
    border: '2px solid #6ee7b7',
  },
  buttonGroup: {
    display: 'flex',
    gap: '16px',
  },
  primaryButton: {
    flex: 1,
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
};
