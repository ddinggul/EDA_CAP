// frontend/src/components/TaskSelector.tsx
import React from 'react';
import { theme, shadows } from '../theme';

interface TaskSelectorProps {
  selectedTask: number;
  onTaskChange: (taskId: number) => void;
}

const TASKS = [
  { id: 1, title: 'Task 1', description: '독립형 과제: 개인 선호도' },
  { id: 2, title: 'Task 2', description: '독립형 과제: 선택' },
  { id: 3, title: 'Task 3', description: '통합형 과제: 캠퍼스 상황' },
  { id: 4, title: 'Task 4', description: '통합형 과제: 학술 강의' },
];

const TaskSelector: React.FC<TaskSelectorProps> = ({ selectedTask, onTaskChange }) => {
  return (
    <div style={styles.container}>
      <h3 style={styles.title}>TOEFL Speaking Task 선택</h3>
      <div style={styles.taskGrid}>
        {TASKS.map((task) => (
          <div
            key={task.id}
            style={{
              ...styles.taskCard,
              ...(selectedTask === task.id ? styles.taskCardSelected : {}),
            }}
            onClick={() => onTaskChange(task.id)}
          >
            <div style={styles.taskNumber}>{task.title}</div>
            <div style={styles.taskDescription}>{task.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    marginBottom: '30px',
  },
  title: {
    fontSize: '18px',
    fontWeight: '600',
    marginBottom: '15px',
    color: theme.text.primary,
  },
  taskGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '15px',
  },
  taskCard: {
    padding: '20px',
    border: `2px solid ${theme.border.light}`,
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    backgroundColor: theme.background.primary,
  },
  taskCardSelected: {
    borderColor: theme.accent,
    backgroundColor: theme.accentLight,
    boxShadow: shadows.colored,
  },
  taskNumber: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: theme.accent,
    marginBottom: '8px',
  },
  taskDescription: {
    fontSize: '14px',
    color: theme.text.secondary,
  },
};

export default TaskSelector;
