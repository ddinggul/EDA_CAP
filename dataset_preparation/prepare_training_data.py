import pandas as pd
import json
from pathlib import Path

def convert_to_training_format(csv_path: str, output_path: str, format_type: str = "openai"):
    """
    CSV 데이터를 LLM 파인튜닝 형식으로 변환

    Args:
        csv_path: 입력 CSV 파일 경로
        output_path: 출력 JSONL 파일 경로
        format_type: 'openai', 'huggingface', 'gemini' 중 선택
    """
    df = pd.read_csv(csv_path)

    training_data = []

    for idx, row in df.iterrows():
        # 기본 정보 추출
        text = row['텍스트']
        feedback = row['텍스트 피드백'] if pd.notna(row['텍스트 피드백']) else ""
        pronunciation = row['발음'] if pd.notna(row['발음']) else ""
        fluency = row['fluency'] if pd.notna(row['fluency']) else ""
        content = row['내용'] if pd.notna(row['내용']) else ""
        grammar = row['문법/표현'] if pd.notna(row['문법/표현']) else ""
        total_score = row['total_score']

        # 시스템 프롬프트 구성
        system_prompt = """당신은 TOEFL 스피킹 평가 전문가입니다. 학생의 답변을 다음 기준으로 평가하세요:

1. 발음(Pronunciation): 개별 음소의 정확성, R/L 구분, 장단모음 구분
2. 유창성(Fluency): 말하기 속도, 톤 조절, 강조, 자연스러움
3. 내용(Content): 질문에 대한 적절한 답변, 논리적 구조
4. 문법/표현(Grammar & Expression): 문법적 정확성, 적절한 어휘 사용

각 항목에 대한 구체적인 피드백과 함께 총점(0-4점)을 제공하세요."""

        # 사용자 입력 구성
        user_input = f"다음 학생의 답변을 평가해주세요:\n\n{text}"

        # 모델 응답 구성 (Ground Truth)
        assistant_response = f"""평가 결과:

**발음 (Pronunciation):**
{pronunciation if pronunciation else '평가 내용 없음'}

**유창성 (Fluency):**
{fluency if fluency else '평가 내용 없음'}

**내용 (Content):**
{content if content else '평가 내용 없음'}

**문법/표현 (Grammar & Expression):**
{grammar if grammar else '평가 내용 없음'}

**추가 피드백:**
{feedback if feedback else '없음'}

**총점: {total_score}/4.0**"""

        # 형식에 맞게 변환
        if format_type == "openai":
            # OpenAI Fine-tuning 형식 (GPT-3.5, GPT-4)
            training_example = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": assistant_response}
                ]
            }
        elif format_type == "huggingface":
            # HuggingFace 형식
            training_example = {
                "text": f"<|system|>\n{system_prompt}\n<|user|>\n{user_input}\n<|assistant|>\n{assistant_response}"
            }
        elif format_type == "gemini":
            # Google Gemini 형식
            training_example = {
                "contents": [
                    {"role": "user", "parts": [{"text": user_input}]},
                    {"role": "model", "parts": [{"text": assistant_response}]}
                ],
                "system_instruction": {"parts": [{"text": system_prompt}]}
            }
        else:
            raise ValueError(f"Unknown format type: {format_type}")

        training_data.append(training_example)

    # JSONL 형식으로 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in training_data:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"✅ {len(training_data)}개의 학습 데이터를 {output_path}에 저장했습니다.")
    return training_data


def validate_training_data(jsonl_path: str):
    """학습 데이터의 품질 검증"""
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    print(f"\n📊 데이터 통계:")
    print(f"총 샘플 수: {len(data)}")

    # 토큰 길이 분석 (간단한 추정)
    total_tokens = 0
    for item in data:
        if 'messages' in item:
            for msg in item['messages']:
                total_tokens += len(msg['content'].split())

    avg_tokens = total_tokens / len(data) if data else 0
    print(f"평균 토큰 수 (추정): {avg_tokens:.1f}")
    print(f"\n권장사항:")
    print(f"- 최소 학습 데이터: 50-100개")
    print(f"- 현재 데이터: {len(data)}개")

    if len(data) < 50:
        print(f"⚠️  데이터가 부족합니다. 더 많은 평가 샘플을 수집하세요.")
    else:
        print(f"✅ 충분한 데이터가 있습니다.")


if __name__ == "__main__":
    # 예시 실행
    print("TOEFL 스피킹 평가 파인튜닝 데이터 준비 도구\n")

    # CSV 파일 경로 설정
    csv_file = "toefl_evaluations.csv"

    if not Path(csv_file).exists():
        print(f"❌ {csv_file} 파일을 찾을 수 없습니다.")
        print("CSV 파일을 먼저 준비해주세요.")
    else:
        # 여러 형식으로 변환
        print("변환할 형식을 선택하세요:")
        print("1. OpenAI (GPT-3.5/GPT-4)")
        print("2. HuggingFace (Llama, Mistral 등)")
        print("3. Google Gemini")

        choice = input("\n선택 (1-3): ").strip()

        format_map = {
            "1": "openai",
            "2": "huggingface",
            "3": "gemini"
        }

        format_type = format_map.get(choice, "openai")
        output_file = f"training_data_{format_type}.jsonl"

        training_data = convert_to_training_format(csv_file, output_file, format_type)
        validate_training_data(output_file)
