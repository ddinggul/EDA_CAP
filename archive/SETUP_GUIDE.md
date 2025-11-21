# 상세 설정 가이드

## Naver CLOVA Speech Recognition API 설정

### 1. 네이버 클라우드 플랫폼 가입 및 서비스 신청

1. **회원가입**
   - https://www.ncloud.com/ 접속
   - 회원가입 (이메일 인증 필요)
   - 결제 정보 등록 (무료 크레딧 제공)

2. **CLOVA Speech 서비스 신청**
   - 콘솔 로그인
   - `AI·NAVER API` > `CLOVA Speech` 선택
   - `이용 신청하기` 클릭
   - 약관 동의 후 신청

3. **인증 정보 발급**
   - `서비스 관리` > `CLOVA Speech` 메뉴 이동
   - `Domain` 생성 (예: `toefl-speaking-ai`)
   - 생성된 도메인 클릭
   - 다음 정보 확인 및 복사:
     - **Client ID**
     - **Client Secret**
     - **Invoke URL**

### 2. .env 파일 설정

```bash
# backend/.env 파일 생성
cd backend
cp .env.example .env
```

`.env` 파일을 열어 다음과 같이 설정:

```env
# Naver CLOVA Speech
NAVER_CLOVA_CLIENT_ID=abcd1234efgh5678
NAVER_CLOVA_CLIENT_SECRET=ABCDabcd1234EFGHefgh5678
NAVER_CLOVA_INVOKE_URL=https://clovaspeech-gw.ncloud.com/external/v1/7392/xxxxxxxxxxxxxxxxxxxx

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL_NAME=gpt-4o-mini
```

### 3. API 응답 형식 확인 및 코드 수정

Naver CLOVA Speech API의 응답 형식은 공식 문서에 따라 다를 수 있습니다.

**예상 응답 형식 1 (단순 텍스트):**
```json
{
  "text": "Hello world"
}
```

**예상 응답 형식 2 (세그먼트 포함):**
```json
{
  "text": "Hello world",
  "segments": [
    {
      "start": 0,
      "end": 500,
      "text": "Hello",
      "confidence": 0.98
    },
    {
      "start": 500,
      "end": 1000,
      "text": "world",
      "confidence": 0.95
    }
  ]
}
```

`backend/app/services/naver_stt.py` 파일의 75-78번 줄을 실제 응답 형식에 맞게 수정:

```python
# 실제 API 테스트 후 응답 형식 확인하여 수정
transcribed_text = result.get("text", "")
confidence = result.get("confidence", 0.85)

# 또는 segments가 있는 경우
# segments = result.get("segments", [])
# if segments:
#     transcribed_text = " ".join([seg["text"] for seg in segments])
#     confidences = [seg.get("confidence", 0.85) for seg in segments]
#     confidence = sum(confidences) / len(confidences) if confidences else 0.85
```

### 4. 테스트

```bash
# 백엔드 실행
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

브라우저에서 http://localhost:8000/docs 접속하여 API 테스트

---

## OpenAI API 설정

### 1. OpenAI API 키 발급

1. https://platform.openai.com/ 접속
2. 로그인 또는 회원가입
3. `API keys` 메뉴 이동
4. `Create new secret key` 클릭
5. 키 이름 입력 후 생성
6. **생성된 키를 반드시 복사** (다시 볼 수 없음)

### 2. 사용량 및 과금 설정

1. `Settings` > `Billing` 이동
2. 결제 정보 등록
3. `Usage limits` 설정 권장 (예: 월 $10 제한)

### 3. Fine-tuned 모델 사용 (선택사항)

TOEFL Speaking 평가용 커스텀 모델을 만들려면:

1. **학습 데이터 준비** (JSONL 형식)
```jsonl
{"messages": [{"role": "system", "content": "You are a TOEFL examiner..."}, {"role": "user", "content": "Task 1: I think..."}, {"role": "assistant", "content": "{\"fluency\": 3, \"pronunciation\": 3, ...}"}]}
{"messages": [{"role": "system", "content": "You are a TOEFL examiner..."}, {"role": "user", "content": "Task 2: In my opinion..."}, {"role": "assistant", "content": "{\"fluency\": 4, \"pronunciation\": 3, ...}"}]}
```

2. **Fine-tuning 작업 생성**
```bash
openai api fine_tunes.create \
  -t training_data.jsonl \
  -m gpt-4o-mini \
  --suffix "toefl-eval"
```

3. **Fine-tuned 모델 ID 확인**
```bash
openai api fine_tunes.list
```

4. **.env 파일에 모델 ID 설정**
```env
OPENAI_MODEL_NAME=ft:gpt-4o-mini:my-org:toefl-eval:abc123
```

---

## 발음 평가 고도화 (선택사항)

현재 버전은 텍스트 기반 간단 추정만 제공합니다.

실제 음성 기반 발음 평가를 추가하려면:

### 옵션 1: 오픈소스 라이브러리 사용

**librosa + 음향 특징 분석**

```bash
pip install librosa numpy scipy
```

```python
# backend/app/services/pronunciation_eval.py
import librosa
import numpy as np

def analyze_pronunciation(audio_path: str):
    # 음성 파일 로드
    y, sr = librosa.load(audio_path, sr=16000)

    # 피치 분석
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    # 에너지 분석
    energy = librosa.feature.rms(y=y)[0]

    # 말속도 추정 (zero crossing rate)
    zcr = librosa.feature.zero_crossing_rate(y)[0]

    # 점수 계산 로직
    fluency_score = calculate_fluency(energy, zcr)
    pronunciation_score = calculate_pronunciation(pitches)

    return {
        "overall": pronunciation_score,
        "fluency": fluency_score
    }
```

### 옵션 2: 전문 발음 평가 API 사용

- **ETS Speechrater API** (유료)
- **Pronunciation Coach API** (Microsoft)
- **Google Speech-to-Text with pronunciation assessment**

### 옵션 3: 자체 딥러닝 모델 개발

1. Wav2Vec2, HuBERT 등 사전학습 모델 활용
2. TOEFL 스피킹 데이터로 Fine-tuning
3. 발음 점수 회귀 모델 학습

---

## 프로덕션 배포 가이드

### Docker 컨테이너화

**backend/Dockerfile**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**frontend/Dockerfile**
```dockerfile
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/tmp:/app/tmp

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### AWS 배포 예시

1. **EC2 인스턴스 생성**
2. **Docker 설치**
3. **코드 배포**
```bash
git clone your-repo
cd your-repo
docker-compose up -d
```

4. **도메인 연결 및 SSL 설정** (Let's Encrypt)

---

## 문제 해결

### Naver CLOVA API 오류

**오류: 401 Unauthorized**
- Client ID, Client Secret 확인
- Invoke URL이 올바른지 확인

**오류: 400 Bad Request**
- 오디오 파일 형식 확인 (지원: WAV, MP3, OGG 등)
- 파일 크기 확인 (최대 10MB)
- Content-Type 헤더 확인

**오류: 500 Internal Server Error**
- 네이버 클라우드 서비스 상태 확인
- 잠시 후 재시도

### OpenAI API 오류

**오류: Rate Limit Exceeded**
- API 사용량 제한 초과
- Billing 설정에서 한도 상향 조정

**오류: Invalid API Key**
- API 키 재확인
- `.env` 파일 로드 확인

### ffmpeg 오류

**macOS에서 ffmpeg 설치**
```bash
brew install ffmpeg
```

**Ubuntu에서 ffmpeg 설치**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows에서 ffmpeg 설치**
1. https://ffmpeg.org/download.html 다운로드
2. 압축 해제
3. 환경 변수 PATH에 bin 폴더 추가

---

## 참고 자료

- [Naver Cloud Platform 공식 문서](https://guide.ncloud-docs.com/)
- [CLOVA Speech API 가이드](https://api.ncloud-docs.com/docs/ai-naver-clovaspeechrecognition-stt)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [React 공식 문서](https://react.dev/)
