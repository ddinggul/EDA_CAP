# 🎓 TOEFL 스피킹 평가 LLM 파인튜닝 프로젝트

M2 MacBook Pro에서 로컬로 실행 가능한 TOEFL 스피킹 자동 채점 시스템

---

## 📁 프로젝트 구조

```
EDA_CAP/
├── 📄 prepare_training_data.py      # CSV → JSONL 변환 도구
├── 🍎 finetune_m2_mac.py           # M2 Mac 최적화 파인튜닝 (권장!)
├── 🤖 finetune_openai.py           # OpenAI GPT 파인튜닝
├── 🤗 finetune_huggingface.py      # HuggingFace 모델 파인튜닝
├── 🌐 api_server_mlx.py            # REST API 서버 (MLX)
├── ⚙️ setup_m2.sh                  # M2 Mac 자동 설치 스크립트
│
├── 📋 requirements_m2.txt          # M2 Mac 전용 패키지
├── 📋 requirements_finetuning.txt  # 일반 파인튜닝 패키지
│
├── 📖 QUICKSTART_M2.md             # 🚀 5분 빠른 시작 가이드
├── 📖 M2_MAC_SETUP.md              # M2 Mac 상세 가이드
├── 📖 FINETUNING_GUIDE.md          # 일반 파인튜닝 가이드
│
└── 📊 toefl_evaluations_template.csv  # CSV 템플릿
```

---

## 🚀 빠른 시작 (M2 Mac 권장)

### 1단계: 설치 (2분)
```bash
./setup_m2.sh
```

### 2단계: 데이터 준비
```bash
# CSV 파일을 toefl_evaluations.csv로 저장 후
python prepare_training_data.py
# → 2번 선택 (HuggingFace)
```

### 3단계: 파인튜닝 (1-2시간)
```bash
python finetune_m2_mac.py
# → 1번 선택 (Mistral-7B)
```

**상세 가이드**: `QUICKSTART_M2.md` 참고

---

## 💡 플랫폼별 선택 가이드

### 🍎 M2 Mac 사용자 (권장!)
- **파일**: `finetune_m2_mac.py`
- **프레임워크**: MLX (Apple Silicon 최적화)
- **장점**: 완전 무료, 로컬 실행, 빠름
- **RAM**: 16GB 이상 권장
- **가이드**: `M2_MAC_SETUP.md`

### 🤖 OpenAI 사용자
- **파일**: `finetune_openai.py`
- **장점**: 간단, 고품질
- **단점**: 비용 발생 ($50-100)
- **가이드**: `FINETUNING_GUIDE.md`

### 🤗 HuggingFace 사용자
- **파일**: `finetune_huggingface.py`
- **장점**: 오픈소스, 커스터마이징
- **단점**: GPU 필요, 복잡
- **가이드**: `FINETUNING_GUIDE.md`

---

## 📊 데이터 형식

### CSV 형식 (입력)
```csv
텍스트,파일 이름,텍스트 피드백,발음,fluency,내용,문법/표현,total_score
"I prefer studying...",Q1 CB,#발음: read,"R/L 구분","톤조절","주제 적합","대명사 오류",2.6
```

### JSONL 형식 (학습용, 자동 변환)
```json
{
  "messages": [
    {"role": "system", "content": "당신은 TOEFL 평가 전문가입니다."},
    {"role": "user", "content": "다음 답변을 평가하세요: ..."},
    {"role": "assistant", "content": "평가 결과: ..."}
  ]
}
```

---

## 🎯 성능 비교

### M2 Mac (MLX) vs 다른 방법

| 방법 | 초기 비용 | 월 비용 | 학습 시간 | 품질 | 난이도 |
|------|---------|--------|----------|------|--------|
| **M2 Mac (MLX)** ⭐ | $0 | $0 | 1-2시간 | ⭐⭐⭐⭐ | ⭐ 쉬움 |
| OpenAI | $0 | $50-100 | 1-3시간 | ⭐⭐⭐⭐⭐ | ⭐ 쉬움 |
| Cloud GPU | $0 | $100-300 | 2-4시간 | ⭐⭐⭐⭐ | ⭐⭐⭐ 어려움 |

---

## 📈 RAM 용량별 권장 모델

| RAM | 모델 | 파라미터 | 학습 시간 | 품질 |
|-----|------|---------|----------|------|
| 8GB | Phi-2 | 2.7B | 30-60분 | ⭐⭐⭐ |
| 16GB | **Mistral-7B** ⭐ | 7B | 1-2시간 | ⭐⭐⭐⭐ |
| 32GB+ | Llama-2-13B | 13B | 2-4시간 | ⭐⭐⭐⭐⭐ |

---

## 🛠️ 사용 예시

### Python 스크립트
```python
from mlx_lm import load, generate

# 모델 로드
model, tokenizer = load(
    "mlx-community/Mistral-7B-Instruct-v0.2-4bit",
    adapter_path="./toefl_finetuned_mlx"
)

# 평가
text = "I prefer studying subjects that interest me..."
prompt = f"TOEFL 답변 평가: {text}"
result = generate(model, tokenizer, prompt=prompt, max_tokens=400)
print(result)
```

### REST API
```bash
# 서버 시작
python api_server_mlx.py

# 평가 요청
curl -X POST http://localhost:5000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"text": "I like reading books..."}'
```

### 웹 인터페이스 (Streamlit)
```python
import streamlit as st
from mlx_lm import load, generate

st.title("TOEFL 평가")
text = st.text_area("답변 입력:")
if st.button("평가"):
    # 평가 로직
    st.success(result)
```

---

## 📚 주요 파일 설명

### 핵심 스크립트

#### `finetune_m2_mac.py` ⭐ (M2 Mac 권장)
- MLX 프레임워크 사용
- Apple Silicon 최적화
- 자동 시스템 체크
- 대화형 모드 지원

#### `prepare_training_data.py`
- CSV → JSONL 변환
- 3가지 형식 지원 (OpenAI, HuggingFace, Gemini)
- 데이터 검증 기능

#### `api_server_mlx.py`
- Flask REST API
- 단일/일괄 평가
- CORS 지원
- 상태 체크 엔드포인트

### 가이드 문서

#### `QUICKSTART_M2.md` 🚀
- 5분 빠른 시작
- 실전 예시
- FAQ

#### `M2_MAC_SETUP.md` 📖
- 상세 설치 가이드
- 모델 선택 가이드
- 문제 해결

#### `FINETUNING_GUIDE.md` 📚
- 파인튜닝 이론
- 플랫폼별 가이드
- 비용 분석

---

## 🔧 설치 옵션

### Option 1: 자동 설치 (권장)
```bash
chmod +x setup_m2.sh
./setup_m2.sh
```

### Option 2: 수동 설치
```bash
# MLX 설치
pip install mlx mlx-lm

# 기본 패키지
pip install -r requirements_m2.txt
```

---

## 💻 시스템 요구사항

### 최소 사양
- M2/M3 Mac (Apple Silicon)
- 8GB RAM
- 50GB 저장공간
- macOS 13.0+
- Python 3.9+

### 권장 사양
- M2 Pro/Max/Ultra
- 16GB+ RAM
- 100GB SSD
- macOS 14.0+
- Python 3.11+

---

## 🎯 실전 활용

### 1. 개별 평가 시스템
```python
# app.py
evaluator = TOEFLEvaluator()
score = evaluator.evaluate(student_answer)
```

### 2. 배치 처리
```python
# batch_process.py
answers = load_student_answers()
results = [evaluator.evaluate(a) for a in answers]
save_results(results)
```

### 3. 실시간 평가 웹앱
```bash
streamlit run web_app.py
# → http://localhost:8501
```

### 4. API 서비스
```bash
python api_server_mlx.py --port 8080
# → http://localhost:8080
```

---

## 📊 평가 기준

모델은 다음 4가지 기준으로 평가합니다:

1. **발음 (Pronunciation)**
   - 개별 음소 정확성
   - R/L 구분
   - 장단모음

2. **유창성 (Fluency)**
   - 말하기 속도
   - 톤 조절
   - 자연스러움

3. **내용 (Content)**
   - 질문 적합성
   - 논리적 구조
   - 구체적 예시

4. **문법/표현 (Grammar)**
   - 문법 정확성
   - 어휘 다양성
   - 적절한 표현

**총점**: 0-4점 (TOEFL 기준)

---

## 🤝 기여 및 지원

### 버그 리포트
Issues 탭에 문제를 제보해주세요.

### 개선 제안
Pull Request를 환영합니다!

### 질문
Discussions 탭에서 질문하세요.

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 🙏 감사의 말

- **Apple MLX Team**: Apple Silicon 최적화
- **HuggingFace**: 오픈소스 모델
- **Mistral AI**: Mistral-7B 모델

---

## 📞 연락처

문제가 있거나 질문이 있으신가요?

1. 📖 먼저 가이드 문서를 확인하세요
2. 🔍 FAQ를 검색하세요
3. 💬 Issues에 질문하세요

---

## ✅ 다음 단계

- [ ] `QUICKSTART_M2.md`로 시작하기
- [ ] CSV 데이터 50개 이상 준비
- [ ] 파인튜닝 실행
- [ ] 모델 테스트
- [ ] API 서버 배포

**Happy Fine-tuning!** 🚀🎓
