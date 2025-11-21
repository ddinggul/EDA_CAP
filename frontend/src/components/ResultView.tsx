// frontend/src/components/ResultView.tsx
import React from 'react';
import { SpeechAnalyzeResponse } from '../types/api';
import { theme, shadows } from '../theme';

interface ResultViewProps {
  result: SpeechAnalyzeResponse;
  onReset: () => void;
}

const ResultView: React.FC<ResultViewProps> = ({ result, onReset }) => {
  const { stt, pronunciation, evaluation } = result;

  const renderScoreBar = (label: string, score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    let color = theme.accent;
    if (percentage >= 87.5) color = theme.success;  // 3.5+ / 4.0
    else if (percentage >= 75) color = theme.accent;  // 3.0-3.4 / 4.0
    else if (percentage >= 62.5) color = theme.warning;  // 2.5-2.9 / 4.0
    else if (percentage >= 50) color = '#FF9800';  // 2.0-2.4 / 4.0
    else color = theme.error;  // < 2.0 / 4.0

    return (
      <div style={styles.scoreBarContainer}>
        <div style={styles.scoreLabel}>
          <span>{label}</span>
          <span style={styles.scoreValue}>{score.toFixed(1)}/{maxScore.toFixed(1)}</span>
        </div>
        <div style={styles.scoreBarBg}>
          <div
            style={{
              ...styles.scoreBarFill,
              width: `${percentage}%`,
              backgroundColor: color,
            }}
          />
        </div>
      </div>
    );
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>분석 결과</h2>
        <button onClick={onReset} style={styles.resetButton}>
          새로운 분석
        </button>
      </div>

      {/* Total Score */}
      <div style={styles.totalScoreCard}>
        <div style={styles.totalScoreLabel}>총점</div>
        <div style={styles.totalScoreValue}>{evaluation.scores.total.toFixed(1)}/4.0</div>
        <div style={styles.totalScoreSubtext}>
          {evaluation.scores.total >= 3.5 ? '🌟 우수함' :
           evaluation.scores.total >= 3.0 ? '✨ 좋음' :
           evaluation.scores.total >= 2.5 ? '👍 양호' :
           evaluation.scores.total >= 2.0 ? '💪 노력 필요' : '📚 더 연습해보세요'}
        </div>
      </div>

      {/* Individual Scores */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>세부 점수</h3>
        <div style={styles.scoresGrid}>
          {renderScoreBar('유창성 (Fluency)', evaluation.scores.fluency, 4.0)}
          {renderScoreBar('발음 (Pronunciation)', evaluation.scores.pronunciation, 4.0)}
          {renderScoreBar('내용 (Content)', evaluation.scores.content, 4.0)}
          {renderScoreBar('문법 (Grammar)', evaluation.scores.grammar, 4.0)}
        </div>
      </div>

      {/* STT Text */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>음성 인식 결과</h3>
        <div style={styles.sttBox}>
          <p style={styles.sttText}>{stt.text}</p>
        </div>
      </div>

      {/* Pronunciation Metrics */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>발음 분석</h3>
        <div style={styles.pronGrid}>
          <div style={styles.pronCard}>
            <div style={styles.pronLabel}>전체 발음 점수</div>
            <div style={styles.pronValue}>{pronunciation.overall.toFixed(1)}/100</div>
          </div>
          <div style={styles.pronCard}>
            <div style={styles.pronLabel}>유창성 점수</div>
            <div style={styles.pronValue}>{pronunciation.fluency.toFixed(1)}/100</div>
          </div>
        </div>
      </div>

      {/* Feedback */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>상세 피드백</h3>
        <div style={styles.feedbackBox}>
          <p style={styles.feedbackText}>{evaluation.feedback}</p>
        </div>
      </div>

      {/* Tips */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>개선 팁</h3>
        <ul style={styles.tipsList}>
          {evaluation.tips.map((tip, index) => (
            <li key={index} style={styles.tipItem}>
              {tip}
            </li>
          ))}
        </ul>
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
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: theme.text.primary,
    margin: 0,
  },
  resetButton: {
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '600',
    backgroundColor: theme.info,
    color: theme.text.white,
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  totalScoreCard: {
    backgroundColor: theme.accent,
    color: theme.text.white,
    padding: '30px',
    borderRadius: '12px',
    textAlign: 'center',
    marginBottom: '30px',
    boxShadow: shadows.colored,
  },
  totalScoreLabel: {
    fontSize: '18px',
    fontWeight: '500',
    marginBottom: '10px',
    opacity: 0.9,
  },
  totalScoreValue: {
    fontSize: '48px',
    fontWeight: 'bold',
  },
  totalScoreSubtext: {
    fontSize: '16px',
    marginTop: '10px',
    opacity: 0.95,
    fontWeight: '500',
  },
  section: {
    marginBottom: '30px',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: '600',
    color: theme.text.primary,
    marginBottom: '15px',
    paddingBottom: '10px',
    borderBottom: `2px solid ${theme.border.light}`,
  },
  scoresGrid: {
    display: 'grid',
    gap: '15px',
  },
  scoreBarContainer: {
    marginBottom: '10px',
  },
  scoreLabel: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '5px',
    fontSize: '14px',
    fontWeight: '500',
    color: theme.text.secondary,
  },
  scoreValue: {
    fontWeight: 'bold',
    color: theme.text.primary,
  },
  scoreBarBg: {
    width: '100%',
    height: '20px',
    backgroundColor: theme.border.light,
    borderRadius: '10px',
    overflow: 'hidden',
  },
  scoreBarFill: {
    height: '100%',
    transition: 'width 0.5s ease',
    borderRadius: '10px',
  },
  sttBox: {
    backgroundColor: theme.background.secondary,
    padding: '20px',
    borderRadius: '8px',
    border: `1px solid ${theme.border.light}`,
  },
  sttText: {
    fontSize: '16px',
    lineHeight: '1.6',
    color: theme.text.primary,
    margin: '0 0 15px 0',
  },
  confidenceTag: {
    display: 'inline-block',
    padding: '5px 12px',
    backgroundColor: theme.info,
    color: theme.text.white,
    borderRadius: '12px',
    fontSize: '13px',
    fontWeight: '500',
  },
  pronGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '15px',
  },
  pronCard: {
    backgroundColor: theme.background.primary,
    padding: '20px',
    borderRadius: '8px',
    border: `2px solid ${theme.border.light}`,
    textAlign: 'center',
  },
  pronLabel: {
    fontSize: '14px',
    color: theme.text.secondary,
    marginBottom: '8px',
  },
  pronValue: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: theme.accent,
  },
  feedbackBox: {
    backgroundColor: '#fff3cd',
    padding: '20px',
    borderRadius: '8px',
    border: `1px solid ${theme.warning}`,
  },
  feedbackText: {
    fontSize: '15px',
    lineHeight: '1.6',
    color: theme.text.primary,
    margin: 0,
  },
  tipsList: {
    listStyleType: 'none',
    padding: 0,
    margin: 0,
  },
  tipItem: {
    backgroundColor: theme.accentLight,
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '10px',
    fontSize: '15px',
    color: theme.text.primary,
    borderLeft: `4px solid ${theme.accent}`,
  },
};

export default ResultView;
