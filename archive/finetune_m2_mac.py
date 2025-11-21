"""
M2 MacBook Pro 최적화 LLM 파인튜닝 스크립트
MLX 프레임워크 사용 (Apple Silicon 최적화)

지원 모델:
- Llama-2-7B/13B
- Mistral-7B
- Phi-2/3
- Gemma-7B
"""

import json
import time
from pathlib import Path
from typing import Optional

try:
    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    from mlx_lm import load, generate
    from mlx_lm.tuner import datasets, utils
    from mlx_lm.tuner.trainer import TrainingArgs, train
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    print("⚠️  MLX가 설치되지 않았습니다.")
    print("설치: pip install mlx mlx-lm")


def prepare_data_for_mlx(jsonl_path: str, output_dir: str = "./data"):
    """
    JSONL 데이터를 MLX 형식으로 변환

    Args:
        jsonl_path: 입력 JSONL 파일 (prepare_training_data.py로 생성)
        output_dir: 출력 디렉토리
    """
    Path(output_dir).mkdir(exist_ok=True)

    print(f"📂 데이터 변환 중: {jsonl_path}")

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    # MLX 형식으로 변환 (train/valid 분할)
    train_size = int(len(data) * 0.9)
    train_data = data[:train_size]
    valid_data = data[train_size:]

    # train.jsonl 저장
    with open(f"{output_dir}/train.jsonl", 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    # valid.jsonl 저장
    with open(f"{output_dir}/valid.jsonl", 'w', encoding='utf-8') as f:
        for item in valid_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ 학습 데이터: {len(train_data)}개")
    print(f"✅ 검증 데이터: {len(valid_data)}개")
    print(f"✅ 저장 위치: {output_dir}/")

    return train_data, valid_data


def check_m2_memory():
    """M2 Mac 메모리 확인"""
    import psutil

    total_ram = psutil.virtual_memory().total / (1024**3)
    available_ram = psutil.virtual_memory().available / (1024**3)

    print(f"\n💻 시스템 정보:")
    print(f"총 RAM: {total_ram:.1f} GB")
    print(f"사용 가능 RAM: {available_ram:.1f} GB")

    # M2 Pro/Max/Ultra 확인
    import platform
    print(f"칩셋: {platform.processor()}")

    if total_ram >= 16:
        print("✅ 7B 모델 파인튜닝 가능")
        if total_ram >= 32:
            print("✅ 13B 모델 파인튜닝 가능")
    else:
        print("⚠️  RAM 부족. 더 작은 모델 권장 (Phi-2)")

    return total_ram


def fine_tune_with_mlx(
    model_name: str = "mlx-community/Mistral-7B-Instruct-v0.2-4bit",
    data_dir: str = "./data",
    output_dir: str = "./toefl_finetuned_mlx",
    num_epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 1e-5,
    lora_rank: int = 16
):
    """
    MLX를 사용한 M2 Mac 최적화 파인튜닝

    Args:
        model_name: HuggingFace 모델 또는 MLX community 모델
        data_dir: 학습 데이터 디렉토리
        output_dir: 모델 저장 경로
        num_epochs: 학습 에포크
        batch_size: 배치 크기
        learning_rate: 학습률
        lora_rank: LoRA rank (메모리 효율성)
    """

    if not MLX_AVAILABLE:
        print("❌ MLX를 먼저 설치하세요: pip install mlx mlx-lm")
        return

    print("=" * 60)
    print(f"M2 Mac 파인튜닝 시작: {model_name}")
    print("=" * 60)

    # 메모리 체크
    total_ram = check_m2_memory()

    # 학습 설정
    training_args = TrainingArgs(
        model=model_name,
        data=data_dir,
        train=True,
        iters=num_epochs * 100,  # 반복 횟수
        batch_size=batch_size,
        learning_rate=learning_rate,
        lora_layers=16,  # LoRA를 적용할 레이어 수
        adapter_file=f"{output_dir}/adapters.npz",
        save_every=100,
        test=True,
        test_batches=10
    )

    print(f"\n⚙️  학습 설정:")
    print(f"  - 모델: {model_name}")
    print(f"  - 에포크: {num_epochs}")
    print(f"  - 배치 크기: {batch_size}")
    print(f"  - 학습률: {learning_rate}")
    print(f"  - LoRA rank: {lora_rank}")

    # 파인튜닝 시작
    print(f"\n🚀 파인튜닝 시작...")
    start_time = time.time()

    try:
        # MLX 파인튜닝 실행
        train(
            model=model_name,
            data=data_dir,
            adapter_path=output_dir,
            iters=training_args.iters,
            batch_size=batch_size,
            learning_rate=learning_rate,
            save_every=100,
            test=True
        )

        elapsed = time.time() - start_time
        print(f"\n✅ 파인튜닝 완료! (소요 시간: {elapsed/60:.1f}분)")
        print(f"💾 어댑터 저장 위치: {output_dir}/adapters.npz")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("MLX 버전과 모델 호환성을 확인하세요.")

    return output_dir


def test_finetuned_model(
    model_name: str,
    adapter_path: str,
    test_text: str,
    max_tokens: int = 500
):
    """파인튜닝된 모델 테스트"""

    print("\n🧪 모델 테스트 중...")

    # 모델 및 어댑터 로드
    print(f"📥 모델 로딩: {model_name}")
    print(f"📥 어댑터 로딩: {adapter_path}")

    model, tokenizer = load(model_name, adapter_path=adapter_path)

    # 프롬프트 구성
    prompt = f"""<|system|>
당신은 TOEFL 스피킹 평가 전문가입니다. 학생의 답변을 다음 기준으로 평가하세요:
1. 발음 (Pronunciation)
2. 유창성 (Fluency)
3. 내용 (Content)
4. 문법/표현 (Grammar & Expression)
<|user|>
다음 학생의 답변을 평가해주세요:

{test_text}
<|assistant|>
"""

    print("\n생성 중...")
    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens,
        temp=0.7
    )

    print("\n" + "=" * 60)
    print("평가 결과:")
    print("=" * 60)
    print(response)
    print("=" * 60)

    return response


def interactive_evaluation(model_name: str, adapter_path: str):
    """대화형 평가 모드"""

    print("\n" + "=" * 60)
    print("🎓 TOEFL 스피킹 평가 시스템 (MLX on M2)")
    print("=" * 60)
    print("종료하려면 'quit' 입력")
    print()

    model, tokenizer = load(model_name, adapter_path=adapter_path)

    while True:
        text = input("\n학생 답변을 입력하세요:\n> ")

        if text.lower() in ['quit', 'exit', 'q']:
            print("👋 종료합니다.")
            break

        if not text.strip():
            continue

        prompt = f"""<|system|>
당신은 TOEFL 스피킹 평가 전문가입니다.
<|user|>
다음 답변을 평가해주세요:

{text}
<|assistant|>
"""

        print("\n평가 중...")
        response = generate(model, tokenizer, prompt=prompt, max_tokens=400, temp=0.7)

        print("\n" + "─" * 60)
        print(response)
        print("─" * 60)


# M2 Mac에 최적화된 권장 모델 목록
M2_RECOMMENDED_MODELS = {
    "8GB RAM": [
        "mlx-community/Phi-2-4bit",  # 가장 가벼움
        "mlx-community/TinyLlama-1.1B-4bit",
    ],
    "16GB RAM": [
        "mlx-community/Mistral-7B-Instruct-v0.2-4bit",  # 권장 ⭐
        "mlx-community/Llama-2-7b-chat-4bit",
        "mlx-community/gemma-7b-it-4bit",
    ],
    "32GB+ RAM": [
        "mlx-community/Llama-2-13b-chat-4bit",
        "mlx-community/Mixtral-8x7B-Instruct-v0.1-4bit",
    ]
}


def print_recommended_models():
    """RAM 용량별 권장 모델 출력"""
    total_ram = check_m2_memory()

    print("\n📋 RAM 용량별 권장 모델:\n")

    for ram_size, models in M2_RECOMMENDED_MODELS.items():
        print(f"[{ram_size}]")
        for model in models:
            print(f"  - {model}")
        print()

    # 현재 시스템 권장
    if total_ram >= 32:
        recommended = M2_RECOMMENDED_MODELS["32GB+ RAM"]
        category = "32GB+ RAM"
    elif total_ram >= 16:
        recommended = M2_RECOMMENDED_MODELS["16GB RAM"]
        category = "16GB RAM"
    else:
        recommended = M2_RECOMMENDED_MODELS["8GB RAM"]
        category = "8GB RAM"

    print(f"💡 현재 시스템({total_ram:.0f}GB)에 권장: [{category}]")
    for model in recommended:
        print(f"  ✅ {model}")


if __name__ == "__main__":
    print("=" * 60)
    print("🍎 M2 MacBook Pro TOEFL 평가 파인튜닝")
    print("=" * 60)

    # 1. 시스템 체크 및 권장 모델 출력
    print_recommended_models()

    # 2. 데이터 준비
    print("\n" + "=" * 60)
    print("1단계: 데이터 준비")
    print("=" * 60)

    jsonl_file = "training_data_huggingface.jsonl"

    if not Path(jsonl_file).exists():
        print(f"⚠️  {jsonl_file} 파일이 없습니다.")
        print("먼저 prepare_training_data.py를 실행하세요:")
        print("  python prepare_training_data.py")
        exit(1)

    # JSONL → MLX 형식 변환
    train_data, valid_data = prepare_data_for_mlx(jsonl_file, output_dir="./data")

    # 3. 모델 선택
    print("\n" + "=" * 60)
    print("2단계: 모델 선택")
    print("=" * 60)

    print("\n권장 모델:")
    print("1. Mistral-7B-Instruct (권장, 균형잡힌 성능)")
    print("2. Llama-2-7b-chat (안정적)")
    print("3. Phi-2 (가벼움, 8GB RAM)")
    print("4. 직접 입력")

    choice = input("\n선택 (1-4): ").strip()

    model_map = {
        "1": "mlx-community/Mistral-7B-Instruct-v0.2-4bit",
        "2": "mlx-community/Llama-2-7b-chat-4bit",
        "3": "mlx-community/Phi-2-4bit",
    }

    if choice in model_map:
        selected_model = model_map[choice]
    elif choice == "4":
        selected_model = input("모델 이름 입력: ").strip()
    else:
        selected_model = model_map["1"]  # 기본값

    print(f"\n✅ 선택된 모델: {selected_model}")

    # 4. 파인튜닝 실행
    print("\n" + "=" * 60)
    print("3단계: 파인튜닝")
    print("=" * 60)

    adapter_path = fine_tune_with_mlx(
        model_name=selected_model,
        data_dir="./data",
        output_dir="./toefl_finetuned_mlx",
        num_epochs=3,
        batch_size=4,
        learning_rate=1e-5,
        lora_rank=16
    )

    # 5. 테스트
    print("\n" + "=" * 60)
    print("4단계: 모델 테스트")
    print("=" * 60)

    test_text = """From my perspective, I prefer to study subjects that interest them.
That's because I think that it is important to find a job that is suitable for my interests."""

    test_finetuned_model(
        model_name=selected_model,
        adapter_path=adapter_path,
        test_text=test_text
    )

    # 6. 대화형 모드 (선택)
    print("\n대화형 평가 모드를 시작하시겠습니까? (y/n): ", end="")
    if input().lower() == 'y':
        interactive_evaluation(selected_model, adapter_path)

    print("\n✅ 모든 작업 완료!")
    print(f"💾 어댑터 위치: {adapter_path}/adapters.npz")
