# CLOVA Speech 단문 인식 API 상세 가이드

## 개요

CLOVA Speech 단문 인식 API는 60초 이내의 짧은 음성을 텍스트로 변환하고, 동시에 발음 평가를 수행할 수 있는 API입니다.

## 주요 특징

- ✅ **60초 이내 음성 최적화**: 짧은 발화에 특화된 빠른 처리
- ✅ **발음 평가 기능**: `nbestScoreLangEval` 파라미터로 발음 점수 제공
- ✅ **다국어 지원**: 영어, 한국어, 일본어, 중국어
- ✅ **실시간 처리**: 동기 방식으로 즉시 결과 반환

## API 스펙

### Endpoint

```
POST https://clovaspeech-gw.ncloud.com/recog/v1/stt
```

**Beta 환경:**
```
POST https://beta-clovaspeech-gw.ncloud.com/recog/v1/stt
```

### 요청 헤더

| 헤더 | 필수 | 설명 |
|------|------|------|
| `X-CLOVASPEECH-API-KEY` | 필수 | CLOVA Speech Secret Key |
| `Content-Type` | 필수 | `application/octet-stream` |

### 쿼리 파라미터

| 파라미터 | 필수 | 설명 | 기본값 | 예시 |
|----------|------|------|--------|------|
| `lang` | 필수 | 언어 코드 | - | `Eng`, `Kor`, `Jpn`, `Chn` |
| `nbestScoreLangEval` | 선택 | 발음 평가 활성화 | `false` | `true` |

### 요청 Body

오디오 파일의 바이너리 데이터

**지원 포맷:**
- WAV (PCM)
- MP3
- OGG
- FLAC
- AMR

**제약사항:**
- 최대 파일 크기: 10MB
- 최대 길이: 60초
- 권장 샘플링 레이트: 16kHz 또는 8kHz

## 응답 형식

### 기본 응답 (nbestScoreLangEval=false)

```json
{
  "text": "Hello world",
  "confidence": 0.95,
  "words": [
    {
      "text": "Hello",
      "confidence": 0.98,
      "start": 0,
      "end": 500
    },
    {
      "text": "world",
      "confidence": 0.92,
      "start": 500,
      "end": 1000
    }
  ]
}
```

### 발음 평가 포함 응답 (nbestScoreLangEval=true)

```json
{
  "text": "Hello world",
  "confidence": 0.95,
  "pronunciationScore": 85.5,
  "fluencyScore": 80.0,
  "completenessScore": 90.0,
  "prosodyScore": 75.0,
  "words": [
    {
      "text": "Hello",
      "confidence": 0.98,
      "pronunciationScore": 90,
      "start": 0,
      "end": 500
    },
    {
      "text": "world",
      "confidence": 0.92,
      "pronunciationScore": 81,
      "start": 500,
      "end": 1000
    }
  ]
}
```

**발음 평가 필드 설명:**

| 필드 | 설명 | 범위 |
|------|------|------|
| `pronunciationScore` | 전체 발음 정확도 | 0-100 |
| `fluencyScore` | 유창성 점수 | 0-100 |
| `completenessScore` | 완성도 (발화 완료 정도) | 0-100 |
| `prosodyScore` | 운율 점수 (억양, 강세 등) | 0-100 |

## Python 예제 코드

### 기본 사용

```python
import httpx

async def transcribe_audio(audio_file_path: str, secret_key: str):
    url = "https://clovaspeech-gw.ncloud.com/recog/v1/stt"

    headers = {
        "X-CLOVASPEECH-API-KEY": secret_key,
        "Content-Type": "application/octet-stream"
    }

    params = {
        "lang": "Eng"
    }

    with open(audio_file_path, "rb") as f:
        audio_data = f.read()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=headers,
            params=params,
            content=audio_data
        )

        result = response.json()
        return result
```

### 발음 평가 포함

```python
async def transcribe_with_pronunciation(audio_file_path: str, secret_key: str):
    url = "https://clovaspeech-gw.ncloud.com/recog/v1/stt"

    headers = {
        "X-CLOVASPEECH-API-KEY": secret_key,
        "Content-Type": "application/octet-stream"
    }

    params = {
        "lang": "Eng",
        "nbestScoreLangEval": "true"  # 발음 평가 활성화
    }

    with open(audio_file_path, "rb") as f:
        audio_data = f.read()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=headers,
            params=params,
            content=audio_data
        )

        result = response.json()

        # 결과 파싱
        text = result.get("text", "")
        pronunciation_score = result.get("pronunciationScore", 0)
        fluency_score = result.get("fluencyScore", 0)

        return {
            "text": text,
            "pronunciation": pronunciation_score,
            "fluency": fluency_score
        }
```

## cURL 예제

```bash
curl -X POST "https://clovaspeech-gw.ncloud.com/recog/v1/stt?lang=Eng&nbestScoreLangEval=true" \
  -H "X-CLOVASPEECH-API-KEY: your_secret_key_here" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@audio.wav"
```

## TOEFL Speaking 적용 시 권장사항

### 1. 언어 설정

```python
params = {
    "lang": "Eng",  # TOEFL은 영어이므로 Eng 사용
    "nbestScoreLangEval": "true"
}
```

### 2. 오디오 전처리

TOEFL 답변은 보통 45~60초이므로:
- 녹음 시간 제한: 60초
- 샘플링 레이트: 16kHz 권장
- 모노 채널 사용

```python
# ffmpeg로 전처리
ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav
```

### 3. 발음 점수 해석

CLOVA Speech 발음 점수와 TOEFL 점수 매핑 예시:

| CLOVA 점수 | TOEFL 발음 점수 (0-4) |
|------------|----------------------|
| 90-100 | 4 (Excellent) |
| 75-89 | 3 (Good) |
| 60-74 | 2 (Fair) |
| 40-59 | 1 (Limited) |
| 0-39 | 0 (Poor) |

### 4. 에러 처리

```python
try:
    response = await client.post(url, ...)
    response.raise_for_status()
    result = response.json()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 400:
        # 잘못된 요청 (파일 형식, 크기 등)
        print("Invalid request")
    elif e.response.status_code == 401:
        # 인증 실패
        print("Invalid API key")
    elif e.response.status_code == 413:
        # 파일 크기 초과
        print("File too large")
    else:
        print(f"Error: {e.response.status_code}")
```

## 제한사항 및 주의사항

### 1. API 사용량 제한

- 무료 티어: 월 1,000건
- 유료 플랜: 사용량에 따라 과금
- Rate Limit: 초당 10건 (변경 가능)

### 2. 발음 평가 지원 언어

`nbestScoreLangEval` 기능은 **영어(Eng)에서만 정확도가 높습니다.**
- 한국어, 일본어, 중국어는 제한적 지원 또는 미지원

### 3. 음성 품질

발음 평가 정확도는 음성 품질에 크게 영향받습니다:
- ✅ 권장: 조용한 환경, 명확한 발화
- ❌ 비권장: 배경 소음, 불명확한 발화

### 4. 60초 제한

60초를 초과하는 음성은:
- 단문 인식 API 사용 불가
- CLOVA Speech 객체 스토리지 연동 API 사용 (별도 설정 필요)

## 트러블슈팅

### 문제: 발음 점수가 항상 0으로 반환됨

**원인:**
- `nbestScoreLangEval` 파라미터 미설정 또는 오타
- 언어가 영어가 아님
- API 버전 문제

**해결:**
```python
# 올바른 설정
params = {
    "lang": "Eng",
    "nbestScoreLangEval": "true"  # 문자열 "true"
}
```

### 문제: 401 Unauthorized

**원인:**
- Secret Key 오류
- 헤더 이름 오타

**해결:**
```python
headers = {
    "X-CLOVASPEECH-API-KEY": secret_key,  # 정확한 헤더 이름
    "Content-Type": "application/octet-stream"
}
```

### 문제: 400 Bad Request

**원인:**
- 지원하지 않는 오디오 형식
- 파일 크기 초과
- 빈 파일

**해결:**
- WAV, MP3 등 지원 형식으로 변환
- 60초 이내로 자르기
- 파일 크기 확인 (10MB 이하)

## 참고 자료

- [CLOVA Speech 공식 문서](https://api.ncloud-docs.com/docs/ai-application-service-clovaspeech-shortsentence)
- [Naver Cloud Platform 콘솔](https://console.ncloud.com/)
- [CLOVA Speech 가격 정책](https://www.ncloud.com/charge/price)

## 실제 프로젝트 적용 예시

본 TOEFL Speaking AI 프로젝트에서는:

1. **음성 업로드/녹음** → `backend/app/routers/speech.py`
2. **CLOVA Speech API 호출** → `backend/app/services/clova_stt.py`
3. **발음 점수 파싱** → `_parse_pronunciation_result()`
4. **OpenAI 종합 평가** → `backend/app/services/openai_eval.py`
5. **결과 반환** → 프론트엔드 렌더링

```python
# speech.py
stt_result, pron_result = await transcribe_with_pronunciation_eval(
    wav_file_path,
    language="Eng"
)

# OpenAI에 발음 점수 전달
pron_scores = {
    "overall": pron_result.overall,
    "fluency": pron_result.fluency
}
eval_result = await evaluate_speaking(task_id, stt_result.text, pron_scores)
```

---

**업데이트:** 2025년 1월 기준

실제 API 스펙은 네이버 클라우드 공식 문서를 참조하세요.
