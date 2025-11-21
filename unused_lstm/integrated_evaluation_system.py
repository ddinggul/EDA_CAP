"""
통합 TOEFL 스피킹 평가 시스템
음성 분석 모델 + LLM 결합
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, Optional

# 음성 처리
from audio_feature_extraction import AudioFeatureExtractor
from train_audio_model import predict_audio_scores

# LLM (MLX or OpenAI)
try:
    from mlx_lm import load, generate
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class IntegratedTOEFLEvaluator:
    """
    음성 분석 + LLM 통합 평가 시스템
    """

    def __init__(
        self,
        audio_model_dir: str = "./audio_model",
        llm_type: str = "mlx",  # "mlx" or "openai"
        llm_model: str = "mlx-community/Mistral-7B-Instruct-v0.2-4bit",
        llm_adapter_path: Optional[str] = "./toefl_finetuned_mlx",
        openai_api_key: Optional[str] = None
    ):
        """
        Args:
            audio_model_dir: 음성 분석 모델 디렉토리
            llm_type: LLM 종류 ("mlx" or "openai")
            llm_model: LLM 모델 이름
            llm_adapter_path: MLX 어댑터 경로
            openai_api_key: OpenAI API 키
        """

        # 음성 특징 추출기
        self.audio_extractor = AudioFeatureExtractor()
        self.audio_model_dir = audio_model_dir

        # LLM 설정
        self.llm_type = llm_type

        if llm_type == "mlx":
            if not MLX_AVAILABLE:
                raise ImportError("MLX가 설치되지 않았습니다: pip install mlx mlx-lm")

            print(f"📥 MLX 모델 로딩: {llm_model}")
            if llm_adapter_path and Path(llm_adapter_path).exists():
                self.model, self.tokenizer = load(llm_model, adapter_path=llm_adapter_path)
                print(f"   ✅ 파인튜닝 모델 로드 완료")
            else:
                self.model, self.tokenizer = load(llm_model)
                print(f"   ✅ 베이스 모델 로드 완료")

        elif llm_type == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI가 설치되지 않았습니다: pip install openai")

            if openai_api_key:
                openai.api_key = openai_api_key
            self.llm_model = llm_model
            print(f"✅ OpenAI 모델 준비: {llm_model}")

        print("✅ 통합 평가 시스템 초기화 완료\n")

    def evaluate_audio(self, audio_path: str) -> Dict:
        """
        음성 파일 평가 (발음, 유창성)

        Returns:
            {
                'pronunciation': float,
                'fluency': float,
                'audio_features': dict
            }
        """

        print(f"🎤 음성 분석 중: {Path(audio_path).name}")

        # 음성 특징 추출
        audio_features = self.audio_extractor.extract_all_features(audio_path)

        # 특징 벡터 생성
        feature_vector = []
        for key, value in audio_features.items():
            if isinstance(value, list):
                feature_vector.extend(value)
            elif isinstance(value, (int, float)):
                feature_vector.append(value)

        feature_array = np.array(feature_vector)

        # 음성 모델로 점수 예측
        scores = predict_audio_scores(
            feature_array,
            model_dir=self.audio_model_dir
        )

        print(f"   발음: {scores['pronunciation']:.2f}/4.0")
        print(f"   유창성: {scores['fluency']:.2f}/4.0")

        return {
            'pronunciation': scores['pronunciation'],
            'fluency': scores['fluency'],
            'audio_features': audio_features
        }

    def evaluate_content(
        self,
        transcript: str,
        audio_scores: Dict,
        max_tokens: int = 500
    ) -> str:
        """
        LLM으로 내용/문법 평가

        Args:
            transcript: 발화 텍스트
            audio_scores: 음성 평가 결과
            max_tokens: 최대 토큰 수

        Returns:
            평가 결과 텍스트
        """

        print(f"📝 내용/문법 평가 중...")

        # 프롬프트 구성
        prompt = f"""<|system|>
당신은 TOEFL 스피킹 평가 전문가입니다.

음성 분석 결과:
- 발음 점수: {audio_scores['pronunciation']:.2f}/4.0
- 유창성 점수: {audio_scores['fluency']:.2f}/4.0

위 음성 분석 결과를 참고하여, 아래 학생의 답변 텍스트를 평가하세요:
1. 내용 (Content): 질문 적합성, 논리적 구조, 구체적 예시
2. 문법/표현 (Grammar): 문법 정확성, 어휘 다양성

각 항목에 대한 구체적 피드백과 점수(0-4점)를 제공하세요.
<|user|>
학생의 답변:

{transcript}
<|assistant|>
"""

        # LLM 실행
        if self.llm_type == "mlx":
            response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                temp=0.7
            )
        elif self.llm_type == "openai":
            response = openai.ChatCompletion.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "당신은 TOEFL 평가 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            response = response.choices[0].message.content

        return response

    def evaluate_complete(
        self,
        audio_path: str,
        transcript: Optional[str] = None,
        use_whisper: bool = False
    ) -> Dict:
        """
        완전 통합 평가 (음성 + 텍스트)

        Args:
            audio_path: 음성 파일 경로
            transcript: 발화 텍스트 (없으면 Whisper로 자동 인식)
            use_whisper: Whisper로 자동 전사 여부

        Returns:
            종합 평가 결과
        """

        print("=" * 60)
        print("🎓 TOEFL 스피킹 통합 평가")
        print("=" * 60)
        print()

        # 1. 음성 평가
        audio_result = self.evaluate_audio(audio_path)
        print()

        # 2. 텍스트 준비
        if transcript is None and use_whisper:
            print("🎙️  Whisper로 음성 인식 중...")
            transcript = self.transcribe_with_whisper(audio_path)
            print(f"   인식 결과: {transcript[:100]}...")
            print()
        elif transcript is None:
            raise ValueError("transcript를 제공하거나 use_whisper=True로 설정하세요.")

        # 3. 내용/문법 평가
        content_result = self.evaluate_content(transcript, audio_result)
        print()

        # 4. 종합 결과
        result = {
            'audio_file': Path(audio_path).name,
            'transcript': transcript,
            'pronunciation_score': audio_result['pronunciation'],
            'fluency_score': audio_result['fluency'],
            'content_evaluation': content_result,
            'audio_features': audio_result['audio_features']
        }

        print("=" * 60)
        print("📊 평가 완료")
        print("=" * 60)
        print(f"발음: {result['pronunciation_score']:.2f}/4.0")
        print(f"유창성: {result['fluency_score']:.2f}/4.0")
        print()
        print("상세 평가:")
        print(content_result)
        print("=" * 60)

        return result

    def transcribe_with_whisper(self, audio_path: str) -> str:
        """Whisper로 음성 인식"""
        try:
            import whisper
        except ImportError:
            raise ImportError("Whisper가 설치되지 않았습니다: pip install openai-whisper")

        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]

    def batch_evaluate(
        self,
        audio_dir: str,
        csv_path: str,
        output_path: str = "evaluation_results.jsonl"
    ):
        """여러 음성 파일 일괄 평가"""

        import pandas as pd

        df = pd.read_csv(csv_path)
        audio_files = list(Path(audio_dir).glob("*.wav"))

        results = []

        for i, audio_file in enumerate(audio_files):
            print(f"\n[{i+1}/{len(audio_files)}] 평가 중...")

            # CSV에서 대본 찾기
            file_id = audio_file.stem
            matching_row = df[df['파일 이름'].str.contains(file_id, na=False)]

            if not matching_row.empty:
                transcript = matching_row.iloc[0].get('텍스트', '')

                try:
                    result = self.evaluate_complete(
                        str(audio_file),
                        transcript=transcript
                    )
                    results.append(result)
                except Exception as e:
                    print(f"❌ 오류: {e}")
                    continue

        # 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

        print(f"\n✅ 일괄 평가 완료: {len(results)}개 파일")
        print(f"💾 저장: {output_path}")

        return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='통합 TOEFL 평가 시스템')
    parser.add_argument('--audio', type=str,
                        help='평가할 음성 파일')
    parser.add_argument('--transcript', type=str,
                        help='발화 텍스트 (선택)')
    parser.add_argument('--audio_model', type=str, default='./audio_model',
                        help='음성 모델 디렉토리')
    parser.add_argument('--llm_type', type=str, default='mlx',
                        choices=['mlx', 'openai'],
                        help='LLM 종류')
    parser.add_argument('--llm_model', type=str,
                        default='mlx-community/Mistral-7B-Instruct-v0.2-4bit',
                        help='LLM 모델')
    parser.add_argument('--adapter', type=str, default='./toefl_finetuned_mlx',
                        help='MLX 어댑터 경로')
    parser.add_argument('--use_whisper', action='store_true',
                        help='Whisper로 자동 전사')

    # 일괄 평가 옵션
    parser.add_argument('--batch', action='store_true',
                        help='일괄 평가 모드')
    parser.add_argument('--audio_dir', type=str,
                        help='음성 파일 디렉토리 (일괄 평가)')
    parser.add_argument('--csv', type=str,
                        help='CSV 파일 (일괄 평가)')

    args = parser.parse_args()

    # 시스템 초기화
    evaluator = IntegratedTOEFLEvaluator(
        audio_model_dir=args.audio_model,
        llm_type=args.llm_type,
        llm_model=args.llm_model,
        llm_adapter_path=args.adapter
    )

    if args.batch:
        # 일괄 평가
        if not args.audio_dir or not args.csv:
            print("❌ --audio_dir와 --csv를 지정하세요.")
        else:
            evaluator.batch_evaluate(args.audio_dir, args.csv)
    else:
        # 단일 평가
        if not args.audio:
            print("❌ --audio를 지정하세요.")
        else:
            result = evaluator.evaluate_complete(
                args.audio,
                transcript=args.transcript,
                use_whisper=args.use_whisper
            )

            # 결과 저장
            output_file = f"result_{Path(args.audio).stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"\n💾 결과 저장: {output_file}")
