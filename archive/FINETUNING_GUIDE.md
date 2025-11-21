# TOEFL 스피킹 평가 LLM 파인튜닝 가이드

## 📋 목차
1. [데이터 준비](#1-데이터-준비)
2. [플랫폼 선택](#2-플랫폼-선택)
3. [파인튜닝 실행](#3-파인튜닝-실행)
4. [평가 및 배포](#4-평가-및-배포)
5. [비용 및 리소스](#5-비용-및-리소스)

---

## 1. 데이터 준비

### 1.1 현재 데이터 현황
- **컬럼 구조**: 텍스트, 파일이름, 텍스트피드백, 발음, fluency, 내용, 문법/표현, total_score
- **최소 필요 데이터**: 50-100개 샘플 (권장: 200개 이상)
- **데이터 품질**: 일관된 평가 기준, 명확한 피드백

### 1.2 CSV 파일 준비
```bash
# CSV 파일 구조 예시
python prepare_training_data.py
```

### 1.3 데이터 검증
- 모든 컬럼에 누락된 값 확인
- 평가 점수의 일관성 확인 (0-4점)
- 피드백 내용의 구체성 확인

---

## 2. 플랫폼 선택

### 옵션 1: OpenAI Fine-tuning (추천 ⭐)
**장점:**
- 간단한 API 사용
- 고품질 결과
- 빠른 학습 시간 (몇 시간)
- 인프라 관리 불필요

**단점:**
- 비용 발생 ($0.008/1K tokens 학습)
- 모델 소유권 없음

**적합한 경우:**
- 빠른 프로토타입
- 높은 품질 요구
- 인프라 관리 부담 회피

```bash
pip install openai
python finetune_openai.py
```

**비용 예상:**
- 100개 샘플 (평균 500 토큰): $4-10
- 1000개 샘플: $40-100

---

### 옵션 2: HuggingFace (오픈소스)
**장점:**
- 완전한 모델 소유권
- 커스터마이징 자유도 높음
- 장기적으로 비용 절감

**단점:**
- GPU 필요 (VRAM 12GB 이상)
- 기술적 복잡도 높음
- 학습 시간 길음 (수 시간~수일)

**적합한 경우:**
- 장기 운영 계획
- 모델 완전 제어 필요
- GPU 리소스 확보

**권장 모델:**
1. **Llama-2-7b-chat** (권장): 균형잡힌 성능
2. **Mistral-7B-Instruct**: 빠르고 효율적
3. **Gemma-7b-it**: Google 모델, 한국어 지원

```bash
pip install transformers datasets peft accelerate bitsandbytes
python finetune_huggingface.py
```

**리소스 요구사항:**
- GPU: NVIDIA RTX 3090 이상 (24GB VRAM)
- RAM: 32GB 이상
- 저장공간: 50GB 이상

**무료 GPU 옵션:**
- Google Colab (무료 T4 GPU, 제한적)
- Kaggle Notebooks (주 30시간 무료)

---

### 옵션 3: Google Gemini Fine-tuning
**장점:**
- 강력한 다국어 지원
- 합리적인 가격
- Google Cloud 통합

**단점:**
- 상대적으로 새로운 플랫폼
- 문서 부족

```bash
pip install google-generativeai
# Gemini API 키 필요
```

---

## 3. 파인튜닝 실행

### 3.1 데이터 변환
```bash
# CSV → JSONL 변환
python prepare_training_data.py

# 선택할 형식:
# 1. OpenAI
# 2. HuggingFace
# 3. Gemini
```

### 3.2 학습 실행

#### OpenAI 방식:
```bash
# API 키 설정
export OPENAI_API_KEY='your-key-here'

# 파인튜닝 실행
python finetune_openai.py
```

#### HuggingFace 방식:
```bash
# Hugging Face 로그인
huggingface-cli login

# 파인튜닝 실행 (GPU 필요!)
python finetune_huggingface.py
```

### 3.3 하이퍼파라미터 튜닝
```python
# 주요 설정값
hyperparameters = {
    "n_epochs": 3,           # 에포크 수 (3-5 권장)
    "learning_rate": 2e-4,   # 학습률
    "batch_size": 4,         # 배치 크기
}
```

**권장사항:**
- 데이터 50개 미만: epochs=5
- 데이터 100-500개: epochs=3
- 데이터 500개 이상: epochs=2

---

## 4. 평가 및 배포

### 4.1 모델 테스트
```python
# test_model.py
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="ft:gpt-3.5-turbo:your-model-id",
    messages=[
        {"role": "system", "content": "당신은 TOEFL 평가 전문가입니다."},
        {"role": "user", "content": "답변을 평가해주세요: ..."}
    ]
)

print(response.choices[0].message.content)
```

### 4.2 성능 평가 지표
- **일관성**: 같은 답변에 대한 반복 평가 일치도
- **정확성**: 실제 평가자와의 점수 차이 (RMSE)
- **피드백 품질**: 구체적이고 실행 가능한 피드백 제공 여부

### 4.3 A/B 테스트
```python
# 기존 모델 vs 파인튜닝 모델 비교
test_cases = [...]
for case in test_cases:
    original = evaluate_with_base_model(case)
    finetuned = evaluate_with_finetuned_model(case)
    compare(original, finetuned)
```

---

## 5. 비용 및 리소스

### 5.1 OpenAI 비용
| 항목 | 가격 | 예상 비용 |
|------|------|----------|
| 학습 (100 샘플) | $0.008/1K tokens | $5-10 |
| 추론 (1000회) | $0.012/1K tokens | $10-20 |
| **월 총 비용** | | **$50-100** |

### 5.2 HuggingFace 비용
| 항목 | 가격 | 예상 비용 |
|------|------|----------|
| GPU 서버 (A100) | $1-3/hour | 학습 시 $10-50 |
| 추론 (자체 호스팅) | 서버 비용 | $50-200/월 |

### 5.3 권장 시작 전략
1. **프로토타입 단계**: OpenAI GPT-3.5 ($50-100)
2. **검증 단계**: 100개 샘플로 테스트
3. **스케일업**: 데이터 500개 이상 수집
4. **프로덕션**: HuggingFace로 이전 (장기 비용 절감)

---

## 6. 단계별 실행 체크리스트

### ✅ 1단계: 데이터 준비
- [ ] CSV 파일에 최소 50개 샘플 확보
- [ ] 모든 컬럼 누락값 처리
- [ ] 평가 기준 문서화

### ✅ 2단계: 환경 설정
- [ ] Python 3.8+ 설치
- [ ] 필요 라이브러리 설치
- [ ] API 키 발급 (OpenAI or HuggingFace)

### ✅ 3단계: 데이터 변환
- [ ] `prepare_training_data.py` 실행
- [ ] JSONL 파일 검증
- [ ] 데이터 품질 확인

### ✅ 4단계: 파인튜닝
- [ ] 학습 스크립트 실행
- [ ] 학습 진행 모니터링
- [ ] 모델 ID 저장

### ✅ 5단계: 테스트
- [ ] 테스트 케이스 10개 준비
- [ ] 파인튜닝 모델로 평가
- [ ] 기존 평가와 비교

### ✅ 6단계: 배포
- [ ] API 엔드포인트 구축
- [ ] 웹 인터페이스 연결
- [ ] 모니터링 설정

---

## 7. 문제 해결

### Q1: 데이터가 부족한 경우?
**A:** Few-shot learning 사용
```python
# 프롬프트에 예시 포함
examples = """
예시 1:
답변: "I like reading books..."
평가: 발음 3.5, 유창성 3.0, ...

예시 2:
...
"""
```

### Q2: 모델이 일관성이 없는 경우?
**A:** Temperature 낮추기
```python
temperature=0.3  # 더 일관된 결과
```

### Q3: GPU가 없는 경우?
**A:**
1. Google Colab 사용 (무료)
2. OpenAI 사용 (GPU 불필요)
3. Runpod, Lambda Labs (저렴한 GPU 렌탈)

---

## 8. 추가 개선 방안

### 8.1 음성 인식 통합
```python
import whisper

# 음성 → 텍스트
model = whisper.load_model("base")
text = model.transcribe("audio.mp3")

# 텍스트 평가
evaluation = evaluate_toefl_speaking(text)
```

### 8.2 발음 분석 추가
```python
# Azure Speech Services 사용
from azure.cognitiveservices.speech import SpeechConfig

# 발음 점수 추출
pronunciation_score = analyze_pronunciation(audio_file)
```

### 8.3 실시간 피드백
```python
# WebSocket으로 실시간 평가
import asyncio
import websockets

async def evaluate_stream(websocket):
    audio = await websocket.recv()
    text = transcribe(audio)
    evaluation = evaluate(text)
    await websocket.send(evaluation)
```

---

## 9. 참고 자료

- [OpenAI Fine-tuning 가이드](https://platform.openai.com/docs/guides/fine-tuning)
- [HuggingFace PEFT 문서](https://huggingface.co/docs/peft)
- [LoRA 논문](https://arxiv.org/abs/2106.09685)
- [TOEFL 평가 기준](https://www.ets.org/toefl)

---

## 10. 연락처 및 지원

문제가 발생하면:
1. GitHub Issues 확인
2. HuggingFace Forums
3. OpenAI Community

**성공적인 파인튜닝을 기원합니다! 🚀**
