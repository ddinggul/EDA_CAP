"""
음성 파일에서 MFCC 특징 추출 후 CSV에 추가
OpenAI GPT 파인튜닝에 음성 특징 정보 포함
"""

import librosa
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List
import json


def extract_mfcc_features(audio_path: str, sr: int = 16000, n_mfcc: int = 13) -> Dict:
    """
    음성 파일에서 MFCC 및 주요 특징 추출

    Args:
        audio_path: WAV 파일 경로
        sr: 샘플링 레이트
        n_mfcc: MFCC 계수 개수

    Returns:
        음성 특징 딕셔너리
    """

    # 오디오 로드
    y, sr = librosa.load(audio_path, sr=sr)

    # 1. MFCC 추출
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    # 2. Pitch (F0) 추출
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            pitch_values.append(pitch)

    pitch_mean = np.mean(pitch_values) if pitch_values else 0
    pitch_std = np.std(pitch_values) if pitch_values else 0

    # 3. Energy (RMS)
    energy = librosa.feature.rms(y=y)[0]
    energy_mean = float(np.mean(energy))
    energy_std = float(np.std(energy))

    # 4. Zero Crossing Rate (음성/무음 구분)
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_mean = float(np.mean(zcr))

    # 5. Spectral Centroid (음색)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_centroid_mean = float(np.mean(spectral_centroid))

    # 6. Tempo (말하기 속도)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]

    # 7. 음성 길이
    duration = float(librosa.get_duration(y=y, sr=sr))

    # 8. 무음 구간 탐지 (휴지)
    intervals = librosa.effects.split(y, top_db=30)
    num_pauses = len(intervals) - 1

    pauses = []
    for i in range(len(intervals) - 1):
        pause_duration = (intervals[i + 1][0] - intervals[i][1]) / sr
        pauses.append(pause_duration)

    pause_mean = float(np.mean(pauses)) if pauses else 0
    pause_total = float(np.sum(pauses)) if pauses else 0

    # 특징 요약
    features = {
        # MFCC 통계
        'mfcc_mean_0': float(mfcc_mean[0]),
        'mfcc_mean_1': float(mfcc_mean[1]),
        'mfcc_mean_2': float(mfcc_mean[2]),
        'mfcc_std_0': float(mfcc_std[0]),
        'mfcc_std_1': float(mfcc_std[1]),

        # Pitch (음높이)
        'pitch_mean': float(pitch_mean),
        'pitch_std': float(pitch_std),

        # Energy (음량)
        'energy_mean': energy_mean,
        'energy_std': energy_std,

        # 기타
        'zcr_mean': zcr_mean,
        'spectral_centroid_mean': spectral_centroid_mean,
        'tempo': float(tempo),

        # 유창성 관련
        'duration': duration,
        'num_pauses': num_pauses,
        'pause_mean': pause_mean,
        'pause_total': pause_total,
        'speech_rate': num_pauses / duration if duration > 0 else 0
    }

    return features


def create_text_summary(features: Dict) -> str:
    """
    음성 특징을 텍스트로 요약 (GPT에게 전달할 형식)

    Args:
        features: 음성 특징 딕셔너리

    Returns:
        텍스트 요약
    """

    summary = f"""음성 특징 분석:
- 길이: {features['duration']:.1f}초
- 말하기 속도: {features['speech_rate']:.2f} 구간/초
- 평균 Pitch: {features['pitch_mean']:.1f}Hz (변동: {features['pitch_std']:.1f})
- 평균 Energy: {features['energy_mean']:.3f} (안정성: {features['energy_std']:.3f})
- 휴지(Pause): {features['num_pauses']}회, 평균 {features['pause_mean']:.2f}초
- MFCC[0-2]: [{features['mfcc_mean_0']:.2f}, {features['mfcc_mean_1']:.2f}, {features['mfcc_mean_2']:.2f}]
"""

    # 특징 해석 추가
    interpretations = []

    # 말하기 속도
    if features['speech_rate'] < 2:
        interpretations.append("- 말하기 속도가 느림 (휴지 많음)")
    elif features['speech_rate'] > 5:
        interpretations.append("- 말하기 속도가 빠름 (유창함)")

    # 휴지
    if features['pause_mean'] > 1.0:
        interpretations.append("- 긴 휴지 → 말더듬 또는 생각하는 시간 많음")

    # Pitch 변동
    if features['pitch_std'] < 20:
        interpretations.append("- Pitch 변동 적음 → 단조로운 억양")
    elif features['pitch_std'] > 50:
        interpretations.append("- Pitch 변동 많음 → 풍부한 억양")

    if interpretations:
        summary += "\n특징 해석:\n" + "\n".join(interpretations)

    return summary


def process_audio_files_to_csv(
    audio_dir: str,
    csv_path: str,
    output_csv: str = "feedback_with_features.csv"
):
    """
    음성 파일들의 특징을 추출하여 CSV에 추가

    Args:
        audio_dir: WAV 파일 디렉토리
        csv_path: 기존 피드백 CSV
        output_csv: 출력 CSV 파일
    """

    print("=" * 60)
    print("🎤 음성 특징 추출 및 CSV 통합")
    print("=" * 60)
    print()

    # 기존 CSV 로드
    df = pd.read_csv(csv_path)
    print(f"📊 기존 CSV 로드: {len(df)}개 행")

    # 음성 파일 목록
    audio_files = list(Path(audio_dir).glob("*.wav"))
    print(f"🎵 WAV 파일: {len(audio_files)}개")
    print()

    # 새 컬럼들 준비
    feature_columns = [
        'audio_duration', 'pitch_mean', 'pitch_std',
        'energy_mean', 'num_pauses', 'pause_mean',
        'speech_rate', 'audio_summary'
    ]

    # 기존 컬럼에 없으면 추가
    for col in feature_columns:
        if col not in df.columns:
            df[col] = None

    # 각 음성 파일 처리
    matched_count = 0

    for i, audio_file in enumerate(audio_files):
        print(f"[{i+1}/{len(audio_files)}] {audio_file.name}")

        try:
            # 특징 추출
            features = extract_mfcc_features(str(audio_file))

            # 텍스트 요약 생성
            text_summary = create_text_summary(features)

            # 파일명으로 CSV 매칭
            file_id = audio_file.stem
            matching_rows = df[df['파일 이름'].str.contains(file_id, na=False)]

            if not matching_rows.empty:
                idx = matching_rows.index[0]

                # CSV에 특징 추가
                df.at[idx, 'audio_duration'] = features['duration']
                df.at[idx, 'pitch_mean'] = features['pitch_mean']
                df.at[idx, 'pitch_std'] = features['pitch_std']
                df.at[idx, 'energy_mean'] = features['energy_mean']
                df.at[idx, 'num_pauses'] = features['num_pauses']
                df.at[idx, 'pause_mean'] = features['pause_mean']
                df.at[idx, 'speech_rate'] = features['speech_rate']
                df.at[idx, 'audio_summary'] = text_summary

                matched_count += 1
                print(f"   ✅ 매칭됨: {df.at[idx, '파일 이름']}")
                print(f"   길이: {features['duration']:.1f}초, "
                      f"Pitch: {features['pitch_mean']:.1f}Hz, "
                      f"휴지: {features['num_pauses']}회")
            else:
                print(f"   ⚠️  CSV에서 매칭 실패: {file_id}")

        except Exception as e:
            print(f"   ❌ 오류: {e}")
            continue

        print()

    # CSV 저장
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')

    print("=" * 60)
    print("✅ 완료!")
    print("=" * 60)
    print(f"총 {len(audio_files)}개 파일 중 {matched_count}개 매칭")
    print(f"💾 저장: {output_csv}")
    print()

    # 통계
    print("📊 추출된 특징 통계:")
    if matched_count > 0:
        print(f"  평균 길이: {df['audio_duration'].mean():.1f}초")
        print(f"  평균 Pitch: {df['pitch_mean'].mean():.1f}Hz")
        print(f"  평균 휴지 횟수: {df['num_pauses'].mean():.1f}회")
        print(f"  평균 말하기 속도: {df['speech_rate'].mean():.2f} 구간/초")

    return output_csv


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='음성 특징 추출 및 CSV 통합')
    parser.add_argument('--audio_dir', type=str, required=True,
                        help='WAV 파일 디렉토리')
    parser.add_argument('--csv', type=str, required=True,
                        help='기존 피드백 CSV')
    parser.add_argument('--output', type=str, default='feedback_with_features.csv',
                        help='출력 CSV 파일')

    args = parser.parse_args()

    if not Path(args.audio_dir).exists():
        print(f"❌ 디렉토리를 찾을 수 없습니다: {args.audio_dir}")
        exit(1)

    if not Path(args.csv).exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {args.csv}")
        exit(1)

    # 실행
    output_csv = process_audio_files_to_csv(
        audio_dir=args.audio_dir,
        csv_path=args.csv,
        output_csv=args.output
    )

    print("\n다음 단계:")
    print("="*60)
    print("1. 생성된 CSV 확인:")
    print(f"   cat {output_csv}")
    print()
    print("2. OpenAI 파인튜닝 데이터 생성:")
    print(f"   python prepare_openai_finetuning.py --csv {output_csv}")
    print("="*60)
