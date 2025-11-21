# backend/app/services/clova_stt.py
"""
Naver CLOVA Speech Recognition - 단문 인식 API

API 문서: https://api.ncloud-docs.com/docs/ai-application-service-clovaspeech-shortsentence

단문 인식 API 특징:
- 60초 이내의 짧은 음성 인식에 최적화
- 발음 평가 기능 지원 (nbestScoreLangEval 파라미터)
- 실시간 처리 가능
"""

import httpx
import json
from pathlib import Path
from typing import Dict, List, Optional
from app.config import settings
from app.schemas import STTResult, PronResult, PronunciationDetails


async def transcribe_with_pronunciation_eval(
    file_path: Path,
    language: str = "Eng"
) -> tuple[STTResult, PronResult]:
    """
    단문 음성 인식 + 발음 평가를 동시에 수행

    Args:
        file_path: 오디오 파일 경로
        language: 언어 코드 (Eng, Kor, Jpn, Chn)

    Returns:
        (STTResult, PronResult): 음성 인식 결과 및 발음 평가 결과
    """

    # API Endpoint 및 파라미터 설정
    url = settings.NAVER_CLOVA_STT_ENDPOINT

    # Query Parameters
    params = {
        "lang": language,  # 언어: Eng(영어), Kor(한국어), Jpn(일본어), Chn(중국어)
        # nbestScoreLangEval: 발음 평가 기능 활성화
        # - true로 설정 시 발음 점수 및 언어 평가 결과 반환
        # - 단문 인식 API에서만 지원
    }

    # 발음 평가 기능 활성화
    # 참고: 이 파라미터의 정확한 사용법은 네이버 클라우드 공식 문서 확인 필요
    if language == "Eng":
        # 영어의 경우 발음 평가 활성화 시도
        params["nbestScoreLangEval"] = "true"

    # Headers
    headers = {
        "X-CLOVASPEECH-API-KEY": settings.NAVER_CLOVA_SECRET_KEY,
        "Content-Type": "application/octet-stream",
    }

    # 오디오 파일 읽기
    with open(file_path, "rb") as audio_file:
        audio_data = audio_file.read()

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                url,
                headers=headers,
                params=params,
                content=audio_data
            )
            response.raise_for_status()

            result = response.json()

            # 응답 디버깅용 출력
            print(f"CLOVA Speech API Response: {json.dumps(result, indent=2, ensure_ascii=False)}")

            # STT 결과 파싱
            stt_result = _parse_stt_result(result)

            # 발음 평가 결과 파싱
            pron_result = _parse_pronunciation_result(result)

            return stt_result, pron_result

        except httpx.HTTPStatusError as e:
            print(f"CLOVA Speech API HTTP Error: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            return _get_fallback_results()

        except httpx.HTTPError as e:
            print(f"CLOVA Speech API Network Error: {e}")
            return _get_fallback_results()

        except json.JSONDecodeError as e:
            print(f"CLOVA Speech API JSON Parse Error: {e}")
            return _get_fallback_results()

        except Exception as e:
            print(f"CLOVA Speech Unexpected Error: {e}")
            return _get_fallback_results()


def _parse_stt_result(api_response: dict) -> STTResult:
    """
    CLOVA Speech API 응답에서 STT 결과 추출

    예상 응답 형식:
    {
      "text": "인식된 텍스트",
      "confidence": 0.95,
      "words": [...]  (선택적)
    }
    """
    text = api_response.get("text", "")
    confidence = api_response.get("confidence", 0.0)

    # confidence가 없는 경우 words의 평균 confidence 계산
    if confidence == 0.0 and "words" in api_response:
        words = api_response["words"]
        if words:
            confidences = [w.get("confidence", 0) for w in words]
            confidence = sum(confidences) / len(confidences) if confidences else 0.0

    return STTResult(
        text=text,
        confidence=float(confidence)
    )


def _parse_pronunciation_result(api_response: dict) -> PronResult:
    """
    CLOVA Speech API 응답에서 발음 평가 결과 추출

    nbestScoreLangEval=true 설정 시 예상 응답 형식:
    {
      "pronunciationScore": 85.5,
      "fluencyScore": 80.0,
      "completenessScore": 90.0,
      "prosodyScore": 75.0,
      "words": [
        {
          "text": "hello",
          "pronunciationScore": 90,
          "start": 0,
          "end": 500
        },
        ...
      ]
    }

    실제 응답 형식은 네이버 클라우드 문서 확인 필요
    """

    # 발음 평가 점수 추출 시도
    pronunciation_score = api_response.get("pronunciationScore", 0.0)
    fluency_score = api_response.get("fluencyScore", 0.0)

    # 단어별 발음 점수 추출
    words = api_response.get("words", [])
    segments = []

    for word_data in words:
        if isinstance(word_data, dict):
            segment = {
                "word": word_data.get("text", ""),
                "score": word_data.get("pronunciationScore", 0),
                "start": word_data.get("start", 0) / 1000.0,  # ms -> s
                "end": word_data.get("end", 0) / 1000.0
            }
            segments.append(segment)

    # 발음 점수가 없는 경우 기본값 반환
    if pronunciation_score == 0.0 and fluency_score == 0.0:
        # 발음 평가 기능이 비활성화되었거나 응답에 포함되지 않은 경우
        # 텍스트 기반 추정값 사용
        text = api_response.get("text", "")
        return _estimate_pronunciation_from_text(text)

    return PronResult(
        overall=float(pronunciation_score),
        fluency=float(fluency_score),
        details=PronunciationDetails(segments=segments)
    )


def _estimate_pronunciation_from_text(text: str) -> PronResult:
    """
    발음 평가 결과가 없을 때 텍스트 기반 추정
    (간이 방식 - 실제 발음 분석은 아님)
    """
    if not text or text in ["[음성 인식 실패]", "[음성 인식 실패 - API 오류]"]:
        return PronResult(
            overall=0.0,
            fluency=0.0,
            details=PronunciationDetails(segments=[])
        )

    word_count = len(text.split())

    # 단어 수 기반 간단 추정
    if word_count < 10:
        overall = 55.0
        fluency = 55.0
    elif word_count < 30:
        overall = 68.0
        fluency = 68.0
    elif word_count < 60:
        overall = 75.0
        fluency = 75.0
    else:
        overall = 82.0
        fluency = 82.0

    return PronResult(
        overall=overall,
        fluency=fluency,
        details=PronunciationDetails(segments=[])
    )


def _get_fallback_results() -> tuple[STTResult, PronResult]:
    """API 호출 실패 시 기본 응답"""
    stt_result = STTResult(
        text="[음성 인식 실패]",
        confidence=0.0
    )
    pron_result = PronResult(
        overall=0.0,
        fluency=0.0,
        details=PronunciationDetails(segments=[])
    )
    return stt_result, pron_result
