"""
OpenAI GPT 파인튜닝 데이터 준비
MFCC 음성 특징 + Clova API 발음평가 + 텍스트 → GPT 학습 데이터
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict


def create_openai_training_data(
    csv_path: str,
    output_path: str = "openai_training_data.jsonl",
    include_audio_features: bool = True
):
    """
    CSV 데이터를 OpenAI 파인튜닝 형식으로 변환
    MFCC 음성 특징 포함

    Args:
        csv_path: 피드백 CSV 파일 (음성 특징 포함)
        output_path: 출력 JSONL 파일
        include_audio_features: 음성 특징 포함 여부
    """

    df = pd.read_csv(csv_path)

    training_data = []

    print(f"📊 CSV 파일 로딩: {csv_path}")
    print(f"총 샘플 수: {len(df)}\n")

    # 음성 특징 컬럼 확인
    has_audio_features = 'audio_summary' in df.columns
    if include_audio_features and not has_audio_features:
        print("⚠️  음성 특징이 CSV에 없습니다.")
        print("먼저 extract_audio_features.py를 실행하세요.\n")
        include_audio_features = False

    for idx, row in df.iterrows():
        # 학생 답변 텍스트
        transcript = row['텍스트']

        # 교사 피드백 (발음/유창성은 텍스트 피드백)
        pronunciation_feedback = row.get('발음', '')
        fluency_feedback = row.get('fluency', '')

        # 실제 평가 점수 및 피드백
        content_score = row.get('내용', '')
        grammar_score = row.get('문법/표현', '')
        total_score = row.get('total_score', 0)
        feedback = row.get('텍스트 피드백', '')

        # 시스템 프롬프트
        system_message = """당신은 TOEFL 스피킹 평가 전문가입니다.

다음 정보를 받아 학생의 답변을 평가합니다:
1. 학생의 답변 텍스트
2. 음성 특징 분석 (MFCC, Pitch, Energy, 휴지, 말하기 속도 등)

아래 항목을 평가하세요:
- 내용 (Content): 질문 적합성, 논리적 구조, 구체성
- 문법/표현 (Grammar): 문법 정확성, 어휘 다양성
- 발음 (Pronunciation): 음소 정확성, 억양, 강세
- 유창성 (Fluency): 말하기 속도, 휴지 패턴, 자연스러움

각 항목을 0-4점으로 평가하고, 음성 특징을 참고하여 구체적인 피드백을 제공하세요."""

        # 사용자 입력 구성
        user_message = f"""학생 답변:
{transcript}
"""

        # 음성 특징 추가 (있는 경우)
        if include_audio_features and has_audio_features:
            audio_summary = row.get('audio_summary', '')
            if pd.notna(audio_summary):
                user_message += f"\n{audio_summary}\n"

        user_message += "\n위 정보를 참고하여 학생의 답변을 평가해주세요."

        # 모델 응답 (Ground Truth)
        assistant_message = f"""평가 결과:

**내용 (Content): {content_score}/4.0**
- 질문에 대한 적절한 답변 제시
- 논리적 구조와 전개

**문법/표현 (Grammar): {grammar_score}/4.0**
- 문법적 정확성
- 어휘 사용 및 다양성

**발음 (Pronunciation):**
{pronunciation_feedback}

**유창성 (Fluency):**
{fluency_feedback}

**종합 점수: {total_score}/4.0**

**피드백:**
{feedback}
"""

        # 음성 특징 기반 피드백 추가
        if include_audio_features and has_audio_features:
            additional_feedback = []

            # 말하기 속도
            if pd.notna(row.get('speech_rate')):
                speech_rate = float(row['speech_rate'])
                if speech_rate < 2:
                    additional_feedback.append("- 말하기 속도 개선: 휴지를 줄이고 자연스럽게 말하세요")
                elif speech_rate > 5:
                    additional_feedback.append("- 말하기 속도 조절: 너무 빠르면 명확성이 떨어집니다")

            # 휴지
            if pd.notna(row.get('pause_mean')):
                pause_mean = float(row['pause_mean'])
                if pause_mean > 1.0:
                    additional_feedback.append("- 휴지 개선: 긴 멈춤을 줄이고 유창성을 높이세요")

            # Pitch 변동
            if pd.notna(row.get('pitch_std')):
                pitch_std = float(row['pitch_std'])
                if pitch_std < 20:
                    additional_feedback.append("- 억양 개선: 더 풍부한 억양으로 표현력을 높이세요")

            if additional_feedback:
                assistant_message += "\n**음성 특징 기반 개선 방향:**\n" + "\n".join(additional_feedback)


        # OpenAI 형식
        training_example = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message}
            ]
        }

        training_data.append(training_example)

    # JSONL로 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in training_data:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"✅ {len(training_data)}개의 학습 데이터 생성 완료")
    print(f"💾 저장 위치: {output_path}\n")

    # 통계
    print("📊 데이터 통계:")
    print(f"- 총 샘플: {len(training_data)}개")

    avg_length = sum(len(d['messages'][1]['content']) for d in training_data) / len(training_data)
    print(f"- 평균 입력 길이: {avg_length:.0f} 자")

    if include_audio_features and has_audio_features:
        print(f"- 음성 특징: ✅ 포함됨")
    else:
        print(f"- 음성 특징: ❌ 미포함")

    print()

    if len(training_data) < 50:
        print(f"⚠️  권장 샘플 수: 50개 이상 (현재: {len(training_data)}개)")
        print(f"   OpenAI 파인튜닝은 최소 10개부터 가능하지만, 50개 이상 권장합니다.")
    else:
        print(f"✅ 충분한 데이터: OpenAI 파인튜닝 가능")

    return training_data


def validate_training_data(jsonl_path: str):
    """OpenAI 형식 검증"""

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    print(f"\n🔍 데이터 검증:")

    errors = []
    for idx, item in enumerate(data):
        if 'messages' not in item:
            errors.append(f"샘플 {idx}: 'messages' 키 없음")
            continue

        messages = item['messages']

        if len(messages) != 3:
            errors.append(f"샘플 {idx}: 메시지 개수는 3개여야 함 (현재: {len(messages)})")

        expected_roles = ['system', 'user', 'assistant']
        actual_roles = [msg.get('role') for msg in messages]
        if actual_roles != expected_roles:
            errors.append(f"샘플 {idx}: role 순서 오류")

    if errors:
        print("❌ 검증 실패:")
        for error in errors[:5]:
            print(f"   - {error}")
        if len(errors) > 5:
            print(f"   ... 외 {len(errors)-5}개")
    else:
        print("✅ 모든 데이터가 OpenAI 형식에 맞습니다")

    # 토큰 수 추정
    total_chars = sum(
        sum(len(msg['content']) for msg in item['messages'])
        for item in data
    )
    estimated_tokens = total_chars // 4

    print(f"\n📈 토큰 추정:")
    print(f"- 총 문자 수: {total_chars:,}")
    print(f"- 추정 토큰 수: {estimated_tokens:,}")
    print(f"- 평균 토큰/샘플: {estimated_tokens//len(data):,}")

    # 비용 추정
    training_cost = estimated_tokens / 1000 * 0.008
    print(f"\n💰 예상 파인튜닝 비용 (GPT-3.5-turbo):")
    print(f"- 학습 비용: ${training_cost:.2f}")
    print(f"- 추론 비용 (1000회): ~$10-20")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='OpenAI 파인튜닝 데이터 준비')
    parser.add_argument('--csv', type=str, required=True,
                        help='피드백 CSV 파일 (음성 특징 포함)')
    parser.add_argument('--output', type=str, default='openai_training_data.jsonl',
                        help='출력 JSONL 파일')
    parser.add_argument('--no_audio_features', action='store_true',
                        help='음성 특징 제외')

    args = parser.parse_args()

    if not Path(args.csv).exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {args.csv}")
        exit(1)

    # 데이터 생성
    training_data = create_openai_training_data(
        csv_path=args.csv,
        output_path=args.output,
        include_audio_features=not args.no_audio_features
    )

    # 검증
    validate_training_data(args.output)

    print("\n" + "="*60)
    print("다음 단계:")
    print("="*60)
    print(f"1. OpenAI 파인튜닝 실행:")
    print(f"   openai api fine_tunes.create -t {args.output} -m gpt-3.5-turbo")
    print(f"\n2. 또는 웹 인터페이스:")
    print(f"   https://platform.openai.com/finetune")
    print(f"   파일 업로드: {args.output}")
    print("="*60)
