# 🎓 TOEFL 스피킹 자동 평가 시스템

**Clova STT + 발음평가 → 파인튜닝된 OpenAI GPT** 기반 자동 채점

---

## 📋 시스템 구조

```
[학생 음성 WAV/MP3]
     ↓
[Naver Clova API]
  - 음성인식 (STT)
  - 발음 점수 (0-100)
  - 유창성 점수 (0-100)
     ↓
[파인튜닝된 OpenAI GPT]
  - 내용 평가
  - 문법 평가
  - 종합 피드백
     ↓
[종합 평가 결과]
```

---

## 📁 프로젝트 구조

```
EDA_CAP/
│
├── 📂 dataset_preparation/          # 데이터셋 준비
│   ├── prepare_openai_finetuning.py # GPT 파인튜닝 데이터 생성
│   └── README.md
│
├── 🚀 toefl_evaluator.py            # 평가 시스템 (핵심)
├── 🌐 api_server.py                 # REST API 서버
│
├── 📖 README.md                     # 이 파일
├── 📦 requirements.txt              # 필수 패키지
└── 📄 toefl_evaluations_template.csv
```

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일 생성:
```bash
# Naver Clova Speech API
NAVER_CLOVA_SECRET_KEY=your_clova_secret_key

# OpenAI API
OPENAI_API_KEY=sk-your_openai_api_key

# 파인튜닝된 모델 (선택, 없으면 gpt-3.5-turbo 사용)
OPENAI_FINETUNED_MODEL=ft:gpt-3.5-turbo:your-org:model-id
```

### 3. 사용 방법

#### Option A: Python 스크립트

```bash
python toefl_evaluator.py --audio student.wav
```

#### Option B: API 서버

```bash
# 서버 시작
python api_server.py

# 다른 터미널에서 평가 요청
curl -X POST http://localhost:5000/evaluate \
  -F "file=@student.wav"
```

---

## 📊 데이터 준비 (OpenAI 파인튜닝)

### 현재 데이터: 100개 (45초 50개 + 60초 50개)

```bash
cd dataset_preparation

# OpenAI 파인튜닝 데이터 생성
python prepare_openai_finetuning.py \
  --csv ../feedback.csv \
  --output openai_training_data.jsonl
```

**출력**: `openai_training_data.jsonl` (OpenAI 형식)

### CSV 형식

```csv
텍스트,파일 이름,텍스트 피드백,발음,fluency,내용,문법/표현,total_score
"I prefer studying...",Q1 학생A,#발음: R/L구분,3.0,3.5,3.2,2.8,3.1
```

---

## 🎯 OpenAI 파인튜닝

### 데이터 준비 완료 후:

```bash
# OpenAI CLI 사용
openai tools fine_tunes.prepare_data -f openai_training_data.jsonl

# 파인튜닝 시작
openai api fine_tunes.create \
  -t openai_training_data.jsonl \
  -m gpt-3.5-turbo
```

### 또는 OpenAI 웹 인터페이스:
1. https://platform.openai.com/finetune
2. `openai_training_data.jsonl` 업로드
3. 파인튜닝 시작
4. 완료 후 모델 ID 받기: `ft:gpt-3.5-turbo:your-org:model-id`
5. `.env`에 모델 ID 입력

**예상 비용** (100개 샘플):
- 학습: ~$5-10
- 추론 (1000회): ~$10-20

---

## 💻 API 사용법

### 서버 시작

```bash
python api_server.py --port 5000
```

### 음성 파일 평가

```bash
curl -X POST http://localhost:5000/evaluate \
  -F "file=@student.wav"
```

**응답:**
```json
{
  "speech_recognition": {
    "text": "I prefer studying subjects that interest me...",
    "confidence": 0.92
  },
  "pronunciation": {
    "score": 75.5,
    "score_4point": 3.02
  },
  "fluency": {
    "score": 80.0,
    "score_4point": 3.2
  },
  "gpt_evaluation": "평가 결과: 내용 3.5/4.0, 문법 3.0/4.0..."
}
```

### 텍스트만 평가

```bash
curl -X POST http://localhost:5000/evaluate_text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I prefer studying...",
    "pronunciation_score": 75,
    "fluency_score": 80
  }'
```

---

## 🔧 설정

### 필수 패키지

```bash
flask>=3.0.0
flask-cors>=4.0.0
requests>=2.31.0
openai>=1.0.0
python-dotenv>=1.0.0
```

### API 키 발급

1. **Naver Clova Speech**
   - https://www.ncloud.com/product/aiService/clovaSpeech
   - CLOVA Speech 서비스 신청
   - Secret Key 발급

2. **OpenAI**
   - https://platform.openai.com/api-keys
   - API 키 생성

---

## 🎓 실전 사용 예시

### Python에서 직접 사용

```python
from toefl_evaluator import TOEFLEvaluator

# 초기화
evaluator = TOEFLEvaluator(
    clova_secret_key="your_clova_key",
    openai_api_key="your_openai_key",
    finetuned_model="ft:gpt-3.5-turbo:..."  # 또는 None
)

# 평가
result = evaluator.evaluate_complete("student.wav")

# 결과
print(f"발음: {result['pronunciation']['score_4point']:.2f}/4.0")
print(f"유창성: {result['fluency']['score_4point']:.2f}/4.0")
print(result['gpt_evaluation'])
```

---

## 🐛 문제 해결

### Q1: Clova API 오류

**A**: Secret Key 확인
```bash
# 환경변수 확인
echo $NAVER_CLOVA_SECRET_KEY

# 또는 .env 파일 확인
cat .env
```

### Q2: OpenAI API 오류

**A**: API 키 및 모델 ID 확인
```bash
# 파인튜닝된 모델 목록
openai api fine_tunes.list
```

### Q3: 음성 파일 형식 오류

**A**: 지원 형식
- WAV (권장)
- MP3
- M4A
- OGG

---

## 📚 상세 문서

- **`dataset_preparation/README.md`** - 데이터 준비 가이드
- **`PROJECT_STRUCTURE.md`** - 프로젝트 구조
- **`archive/`** - 참고 자료

---

## 💡 핵심 특징

### ✅ 실용적인 구조
- 100개 샘플로 OpenAI GPT 파인튜닝
- LSTM 불필요 (데이터 부족 문제 해결)
- Clova API로 음성 분석

### ✅ 간단한 배포
- Flask API 서버
- Docker 지원 (선택)
- CORS 활성화

### ✅ 비용 효율
- Clova API: 종량제
- OpenAI 파인튜닝: ~$10-20
- 추론: ~$0.01/건

---

## 📦 배포

### Docker (선택)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "api_server.py", "--host", "0.0.0.0"]
```

```bash
docker build -t toefl-api .
docker run -p 5000:5000 --env-file .env toefl-api
```

---

## 📄 라이선스

MIT License

---

**간결하고 실용적인 TOEFL 평가 시스템** 🎓🚀

**핵심**: Clova API (음성분석) + 파인튜닝된 GPT (내용평가)
