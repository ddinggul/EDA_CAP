// frontend/src/components/FileUploader.tsx
import React, { useRef } from 'react';
import { theme } from '../theme';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelect, selectedFile }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/m4a', 'audio/ogg', 'audio/webm'];
      const fileExtension = file.name.split('.').pop()?.toLowerCase();
      const allowedExtensions = ['mp3', 'wav', 'm4a', 'ogg', 'webm'];

      if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension || '')) {
        alert('올바른 음성 파일을 업로드해주세요 (mp3, wav, m4a, ogg, webm)');
        return;
      }

      // Validate file size (max 50MB)
      const maxSize = 50 * 1024 * 1024;
      if (file.size > maxSize) {
        alert('파일 크기는 50MB 이하여야 합니다');
        return;
      }

      onFileSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div style={styles.container}>
      <h4 style={styles.title}>음성 파일 업로드</h4>
      <div style={styles.uploadBox} onClick={handleClick}>
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*,.mp3,.wav,.m4a,.ogg,.webm"
          onChange={handleFileChange}
          style={styles.hiddenInput}
        />
        {selectedFile ? (
          <div style={styles.fileInfo}>
            <div style={styles.fileIcon}>🎵</div>
            <div>
              <div style={styles.fileName}>{selectedFile.name}</div>
              <div style={styles.fileSize}>
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </div>
            </div>
          </div>
        ) : (
          <div style={styles.uploadPrompt}>
            <div style={styles.uploadIcon}>📁</div>
            <div style={styles.uploadText}>클릭하여 음성 파일 업로드</div>
            <div style={styles.uploadHint}>지원 형식: mp3, wav, m4a, ogg, webm (최대 50MB)</div>
          </div>
        )}
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
  uploadBox: {
    padding: '30px',
    border: `2px dashed ${theme.border.medium}`,
    borderRadius: '8px',
    textAlign: 'center',
    cursor: 'pointer',
    backgroundColor: theme.background.secondary,
    transition: 'all 0.3s ease',
  },
  hiddenInput: {
    display: 'none',
  },
  uploadPrompt: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '10px',
  },
  uploadIcon: {
    fontSize: '48px',
  },
  uploadText: {
    fontSize: '16px',
    color: theme.text.secondary,
    fontWeight: '500',
  },
  uploadHint: {
    fontSize: '13px',
    color: theme.text.light,
  },
  fileInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    justifyContent: 'center',
  },
  fileIcon: {
    fontSize: '36px',
  },
  fileName: {
    fontSize: '16px',
    fontWeight: '500',
    color: theme.text.primary,
    marginBottom: '5px',
  },
  fileSize: {
    fontSize: '13px',
    color: theme.text.light,
  },
};

export default FileUploader;
