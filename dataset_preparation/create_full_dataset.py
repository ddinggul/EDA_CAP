"""
전체 데이터셋 준비 파이프라인
음성 특징 추출 + 음성 모델 학습 + LLM 데이터 준비를 한 번에 실행
"""

import argparse
import json
from pathlib import Path
import sys

# 상위 폴더를 import path에 추가
sys.path.append(str(Path(__file__).parent))

from audio_feature_extraction import process_audio_dataset, create_feature_summary
from train_audio_model import train_audio_model
from prepare_training_data import convert_to_training_format, validate_training_data


def create_full_dataset(
    audio_dir: str,
    csv_path: str,
    output_dir: str = "../processed_data",
    train_audio_model_flag: bool = True,
    prepare_llm_data: bool = True,
    audio_model_epochs: int = 100,
    llm_format: str = "huggingface"
):
    """
    전체 데이터셋 준비 파이프라인

    Args:
        audio_dir: WAV 파일 디렉토리
        csv_path: 피드백 CSV 파일
        output_dir: 출력 디렉토리
        train_audio_model_flag: 음성 모델 학습 여부
        prepare_llm_data: LLM 데이터 준비 여부
        audio_model_epochs: 음성 모델 학습 에포크
        llm_format: LLM 데이터 형식 (openai/huggingface/gemini)
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("🎓 TOEFL 스피킹 평가 데이터셋 준비 파이프라인")
    print("=" * 80)
    print(f"음성 디렉토리: {audio_dir}")
    print(f"CSV 파일: {csv_path}")
    print(f"출력 디렉토리: {output_dir}")
    print("=" * 80)
    print()

    # ===================================================================
    # 1단계: 음성 특징 추출
    # ===================================================================
    print("📊 [1/3] 음성 특징 추출")
    print("-" * 80)

    audio_features_path = output_path / "audio_features.jsonl"

    if not audio_features_path.exists():
        print("🎤 음성 파일 처리 시작...")

        results = process_audio_dataset(
            audio_dir=audio_dir,
            csv_path=csv_path,
            output_path=str(audio_features_path)
        )

        print()
        create_feature_summary(str(audio_features_path))
        print()
    else:
        print(f"✅ 음성 특징 파일이 이미 존재합니다: {audio_features_path}")
        print("   (삭제 후 다시 실행하면 재생성됩니다)")
        print()

    # ===================================================================
    # 2단계: 음성 모델 학습 (선택)
    # ===================================================================
    if train_audio_model_flag:
        print("📊 [2/3] 음성 평가 모델 학습 (LSTM)")
        print("-" * 80)

        audio_model_dir = output_path / "audio_model"

        if not (audio_model_dir / "best_model.pth").exists():
            print("🧠 LSTM 모델 학습 시작...")

            train_audio_model(
                jsonl_path=str(audio_features_path),
                output_dir=str(audio_model_dir),
                epochs=audio_model_epochs,
                batch_size=32,
                learning_rate=0.001
            )
            print()
        else:
            print(f"✅ 음성 모델이 이미 존재합니다: {audio_model_dir}")
            print("   (폴더 삭제 후 다시 실행하면 재학습됩니다)")
            print()
    else:
        print("⏭️  [2/3] 음성 모델 학습 건너뛰기")
        print()

    # ===================================================================
    # 3단계: LLM 파인튜닝 데이터 준비 (선택)
    # ===================================================================
    if prepare_llm_data:
        print("📊 [3/3] LLM 파인튜닝 데이터 준비")
        print("-" * 80)

        llm_data_path = output_path / f"training_data_{llm_format}.jsonl"

        if not llm_data_path.exists():
            print(f"📝 LLM 데이터 생성 중 ({llm_format} 형식)...")

            # CSV에서 LLM 데이터 생성
            convert_to_training_format(
                csv_path=csv_path,
                output_path=str(llm_data_path),
                format_type=llm_format
            )

            print()
            validate_training_data(str(llm_data_path))
            print()
        else:
            print(f"✅ LLM 데이터가 이미 존재합니다: {llm_data_path}")
            print("   (삭제 후 다시 실행하면 재생성됩니다)")
            print()
    else:
        print("⏭️  [3/3] LLM 데이터 준비 건너뛰기")
        print()

    # ===================================================================
    # 완료 요약
    # ===================================================================
    print("=" * 80)
    print("✅ 데이터셋 준비 완료!")
    print("=" * 80)
    print()
    print("📁 생성된 파일:")
    print(f"   1. 음성 특징: {audio_features_path}")

    if train_audio_model_flag:
        audio_model_dir = output_path / "audio_model"
        print(f"   2. 음성 모델: {audio_model_dir}/")
        print(f"      - best_model.pth (LSTM 모델)")
        print(f"      - scaler.pkl (정규화 스케일러)")
        print(f"      - metadata.json (메타정보)")

    if prepare_llm_data:
        llm_data_path = output_path / f"training_data_{llm_format}.jsonl"
        print(f"   3. LLM 데이터: {llm_data_path}")

    print()
    print("📌 다음 단계:")

    if train_audio_model_flag:
        print("   ✅ 음성 모델 학습 완료 - 바로 사용 가능!")
    else:
        print("   ➡️  음성 모델 학습:")
        print(f"      python train_audio_model.py --data {audio_features_path}")

    if prepare_llm_data:
        print()
        print("   ➡️  LLM 파인튜닝:")
        if llm_format == "huggingface":
            print("      python ../finetune_huggingface.py")
            print("      또는 python ../finetune_m2_mac.py (M2 Mac)")
        elif llm_format == "openai":
            print("      python ../finetune_openai.py")

    print()
    print("   ➡️  통합 평가:")
    print("      python ../integrated_evaluation_system.py \\")
    print("        --audio student.wav \\")
    print("        --transcript 'text...' \\")
    print(f"        --audio_model {output_path / 'audio_model'}")

    print()
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='TOEFL 평가 데이터셋 전체 준비 파이프라인',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 전체 자동 실행 (음성 모델 학습 포함)
  python create_full_dataset.py \\
    --audio_dir ../audio \\
    --csv ../feedback.csv \\
    --train_audio_model

  # 음성 특징만 추출
  python create_full_dataset.py \\
    --audio_dir ../audio \\
    --csv ../feedback.csv \\
    --no_train_audio \\
    --no_llm_data

  # LLM 데이터만 준비
  python create_full_dataset.py \\
    --csv ../feedback.csv \\
    --only_llm_data \\
    --llm_format openai
        """
    )

    parser.add_argument('--audio_dir', type=str,
                        help='WAV 파일 디렉토리')
    parser.add_argument('--csv', type=str, required=True,
                        help='피드백 CSV 파일')
    parser.add_argument('--output_dir', type=str, default='../processed_data',
                        help='출력 디렉토리 (기본: ../processed_data)')

    # 음성 모델 옵션
    parser.add_argument('--train_audio_model', action='store_true',
                        help='음성 모델 학습 실행')
    parser.add_argument('--no_train_audio', action='store_true',
                        help='음성 모델 학습 건너뛰기')
    parser.add_argument('--audio_epochs', type=int, default=100,
                        help='음성 모델 학습 에포크 (기본: 100)')

    # LLM 데이터 옵션
    parser.add_argument('--llm_format', type=str,
                        choices=['openai', 'huggingface', 'gemini'],
                        default='huggingface',
                        help='LLM 데이터 형식 (기본: huggingface)')
    parser.add_argument('--no_llm_data', action='store_true',
                        help='LLM 데이터 준비 건너뛰기')

    # 특수 모드
    parser.add_argument('--only_llm_data', action='store_true',
                        help='LLM 데이터만 준비 (음성 처리 건너뛰기)')

    args = parser.parse_args()

    # 검증
    if not args.only_llm_data and not args.audio_dir:
        parser.error("--audio_dir이 필요합니다. (또는 --only_llm_data 사용)")

    if not Path(args.csv).exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {args.csv}")
        sys.exit(1)

    if not args.only_llm_data and not Path(args.audio_dir).exists():
        print(f"❌ 음성 디렉토리를 찾을 수 없습니다: {args.audio_dir}")
        sys.exit(1)

    # 실행
    if args.only_llm_data:
        # LLM 데이터만
        print("📝 LLM 데이터만 준비합니다...")
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        llm_data_path = output_path / f"training_data_{args.llm_format}.jsonl"
        convert_to_training_format(
            csv_path=args.csv,
            output_path=str(llm_data_path),
            format_type=args.llm_format
        )
        validate_training_data(str(llm_data_path))
    else:
        # 전체 파이프라인
        create_full_dataset(
            audio_dir=args.audio_dir,
            csv_path=args.csv,
            output_dir=args.output_dir,
            train_audio_model_flag=args.train_audio_model and not args.no_train_audio,
            prepare_llm_data=not args.no_llm_data,
            audio_model_epochs=args.audio_epochs,
            llm_format=args.llm_format
        )


if __name__ == "__main__":
    main()
