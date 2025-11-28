// frontend/src/pages/ExamSelectionPage.tsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Question } from '../types/question';
import { theme, gradients, shadows } from '../theme';
import { API_BASE_URL } from '../config';

export default function ExamSelectionPage() {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPart, setSelectedPart] = useState<number | 'all'>('all');
  const [selectedQuestionNumber, setSelectedQuestionNumber] = useState<number | 'all'>('all');

  useEffect(() => {
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/questions/`);
      const data = await response.json();
      setQuestions(data.questions || []);
    } catch (error) {
      console.error('Failed to fetch questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredQuestions = questions.filter(q => {
    const partMatch = selectedPart === 'all' || q.part === selectedPart;
    const questionMatch = selectedQuestionNumber === 'all' || q.questionNumber === selectedQuestionNumber;
    return partMatch && questionMatch;
  });

  // Part별로 문제 번호 추출
  const getQuestionNumbers = () => {
    const numbers = new Set<number>();
    questions.forEach(q => {
      if (selectedPart === 'all' || q.part === selectedPart) {
        numbers.add(q.questionNumber);
      }
    });
    return Array.from(numbers).sort((a, b) => a - b);
  };

  const startExam = (questionId: string) => {
    navigate(`/exam/${questionId}`);
  };

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.loadingContent}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading questions...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.maxWidth}>
        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>TOEFL Speaking Practice</h1>
          <p style={styles.subtitle}>Part와 문제 번호를 선택하여 연습을 시작하세요</p>
        </div>

        {/* Filters */}
        <div style={styles.filterCard}>
          <div style={styles.filterGrid}>
            <div>
              <label style={styles.label}>Part 선택</label>
              <select
                value={selectedPart}
                onChange={(e) => {
                  setSelectedPart(e.target.value === 'all' ? 'all' : Number(e.target.value));
                  setSelectedQuestionNumber('all'); // Part 변경 시 문제 번호 초기화
                }}
                style={styles.select}
              >
                <option value="all">전체 Part</option>
                <option value="2">Part 2 (Independent Speaking)</option>
                <option value="3">Part 3 (Integrated Speaking)</option>
              </select>
            </div>

            <div>
              <label style={styles.label}>문제 번호</label>
              <select
                value={selectedQuestionNumber}
                onChange={(e) => setSelectedQuestionNumber(e.target.value === 'all' ? 'all' : Number(e.target.value))}
                style={styles.select}
              >
                <option value="all">전체 문제</option>
                {getQuestionNumbers().map(num => (
                  <option key={num} value={num}>문제 {num}번</option>
                ))}
              </select>
            </div>
          </div>

          <div style={styles.filterInfo}>
            {filteredQuestions.length}개 문제 표시 중 (전체 {questions.length}개)
          </div>
        </div>

        {/* Questions Grid */}
        <div style={styles.grid}>
          {filteredQuestions.map((question) => (
            <div key={question.id} style={styles.card}>
              <div style={styles.cardContent}>
                {/* Part & Question Number */}
                <div style={styles.badgeContainer}>
                  <span style={styles.partBadge}>
                    Part {question.part}
                  </span>
                  <span style={styles.questionBadge}>
                    문제 {question.questionNumber}번
                  </span>
                </div>

                {/* Type Badge */}
                <div style={{ marginBottom: '12px' }}>
                  <span style={question.part === 2 ? styles.independentBadge : styles.integratedBadge}>
                    {question.type}
                  </span>
                </div>

                {/* Title */}
                <h3 style={styles.cardTitle}>{question.title}</h3>

                {/* Question Preview */}
                <p style={styles.questionText}>
                  {question.question.substring(0, 120)}...
                </p>

                {/* Time Info */}
                <div style={styles.timeInfo}>
                  <div style={styles.timeItem}>
                    <span style={styles.timeIcon}>⏱️</span>
                    <span>준비: {question.preparationTime}초</span>
                  </div>
                  <div style={styles.timeItem}>
                    <span style={styles.timeIcon}>🎤</span>
                    <span>응답: {question.responseTime}초</span>
                  </div>
                </div>

                {/* Start Button */}
                <button
                  onClick={() => startExam(question.id)}
                  style={styles.startButton}
                >
                  시작하기
                </button>
              </div>
            </div>
          ))}
        </div>

        {filteredQuestions.length === 0 && (
          <div style={styles.noResults}>
            <p style={styles.noResultsText}>선택한 조건에 맞는 문제가 없습니다.</p>
            <p style={{ color: theme.text.secondary, fontSize: '14px', marginTop: '8px' }}>
              다른 필터를 선택하거나 새로운 문제를 추가하세요.
            </p>
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
    maxWidth: '1200px',
    margin: '0 auto',
  },
  loadingContainer: {
    minHeight: '100vh',
    backgroundColor: theme.background.tertiary,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingContent: {
    textAlign: 'center',
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
  loadingText: {
    marginTop: '16px',
    color: theme.text.secondary,
  },
  header: {
    marginBottom: '32px',
    textAlign: 'center',
  },
  title: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: theme.text.primary,
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '16px',
    color: theme.text.secondary,
  },
  filterCard: {
    backgroundColor: theme.background.primary,
    borderRadius: '12px',
    boxShadow: shadows.medium,
    padding: '24px',
    marginBottom: '24px',
  },
  filterGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '16px',
    marginBottom: '16px',
  },
  label: {
    display: 'block',
    fontSize: '14px',
    fontWeight: '500',
    color: theme.text.primary,
    marginBottom: '8px',
  },
  select: {
    width: '100%',
    padding: '10px 16px',
    border: `2px solid ${theme.border.light}`,
    borderRadius: '8px',
    fontSize: '14px',
    backgroundColor: theme.background.primary,
    color: theme.text.primary,
    cursor: 'pointer',
    outline: 'none',
  },
  filterInfo: {
    fontSize: '14px',
    color: theme.text.secondary,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '24px',
  },
  card: {
    backgroundColor: theme.background.primary,
    borderRadius: '12px',
    boxShadow: shadows.medium,
    overflow: 'hidden',
    transition: 'all 0.3s ease',
    border: `2px solid ${theme.border.light}`,
    cursor: 'pointer',
  },
  cardContent: {
    padding: '24px',
  },
  badgeContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '12px',
  },
  partBadge: {
    display: 'inline-block',
    padding: '6px 12px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#7c3aed',
    backgroundColor: '#ede9fe',
    borderRadius: '20px',
  },
  questionBadge: {
    display: 'inline-block',
    padding: '6px 12px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#059669',
    backgroundColor: '#d1fae5',
    borderRadius: '20px',
  },
  independentBadge: {
    display: 'inline-block',
    padding: '6px 12px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#1e40af',
    backgroundColor: '#dbeafe',
    borderRadius: '20px',
  },
  integratedBadge: {
    display: 'inline-block',
    padding: '6px 12px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#c026d3',
    backgroundColor: '#fae8ff',
    borderRadius: '20px',
  },
  cardTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: theme.text.primary,
    marginBottom: '12px',
  },
  questionText: {
    fontSize: '14px',
    color: theme.text.secondary,
    lineHeight: '1.5',
    marginBottom: '16px',
  },
  timeInfo: {
    display: 'flex',
    gap: '16px',
    fontSize: '14px',
    color: theme.text.secondary,
    marginBottom: '16px',
  },
  timeItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
  },
  timeIcon: {
    fontSize: '16px',
  },
  startButton: {
    width: '100%',
    background: gradients.primary,
    color: theme.text.white,
    fontWeight: '600',
    padding: '12px 16px',
    borderRadius: '8px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'all 0.2s ease',
    boxShadow: shadows.colored,
  },
  noResults: {
    textAlign: 'center',
    padding: '48px 20px',
  },
  noResultsText: {
    color: theme.text.secondary,
    fontSize: '18px',
  },
};
