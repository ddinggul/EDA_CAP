"""
음성 특징 추출 및 발음/유창성 분석
MFCC, Pitch, Energy 등 음성 특징 추출
"""

import numpy as np
import librosa
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import json
import warnings
warnings.filterwarnings('ignore')


class AudioFeatureExtractor:
    """음성 파일에서 TOEFL 평가에 필요한 특징 추출"""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def extract_mfcc_features(self, audio_path: str, n_mfcc: int = 13) -> Dict:
        """
        MFCC (Mel-frequency cepstral coefficients) 추출
        발음 특징 분석에 사용
        """
        # 오디오 로드
        y, sr = librosa.load(audio_path, sr=self.sample_rate)

        # MFCC 추출
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        mfcc_delta = librosa.feature.delta(mfcc)
        mfcc_delta2 = librosa.feature.delta(mfcc, order=2)

        return {
            'mfcc_mean': np.mean(mfcc, axis=1).tolist(),
            'mfcc_std': np.std(mfcc, axis=1).tolist(),
            'mfcc_delta_mean': np.mean(mfcc_delta, axis=1).tolist(),
            'mfcc_delta2_mean': np.mean(mfcc_delta2, axis=1).tolist(),
        }

    def extract_prosody_features(self, audio_path: str) -> Dict:
        """
        운율(Prosody) 특징 추출
        유창성, 억양, 리듬 분석에 사용
        """
        y, sr = librosa.load(audio_path, sr=self.sample_rate)

        # Pitch (F0) 추출
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)

        # Energy (음량)
        energy = librosa.feature.rms(y=y)[0]

        # Zero Crossing Rate (음성/무음 구분)
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        # Spectral features (음질)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

        # 말하기 속도 (음절 수 추정)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]

        return {
            'pitch_mean': np.mean(pitch_values) if pitch_values else 0,
            'pitch_std': np.std(pitch_values) if pitch_values else 0,
            'pitch_range': np.ptp(pitch_values) if pitch_values else 0,
            'energy_mean': float(np.mean(energy)),
            'energy_std': float(np.std(energy)),
            'zcr_mean': float(np.mean(zcr)),
            'spectral_centroid_mean': float(np.mean(spectral_centroid)),
            'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
            'tempo': float(tempo),
            'duration': float(librosa.get_duration(y=y, sr=sr))
        }

    def extract_pronunciation_features(self, audio_path: str) -> Dict:
        """
        발음 관련 특징 추출
        자음/모음 명확성, 음소 정확도
        """
        y, sr = librosa.load(audio_path, sr=self.sample_rate)

        # Formants (모음 분석)
        # F1, F2로 모음 구분 가능
        S = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=sr)

        # Spectral contrast (자음 명확성)
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

        # Chroma features (음높이 정확도)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)

        return {
            'spectral_contrast_mean': np.mean(contrast, axis=1).tolist(),
            'chroma_mean': np.mean(chroma, axis=1).tolist(),
            'spectral_flux': float(np.mean(np.diff(S, axis=1)))
        }

    def extract_fluency_features(self, audio_path: str) -> Dict:
        """
        유창성 관련 특징 추출
        휴지(pause), 말더듬, 속도 변화
        """
        y, sr = librosa.load(audio_path, sr=self.sample_rate)

        # 무음 구간 탐지 (휴지)
        intervals = librosa.effects.split(y, top_db=30)

        # 휴지 시간 계산
        pauses = []
        for i in range(len(intervals) - 1):
            pause_start = intervals[i][1]
            pause_end = intervals[i + 1][0]
            pause_duration = (pause_end - pause_start) / sr
            pauses.append(pause_duration)

        # 발화 구간 길이
        speech_durations = [(end - start) / sr for start, end in intervals]

        return {
            'num_pauses': len(pauses),
            'pause_mean': float(np.mean(pauses)) if pauses else 0,
            'pause_std': float(np.std(pauses)) if pauses else 0,
            'pause_total': float(np.sum(pauses)) if pauses else 0,
            'speech_rate': len(intervals) / (len(y) / sr),  # 발화 구간/초
            'speech_duration_mean': float(np.mean(speech_durations)) if speech_durations else 0,
            'articulation_rate': len(intervals) / (np.sum(speech_durations) if speech_durations else 1)
        }

    def extract_all_features(self, audio_path: str) -> Dict:
        """모든 음성 특징 한번에 추출"""
        features = {}

        features.update(self.extract_mfcc_features(audio_path))
        features.update(self.extract_prosody_features(audio_path))
        features.update(self.extract_pronunciation_features(audio_path))
        features.update(self.extract_fluency_features(audio_path))

        return features


def process_audio_dataset(
    audio_dir: str,
    csv_path: str,
    output_path: str = "audio_features.jsonl"
):
    """
    전체 데이터셋의 음성 특징 추출

    Args:
        audio_dir: WAV 파일들이 있는 디렉토리
        csv_path: 피드백 CSV 파일
        output_path: 출력 JSONL 파일
    """

    extractor = AudioFeatureExtractor()

    # CSV 로드
    df = pd.read_csv(csv_path)

    results = []

    print(f"📂 음성 파일 처리 중: {audio_dir}")
    print(f"📊 CSV 파일: {csv_path}")
    print()

    # 각 WAV 파일 처리
    audio_files = list(Path(audio_dir).glob("*.wav"))

    for i, audio_file in enumerate(audio_files):
        print(f"[{i+1}/{len(audio_files)}] 처리 중: {audio_file.name}")

        try:
            # 음성 특징 추출
            features = extractor.extract_all_features(str(audio_file))

            # 파일명으로 CSV에서 매칭 (파일명 규칙에 따라 수정 필요)
            file_id = audio_file.stem  # 확장자 제외한 파일명

            # CSV에서 해당 행 찾기
            matching_row = df[df['파일 이름'].str.contains(file_id, na=False)]

            if not matching_row.empty:
                row = matching_row.iloc[0]

                result = {
                    'audio_file': audio_file.name,
                    'file_id': file_id,
                    'audio_features': features,
                    'ground_truth': {
                        'transcript': row.get('텍스트', ''),
                        'pronunciation_score': row.get('발음', ''),
                        'fluency_score': row.get('fluency', ''),
                        'content_score': row.get('내용', ''),
                        'grammar_score': row.get('문법/표현', ''),
                        'total_score': row.get('total_score', 0),
                        'feedback': row.get('텍스트 피드백', '')
                    }
                }

                results.append(result)
            else:
                print(f"  ⚠️  CSV에서 매칭되는 행을 찾을 수 없음: {file_id}")

        except Exception as e:
            print(f"  ❌ 오류: {e}")
            continue

    # JSONL로 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')

    print(f"\n✅ 완료! {len(results)}개 파일 처리")
    print(f"💾 저장 위치: {output_path}")

    return results


def create_feature_summary(jsonl_path: str):
    """추출된 특징 요약 통계"""

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    print(f"\n📊 데이터셋 요약")
    print(f"총 샘플 수: {len(data)}")
    print()

    # 점수 분포
    scores = [d['ground_truth']['total_score'] for d in data]
    print(f"점수 분포:")
    print(f"  평균: {np.mean(scores):.2f}")
    print(f"  표준편차: {np.std(scores):.2f}")
    print(f"  범위: {np.min(scores):.1f} - {np.max(scores):.1f}")
    print()

    # 음성 특징 요약
    durations = [d['audio_features']['duration'] for d in data]
    tempos = [d['audio_features']['tempo'] for d in data]

    print(f"음성 특징:")
    print(f"  평균 길이: {np.mean(durations):.1f}초")
    print(f"  평균 템포: {np.mean(tempos):.1f} BPM")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='TOEFL 음성 특징 추출')
    parser.add_argument('--audio_dir', type=str, required=True,
                        help='WAV 파일 디렉토리')
    parser.add_argument('--csv', type=str, required=True,
                        help='피드백 CSV 파일')
    parser.add_argument('--output', type=str, default='audio_features.jsonl',
                        help='출력 JSONL 파일')

    args = parser.parse_args()

    # 예시 실행
    if Path(args.audio_dir).exists() and Path(args.csv).exists():
        results = process_audio_dataset(
            args.audio_dir,
            args.csv,
            args.output
        )

        create_feature_summary(args.output)
    else:
        print("❌ 파일 경로를 확인하세요.")
        print(f"예시: python audio_feature_extraction.py --audio_dir ./audio --csv feedback.csv")
