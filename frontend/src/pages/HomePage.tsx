// frontend/src/pages/HomePage.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { theme, gradients, shadows } from '../theme';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div style={styles.container}>
      <div style={styles.hero}>
        <h1 style={styles.title}>TOEFL 스피킹 AI 컨설턴트</h1>
        <p style={styles.subtitle}>
          AI 기반 실시간 TOEFL 스피킹 평가 및 피드백
        </p>
        <button
          onClick={() => navigate('/analyze')}
          style={styles.ctaButton}
        >
          스피킹 분석 시작하기
        </button>
      </div>

      <div style={styles.features}>
        <div style={styles.featureCard}>
          <div style={styles.featureIcon}>🎤</div>
          <h3 style={styles.featureTitle}>음성 인식</h3>
          <p style={styles.featureText}>
            네이버 CLOVA Speech 기술로 정확한 음성-텍스트 변환
          </p>
        </div>

        <div style={styles.featureCard}>
          <div style={styles.featureIcon}>📊</div>
          <h3 style={styles.featureTitle}>발음 평가</h3>
          <p style={styles.featureText}>
            발음, 유창성, 억양 등 다차원 발음 분석 및 평가
          </p>
        </div>

        <div style={styles.featureCard}>
          <div style={styles.featureIcon}>🤖</div>
          <h3 style={styles.featureTitle}>AI 피드백</h3>
          <p style={styles.featureText}>
            OpenAI GPT 기반 맞춤형 피드백 및 개선 팁 제공
          </p>
        </div>
      </div>

      <div style={styles.howItWorks}>
        <h2 style={styles.sectionTitle}>사용 방법</h2>
        <div style={styles.steps}>
          <div style={styles.step}>
            <div style={styles.stepNumber}>1</div>
            <div style={styles.stepText}>TOEFL Speaking Task 선택 (1-4번)</div>
          </div>
          <div style={styles.step}>
            <div style={styles.stepNumber}>2</div>
            <div style={styles.stepText}>답변 녹음 또는 음성 파일 업로드</div>
          </div>
          <div style={styles.step}>
            <div style={styles.stepNumber}>3</div>
            <div style={styles.stepText}>종합 분석 결과 및 피드백 확인</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
  },
  hero: {
    textAlign: 'center',
    padding: '60px 20px',
    background: gradients.light,
    borderRadius: '12px',
    marginBottom: '50px',
  },
  title: {
    fontSize: '48px',
    fontWeight: 'bold',
    color: theme.text.primary,
    marginBottom: '20px',
  },
  subtitle: {
    fontSize: '20px',
    color: theme.text.secondary,
    marginBottom: '30px',
    lineHeight: '1.6',
  },
  ctaButton: {
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
  },
  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '30px',
    marginBottom: '50px',
  },
  featureCard: {
    padding: '30px',
    backgroundColor: theme.background.primary,
    borderRadius: '12px',
    boxShadow: shadows.medium,
    textAlign: 'center',
    transition: 'transform 0.3s ease',
    border: `2px solid ${theme.border.light}`,
  },
  featureIcon: {
    fontSize: '48px',
    marginBottom: '15px',
  },
  featureTitle: {
    fontSize: '20px',
    fontWeight: '600',
    color: theme.accent,
    marginBottom: '10px',
  },
  featureText: {
    fontSize: '15px',
    color: theme.text.secondary,
    lineHeight: '1.6',
  },
  howItWorks: {
    padding: '40px',
    backgroundColor: theme.background.secondary,
    borderRadius: '12px',
  },
  sectionTitle: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: theme.text.primary,
    textAlign: 'center',
    marginBottom: '40px',
  },
  steps: {
    display: 'flex',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
    gap: '30px',
  },
  step: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    maxWidth: '250px',
  },
  stepNumber: {
    width: '60px',
    height: '60px',
    borderRadius: '50%',
    background: gradients.primary,
    color: theme.text.white,
    fontSize: '28px',
    fontWeight: 'bold',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '15px',
    boxShadow: shadows.colored,
  },
  stepText: {
    fontSize: '16px',
    color: theme.text.primary,
    textAlign: 'center',
    lineHeight: '1.5',
  },
};

export default HomePage;
