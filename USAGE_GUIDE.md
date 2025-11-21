# 🎯 TOEFL 스피킹 평가 시스템 사용 가이드

이 가이드는 100개의 WAV 파일(45초 50개 + 60초 50개)과 CSV 피드백 데이터를 사용하여 OpenAI GPT 파인튜닝까지 완료하는 전체 과정을 안내합니다.

---

## 📋 목차

1. [환경 설정](#1-환경-설정)
2. [데이터 준비](#2-데이터-준비)
3. [MFCC 특징 추출](#3-mfcc-특징-추출)
4. [OpenAI 파인튜닝 데이터 생성](#4-openai-파인튜닝-데이터-생성)
5. [GPT 파인튜닝 실행](#5-gpt-파인튜닝-실행)
6. [평가 시스템 사용](#6-평가-시스템-사용)

---

## 1. 환경 설정

### 1.1 패키지 설치

```bash
# 프로젝트 루트에서
pip install -r requirements.txt
```

필요한 패키지:
- `flask` - REST API 서버
- `requests` - HTTP 요청
- `openai` - OpenAI API 클라이언트
- `pandas`, `numpy` - 데이터 처리
- `librosa`, `soundfile` - 음성 특징 추출

### 1.2 API 키 설정

`.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 편집:

```bash
# Naver Clova Speech API
NAVER_CLOVA_SECRET_KEY=your_actual_clova_secret_key

# OpenAI API
OPENAI_API_KEY=sk-your_actual_openai_api_key

# 파인튜닝 전에는 기본 모델
OPENAI_FINETUNED_MODEL=gpt-3.5-turbo
```

**API 키 발급:**
- **Clova API**: https://www.ncloud.com/product/aiService/clovaSpeech
- **OpenAI API**: https://platform.openai.com/api-keys

---

## 2. 데이터 준비

### 2.1 필요한 데이터

```
EDA_CAP/
├── audio/               # 100개 WAV 파일
│   ├── student_1.wav
│   ├── student_2.wav
│   └── ...
└── feedback.csv         # 교사 피드백 데이터
```

### 2.2 CSV 형식 확인

`feedback.csv`에 필요한 컬럼:

```csv
텍스트,파일 이름,텍스트 피드백,발음,fluency,내용,문법/표현,total_score
"I prefer studying subjects that...",student_1,#발음: R/L구분 필요,3.0,3.5,3.2,2.8,3.1
"In my opinion, the most...",student_2,#문법: 관사 누락,3.2,3.0,3.5,2.9,3.2
```

**필수 컬럼:**
- `텍스트`: 학생이 말하고자 했던 대본 (스크립트)
- `파일 이름`: WAV 파일과 매칭할 식별자 (예: "student_1")
- `발음`: 발음 평가 점수 (0-4점)
- `fluency`: 유창성 평가 점수 (0-4점)
- `내용`: 내용 평가 점수 (0-4점)
- `문법/표현`: 문법 평가 점수 (0-4점)
- `total_score`: 종합 점수 (0-4점)
- `텍스트 피드백`: 교사 피드백 텍스트

---

## 3. MFCC 특징 추출

### 3.1 특징 추출 실행

```bash
cd dataset_preparation

python extract_audio_features.py \
  --audio_dir ../audio \
  --csv ../feedback.csv \
  --output feedback_with_features.csv
```

### 3.2 처리 과정

스크립트가 다음 작업을 수행합니다:

1. **WAV 파일 로드**: `../audio/*.wav` 파일 탐색
2. **MFCC 특징 추출**:
   - MFCC 13차원 (평균, 표준편차)
   - Pitch (평균, 표준편차)
   - Energy (평균, 표준편차)
   - 말하기 속도 (speech_rate)
   - 휴지 패턴 (pause 횟수, 평균 길이)
   - Spectral Centroid, Tempo
3. **CSV 매칭**: WAV 파일명과 CSV의 '파일 이름' 컬럼 매칭
4. **특징 추가**: 새 컬럼 추가 및 텍스트 요약 생성

### 3.3 출력 확인

```bash
# 생성된 파일 확인
ls -lh feedback_with_features.csv

# 처음 5행 확인
head -5 feedback_with_features.csv

# 추가된 컬럼 확인
head -1 feedback_with_features.csv | tr ',' '\n'
```

**추가된 컬럼:**
- `audio_duration` - 음성 길이 (초)
- `pitch_mean`, `pitch_std` - Pitch 통계
- `energy_mean` - 평균 에너지
- `num_pauses` - 휴지 횟수
- `pause_mean` - 평균 휴지 길이
- `speech_rate` - 말하기 속도
- `audio_summary` - 음성 특징 텍스트 요약

### 3.4 문제 해결

**Q: "CSV에서 매칭 실패" 메시지가 나옵니다**

A: WAV 파일명과 CSV의 '파일 이름' 컬럼이 일치하는지 확인하세요.

```python
# 예시:
# WAV: student_1.wav
# CSV '파일 이름': student_1 또는 "Q1 student_1"

# 매칭 로직 (extract_audio_features.py:211)
file_id = audio_file.stem  # "student_1"
matching_rows = df[df['파일 이름'].str.contains(file_id, na=False)]
```

필요시 CSV의 '파일 이름' 컬럼을 WAV 파일명과 일치하도록 수정하세요.

---

## 4. OpenAI 파인튜닝 데이터 생성

### 4.1 JSONL 데이터 생성

```bash
# dataset_preparation 폴더에서
python prepare_openai_finetuning.py \
  --csv feedback_with_features.csv \
  --output openai_training_data.jsonl
```

### 4.2 생성되는 데이터 형식

```json
{
  "messages": [
    {
      "role": "system",
      "content": "당신은 TOEFL 스피킹 평가 전문가입니다..."
    },
    {
      "role": "user",
      "content": "학생 답변:\nI prefer studying...\n\nClova API 발음 분석:\n- 발음 점수: 75.0/100\n- 유창성 점수: 87.5/100\n\n음성 특징 분석:\n- 길이: 45.2초\n- 말하기 속도: 3.2 구간/초\n- 평균 Pitch: 150.3Hz (변동: 30.5)\n- 휴지: 5회, 평균 0.8초\n..."
    },
    {
      "role": "assistant",
      "content": "평가 결과:\n\n**내용: 3.2/4.0**\n**문법: 2.8/4.0**\n**발음: 3.0/4.0**\n**유창성: 3.5/4.0**\n\n**피드백:**\n#발음: R/L구분 필요\n..."
    }
  ]
}
```

### 4.3 데이터 검증

스크립트가 자동으로 검증을 수행합니다:

```
✅ 모든 데이터가 OpenAI 형식에 맞습니다

📈 토큰 추정:
- 총 문자 수: 120,456
- 추정 토큰 수: 30,114
- 평균 토큰/샘플: 301

💰 예상 파인튜닝 비용 (GPT-3.5-turbo):
- 학습 비용: $0.24
```

### 4.4 수동 검증

```bash
# 첫 번째 샘플 확인
head -1 openai_training_data.jsonl | python -m json.tool

# 샘플 개수 확인 (100개여야 함)
wc -l openai_training_data.jsonl
```

---

## 5. GPT 파인튜닝 실행

### 5.1 OpenAI 플랫폼 사용 (권장)

**웹 인터페이스:**

1. https://platform.openai.com/finetune 접속
2. "Create fine-tuned model" 클릭
3. `openai_training_data.jsonl` 파일 업로드
4. Base model: `gpt-3.5-turbo-1106` 선택
5. "Create" 클릭

**진행 상황 모니터링:**
- 학습 시간: 약 10-30분 (100개 샘플 기준)
- 상태: Pending → Running → Succeeded
- 완료 후 모델 ID 확인: `ft:gpt-3.5-turbo:your-org:model-name:abc123`

### 5.2 CLI 사용 (선택)

```bash
# OpenAI CLI 설치
pip install openai

# 파일 업로드
openai api files.create -f openai_training_data.jsonl -p fine-tune

# 파인튜닝 시작 (FILE_ID는 위 명령의 출력에서 확인)
openai api fine_tunes.create \
  -t FILE_ID \
  -m gpt-3.5-turbo-1106 \
  --suffix "toefl-speaking-eval"

# 진행 상황 확인
openai api fine_tunes.follow -i FINE_TUNE_ID
```

### 5.3 .env 파일 업데이트

파인튜닝 완료 후:

```bash
# .env 파일 수정
OPENAI_FINETUNED_MODEL=ft:gpt-3.5-turbo:your-org:toefl-speaking-eval:abc123
```

---

## 6. 평가 시스템 사용

### 6.1 CLI로 평가 실행

```bash
cd ..  # 프로젝트 루트로 이동

# 단일 파일 평가
python toefl_evaluator.py --audio test_student.wav

# 결과 저장
python toefl_evaluator.py --audio test_student.wav --save
```

**출력 예시:**

```
=== TOEFL 스피킹 평가 결과 ===

📝 Clova API 음성 인식 결과:
I prefer studying subjects that interest me because they keep me motivated...

🎯 Clova API 발음/유창성 평가:
- 발음 점수: 82.5/100 (3.3/4.0)
- 유창성 점수: 78.0/100 (3.1/4.0)

🤖 GPT 내용/문법 평가:

평가 결과:

**내용 (Content): 3.5/4.0**
- 질문에 대한 명확한 답변 제시
- 논리적 구조와 전개 우수

**문법/표현 (Grammar): 3.0/4.0**
- 대체로 정확한 문법
- 일부 관사 누락 있음

**종합 점수: 3.2/4.0**

**피드백:**
- 억양이 풍부하여 표현력이 좋음
- 휴지 패턴 양호

💾 결과 저장: toefl_evaluation_20251117_153045.json
```

### 6.2 REST API 서버 실행

```bash
# 서버 시작
python api_server.py
```

**API 엔드포인트:**

```bash
# 음성 파일 평가
curl -X POST http://localhost:5000/evaluate \
  -F "audio=@test_student.wav"

# 텍스트만 평가 (STT 결과가 이미 있는 경우)
curl -X POST http://localhost:5000/evaluate_text \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "I prefer studying subjects that interest me...",
    "pronunciation_score": 82.5,
    "fluency_score": 78.0
  }'

# 서버 상태 확인
curl http://localhost:5000/health
```

**응답 예시:**

```json
{
  "success": true,
  "data": {
    "clova_result": {
      "transcript": "I prefer studying...",
      "pronunciation_score": 82.5,
      "fluency_score": 78.0
    },
    "gpt_evaluation": {
      "content_score": 3.5,
      "grammar_score": 3.0,
      "total_score": 3.2,
      "feedback": "..."
    },
    "timestamp": "2025-11-17T15:30:45"
  }
}
```

---

## 🎓 전체 워크플로우 요약

```bash
# 1. 환경 설정
pip install -r requirements.txt
cp .env.example .env
# .env 파일에 API 키 입력

# 2. 데이터 준비
# audio/ 폴더에 100개 WAV 파일 배치
# feedback.csv 파일 준비

# 3. MFCC 특징 추출
cd dataset_preparation
python extract_audio_features.py \
  --audio_dir ../audio \
  --csv ../feedback.csv \
  --output feedback_with_features.csv

# 4. OpenAI 파인튜닝 데이터 생성
python prepare_openai_finetuning.py \
  --csv feedback_with_features.csv \
  --output openai_training_data.jsonl

# 5. 파인튜닝 실행 (OpenAI 웹사이트)
# https://platform.openai.com/finetune
# openai_training_data.jsonl 업로드

# 6. .env 파일에 파인튜닝 모델 ID 설정
# OPENAI_FINETUNED_MODEL=ft:gpt-3.5-turbo:...

# 7. 평가 시스템 사용
cd ..
python toefl_evaluator.py --audio test.wav
# 또는
python api_server.py  # REST API 서버
```

---

## 💡 팁 및 주의사항

### 데이터 품질

- **WAV 파일 품질**: 16kHz 이상, 모노 채널 권장
- **CSV 매칭**: 파일명 일관성 유지
- **피드백 텍스트**: 구체적이고 상세할수록 파인튜닝 효과 증대

### 비용 관리

- **파인튜닝 비용**: 100개 샘플 기준 약 $0.20-0.50
- **추론 비용**: 파인튜닝 모델 사용 시 일반 GPT-3.5-turbo 대비 약 2배
- **Clova API**: 사용량 기반 과금 (무료 체험 가능)

### 성능 최적화

- **파인튜닝 샘플 수**: 최소 50개, 권장 100-500개
- **평가 일관성**: 교사 피드백의 평가 기준 일관성 중요
- **음성 특징**: MFCC 특징이 GPT의 평가 정확도 향상에 기여

---

## 🐛 문제 해결

### librosa 설치 오류

```bash
# macOS
brew install libsndfile
pip install librosa soundfile

# Ubuntu/Debian
sudo apt-get install libsndfile1
pip install librosa soundfile
```

### Clova API 오류

- API 키 확인: `.env` 파일의 `NAVER_CLOVA_SECRET_KEY`
- 네트워크 연결 확인
- Clova API 문서: https://api.ncloud-docs.com/docs/ai-naver-clovaspeech

### OpenAI API 오류

- API 키 확인: `.env` 파일의 `OPENAI_API_KEY`
- 사용량/한도 확인: https://platform.openai.com/usage
- 파인튜닝 모델 ID 확인

---

**MFCC 음성 특징으로 더 정확한 TOEFL 평가를 하세요!** 🎤📊
