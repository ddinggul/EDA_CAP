"""
TOEFL 스피킹 평가 시스템
Clova STT + 발음평가 → 파인튜닝된 OpenAI GPT
"""

import os
import requests
import openai
from pathlib import Path
from typing import Dict, Optional
import json


class TOEFLEvaluator:
    """
    TOEFL 스피킹 통합 평가 시스템

    1. Clova API로 음성인식 + 발음평가
    2. 파인튜닝된 OpenAI GPT로 내용/문법 평가
    """

    def __init__(
        self,
        clova_secret_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        finetuned_model: Optional[str] = None
    ):
        """
        Args:
            clova_secret_key: Naver Clova Speech API 키
            openai_api_key: OpenAI API 키
            finetuned_model: 파인튜닝된 모델 ID (예: ft:gpt-3.5-turbo:...)
        """

        # Clova API 설정
        self.clova_secret_key = clova_secret_key or os.getenv('NAVER_CLOVA_SECRET_KEY')
        self.clova_endpoint = "https://clovaspeech-gw.ncloud.com/recog/v1/stt"

        if not self.clova_secret_key:
            raise ValueError("Clova API 키가 필요합니다")

        # OpenAI 설정
        openai.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.finetuned_model = finetuned_model or os.getenv('OPENAI_FINETUNED_MODEL') or 'gpt-3.5-turbo'

        if not openai.api_key:
            raise ValueError("OpenAI API 키가 필요합니다")

        print("✅ TOEFL 평가 시스템 초기화 완료")
        print(f"   Clova API: {'설정됨' if self.clova_secret_key else '❌'}")
        print(f"   OpenAI 모델: {self.finetuned_model}")
        print()

    def analyze_speech_with_clova(self, audio_path: str) -> Dict:
        """
        Clova Speech API로 음성인식 + 발음평가

        Args:
            audio_path: 음성 파일 경로 (WAV, MP3 등)

        Returns:
            {
                'text': str,  # 음성인식 결과
                'pronunciation_score': float,  # 발음 점수 (0-100)
                'fluency_score': float,  # 유창성 점수 (0-100)
                'confidence': float  # 인식 신뢰도
            }
        """

        print(f"🎤 Clova API 분석 중: {Path(audio_path).name}")

        # 음성 파일 읽기
        with open(audio_path, 'rb') as f:
            audio_data = f.read()

        # API 호출
        headers = {
            'X-CLOVASPEECH-API-KEY': self.clova_secret_key,
            'Content-Type': 'application/octet-stream'
        }

        params = {
            'lang': 'Eng',  # 영어
            'nbestScoreLangEval': 'true'  # 발음평가 활성화
        }

        try:
            response = requests.post(
                self.clova_endpoint,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            # 결과 파싱
            transcript = result.get('text', '')
            confidence = result.get('confidence', 0)

            # 발음 점수 (Clova API 응답 구조에 따라 조정 필요)
            pronunciation_score = result.get('pronunciationScore', 0)
            fluency_score = result.get('fluencyScore', 0)

            print(f"   ✅ 음성인식 완료")
            print(f"   텍스트: {transcript[:50]}...")
            print(f"   발음: {pronunciation_score:.1f}/100")
            print(f"   유창성: {fluency_score:.1f}/100")
            print()

            return {
                'text': transcript,
                'pronunciation_score': pronunciation_score,
                'fluency_score': fluency_score,
                'confidence': confidence
            }

        except requests.exceptions.RequestException as e:
            print(f"❌ Clova API 오류: {e}")
            raise

    def evaluate_with_gpt(
        self,
        transcript: str,
        pronunciation_score: float,
        fluency_score: float
    ) -> Dict:
        """
        파인튜닝된 GPT로 내용/문법 평가

        Args:
            transcript: 음성인식 텍스트
            pronunciation_score: 발음 점수
            fluency_score: 유창성 점수

        Returns:
            {
                'content_score': float,
                'grammar_score': float,
                'total_score': float,
                'feedback': str,
                'tips': list
            }
        """

        print(f"🤖 GPT 평가 중...")

        # 시스템 프롬프트
        system_message = """당신은 TOEFL 스피킹 평가 전문가입니다.

학생의 답변과 Clova API의 발음/유창성 분석 결과를 받아서, 다음을 평가합니다:
1. 내용 (Content): 질문 적합성, 논리적 구조, 구체성
2. 문법/표현 (Grammar): 문법 정확성, 어휘 다양성, 적절한 표현

발음과 유창성은 이미 분석되었으므로, 내용과 문법에 집중하세요.
각 항목을 0-4점으로 평가하고, 구체적인 피드백을 제공하세요."""

        # 사용자 메시지
        user_message = f"""학생 답변:
{transcript}

Clova API 발음 분석:
- 발음 점수: {pronunciation_score:.1f}/100
- 유창성 점수: {fluency_score:.1f}/100

위 정보를 참고하여 학생의 답변을 평가해주세요."""

        try:
            response = openai.ChatCompletion.create(
                model=self.finetuned_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )

            evaluation_text = response.choices[0].message.content

            print(f"   ✅ GPT 평가 완료")
            print()

            # 간단한 파싱 (실제로는 더 정교하게)
            return {
                'evaluation': evaluation_text,
                'raw_response': response
            }

        except Exception as e:
            print(f"❌ OpenAI API 오류: {e}")
            raise

    def evaluate_complete(self, audio_path: str, save_result: bool = True) -> Dict:
        """
        완전 통합 평가

        Args:
            audio_path: 음성 파일 경로
            save_result: 결과 저장 여부

        Returns:
            종합 평가 결과
        """

        print("=" * 60)
        print("🎓 TOEFL 스피킹 종합 평가")
        print("=" * 60)
        print()

        # 1. Clova API 분석
        clova_result = self.analyze_speech_with_clova(audio_path)

        # 2. GPT 평가
        gpt_result = self.evaluate_with_gpt(
            transcript=clova_result['text'],
            pronunciation_score=clova_result['pronunciation_score'],
            fluency_score=clova_result['fluency_score']
        )

        # 3. 결과 통합
        result = {
            'audio_file': Path(audio_path).name,
            'speech_recognition': {
                'text': clova_result['text'],
                'confidence': clova_result['confidence']
            },
            'pronunciation': {
                'score': clova_result['pronunciation_score'],
                'score_4point': clova_result['pronunciation_score'] / 25
            },
            'fluency': {
                'score': clova_result['fluency_score'],
                'score_4point': clova_result['fluency_score'] / 25
            },
            'gpt_evaluation': gpt_result['evaluation']
        }

        # 결과 출력
        print("=" * 60)
        print("📊 평가 완료")
        print("=" * 60)
        print(f"\n📝 음성인식 결과:")
        print(f"{clova_result['text']}\n")
        print(f"📊 점수:")
        print(f"   발음: {result['pronunciation']['score_4point']:.2f}/4.0")
        print(f"   유창성: {result['fluency']['score_4point']:.2f}/4.0")
        print(f"\n💬 GPT 평가:")
        print(gpt_result['evaluation'])
        print("=" * 60)

        # 결과 저장
        if save_result:
            output_file = f"result_{Path(audio_path).stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n💾 결과 저장: {output_file}")

        return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='TOEFL 스피킹 평가')
    parser.add_argument('--audio', type=str, required=True,
                        help='음성 파일 경로')
    parser.add_argument('--clova_key', type=str,
                        help='Clova API 키 (또는 환경변수 NAVER_CLOVA_SECRET_KEY)')
    parser.add_argument('--openai_key', type=str,
                        help='OpenAI API 키 (또는 환경변수 OPENAI_API_KEY)')
    parser.add_argument('--model', type=str,
                        help='파인튜닝된 모델 ID (또는 환경변수 OPENAI_FINETUNED_MODEL)')
    parser.add_argument('--no_save', action='store_true',
                        help='결과 파일 저장 안 함')

    args = parser.parse_args()

    if not Path(args.audio).exists():
        print(f"❌ 음성 파일을 찾을 수 없습니다: {args.audio}")
        exit(1)

    # 평가 시스템 초기화
    evaluator = TOEFLEvaluator(
        clova_secret_key=args.clova_key,
        openai_api_key=args.openai_key,
        finetuned_model=args.model
    )

    # 평가 실행
    result = evaluator.evaluate_complete(
        audio_path=args.audio,
        save_result=not args.no_save
    )
