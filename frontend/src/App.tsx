// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';
import ExamSelectionPage from './pages/ExamSelectionPage';
import ExamPage from './pages/ExamPage';
import ResultsPage from './pages/ResultsPage';

const App: React.FC = () => {
  return (
    <Router>
      <div style={styles.app}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/exam-selection" element={<ExamSelectionPage />} />
          <Route path="/exam/:questionId" element={<ExamPage />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
      </div>
    </Router>
  );
};

import { theme } from './theme';

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: theme.background.tertiary,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
};

export default App;
