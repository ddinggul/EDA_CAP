"""
OpenAI GPT 모델 파인튜닝 스크립트
GPT-3.5-turbo 또는 GPT-4를 TOEFL 스피킹 평가에 맞게 파인튜닝
"""

import openai
import json
import time
from pathlib import Path

# API 키 설정 (환경변수 또는 직접 입력)
# export OPENAI_API_KEY='your-api-key-here'
openai.api_key = "YOUR_API_KEY"  # 또는 os.getenv("OPENAI_API_KEY")


def upload_training_file(file_path: str):
    """학습 데이터 파일을 OpenAI에 업로드"""
    print(f"📤 파일 업로드 중: {file_path}")

    with open(file_path, "rb") as f:
        response = openai.File.create(
            file=f,
            purpose="fine-tune"
        )

    file_id = response["id"]
    print(f"✅ 파일 업로드 완료! File ID: {file_id}")
    return file_id


def create_fine_tune_job(training_file_id: str, model: str = "gpt-3.5-turbo"):
    """파인튜닝 작업 시작"""
    print(f"\n🚀 파인튜닝 시작...")
    print(f"모델: {model}")

    response = openai.FineTuningJob.create(
        training_file=training_file_id,
        model=model,
        hyperparameters={
            "n_epochs": 3,  # 에포크 수 (3-4 권장)
        }
    )

    job_id = response["id"]
    print(f"✅ 파인튜닝 작업 생성 완료! Job ID: {job_id}")
    return job_id


def monitor_fine_tune_job(job_id: str):
    """파인튜닝 진행 상황 모니터링"""
    print(f"\n👀 파인튜닝 진행 상황 모니터링...")

    while True:
        response = openai.FineTuningJob.retrieve(job_id)
        status = response["status"]

        print(f"상태: {status}")

        if status == "succeeded":
            print(f"\n✅ 파인튜닝 완료!")
            print(f"모델 ID: {response['fine_tuned_model']}")
            return response["fine_tuned_model"]
        elif status == "failed":
            print(f"\n❌ 파인튜닝 실패")
            print(f"에러: {response.get('error', 'Unknown error')}")
            return None

        time.sleep(60)  # 1분마다 확인


def test_fine_tuned_model(model_id: str, test_text: str):
    """파인튜닝된 모델 테스트"""
    print(f"\n🧪 모델 테스트 중...")

    response = openai.ChatCompletion.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": "당신은 TOEFL 스피킹 평가 전문가입니다."
            },
            {
                "role": "user",
                "content": f"다음 학생의 답변을 평가해주세요:\n\n{test_text}"
            }
        ],
        temperature=0.7,
        max_tokens=500
    )

    result = response.choices[0].message.content
    print("\n평가 결과:")
    print(result)
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("OpenAI GPT 파인튜닝 for TOEFL 스피킹 평가")
    print("=" * 60)

    # 1. 학습 데이터 파일 업로드
    training_file = "training_data_openai.jsonl"

    if not Path(training_file).exists():
        print(f"❌ {training_file} 파일이 없습니다.")
        print("먼저 prepare_training_data.py를 실행하세요.")
        exit(1)

    file_id = upload_training_file(training_file)

    # 2. 파인튜닝 작업 시작
    # gpt-3.5-turbo (저렴) 또는 gpt-4 (고품질) 선택
    model_choice = "gpt-3.5-turbo-0125"  # 또는 "gpt-4-0613"
    job_id = create_fine_tune_job(file_id, model=model_choice)

    # 3. 작업 모니터링
    fine_tuned_model = monitor_fine_tune_job(job_id)

    # 4. 테스트
    if fine_tuned_model:
        test_text = """From my perspective, I prefer to study subjects that interest them.
That's because I think that it is important to find a job that is suitable for my interests."""

        test_fine_tuned_model(fine_tuned_model, test_text)

        print(f"\n✅ 파인튜닝된 모델 ID를 저장하세요: {fine_tuned_model}")
        with open("fine_tuned_model_id.txt", "w") as f:
            f.write(fine_tuned_model)
