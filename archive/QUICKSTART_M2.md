# 🚀 M2 Mac 빠른 시작 가이드 (5분)

TOEFL 스피킹 평가 LLM 파인튜닝을 M2 MacBook Pro에서 시작하세요!

---

## ⚡ 초간단 3단계 시작

### 1️⃣ 설치 (2분)
```bash
chmod +x setup_m2.sh
./setup_m2.sh
```

### 2️⃣ 데이터 준비 (1분)
```bash
# CSV 파일을 toefl_evaluations.csv로 저장
# 그 다음:
python prepare_training_data.py
# 2번 선택 (HuggingFace)
```

### 3️⃣ 파인튜닝 (1-2시간, 자동)
```bash
python finetune_m2_mac.py
# 1번 선택 (Mistral-7B)
# 이제 커피 한 잔 하세요 ☕
```

**끝!** 🎉

---

## 💻 실행 예시

### 터미널에서 테스트
```python
from mlx_lm import load, generate

# 모델 로드
model, tokenizer = load(
    "mlx-community/Mistral-7B-Instruct-v0.2-4bit",
    adapter_path="./toefl_finetuned_mlx"
)

# 평가 실행
text = "I prefer studying subjects that interest me..."
prompt = f"다음 TOEFL 답변을 평가하세요: {text}"
result = generate(model, tokenizer, prompt=prompt, max_tokens=400)

print(result)
```

### API 서버로 실행
```bash
# 필요 패키지 설치
pip install flask flask-cors

# 서버 시작
python api_server_mlx.py

# 다른 터미널에서 테스트
curl -X POST http://localhost:5000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"text": "I like reading books because it helps me learn new things."}'
```

---

## 📊 내 M2 Mac에서 어떤 모델?

```bash
# RAM 확인
sysctl hw.memsize | awk '{print $2/1024/1024/1024 "GB"}'
```

| RAM | 추천 모델 | 학습 시간 |
|-----|----------|----------|
| 8GB | Phi-2 | 30-60분 |
| 16GB | **Mistral-7B** ⭐ | 1-2시간 |
| 32GB+ | Llama-2-13B | 2-4시간 |

---

## 🎯 실전 사용 시나리오

### 시나리오 1: Python 스크립트에 통합
```python
# my_app.py
from mlx_lm import load, generate

class TOEFLEvaluator:
    def __init__(self):
        self.model, self.tokenizer = load(
            "mlx-community/Mistral-7B-Instruct-v0.2-4bit",
            adapter_path="./toefl_finetuned_mlx"
        )

    def evaluate(self, text):
        prompt = f"TOEFL 답변 평가: {text}"
        return generate(self.model, self.tokenizer,
                       prompt=prompt, max_tokens=400)

# 사용
evaluator = TOEFLEvaluator()
score = evaluator.evaluate("Your answer here...")
print(score)
```

### 시나리오 2: 웹 애플리케이션
```python
# Streamlit 앱
import streamlit as st
from mlx_lm import load, generate

st.title("🎓 TOEFL 스피킹 평가")

# 모델 로드 (캐시)
@st.cache_resource
def load_model():
    return load("mlx-community/Mistral-7B-Instruct-v0.2-4bit",
                adapter_path="./toefl_finetuned_mlx")

model, tokenizer = load_model()

# 입력
text = st.text_area("답변을 입력하세요:")

if st.button("평가하기"):
    with st.spinner("평가 중..."):
        prompt = f"TOEFL 답변 평가: {text}"
        result = generate(model, tokenizer, prompt=prompt, max_tokens=400)
        st.success(result)
```

실행:
```bash
pip install streamlit
streamlit run app.py
```

### 시나리오 3: REST API 서버
```bash
# 서버 시작
python api_server_mlx.py --port 8080

# 다른 앱에서 호출
import requests

response = requests.post('http://localhost:8080/evaluate',
    json={'text': 'I like reading...'})
print(response.json()['evaluation'])
```

---

## 🔧 자주 묻는 질문

### Q1: 학습 중 멈춘 것 같아요
**A:** Activity Monitor를 열어서 "Python" 프로세스 확인
- CPU 800%+ 사용 중이면 정상 (학습 중)
- 메모리 부족 시 배치 크기 줄이기

### Q2: 어떤 모델이 가장 좋나요?
**A:** TOEFL 평가에는 **Mistral-7B** 추천
- 빠르고 정확함
- 한국어/영어 모두 지원
- 16GB RAM에서 안정적

### Q3: 데이터가 적으면 어떻게 하나요?
**A:** 50개 미만이면:
1. Few-shot learning 사용 (예시를 프롬프트에 포함)
2. 더 많은 에포크 (5-7)
3. 데이터 증강 (paraphrasing)

### Q4: 비용이 드나요?
**A:** **완전 무료!**
- 모델 다운로드: 무료
- 학습: M2 Mac에서 무료
- 추론: 무료
- 운영: 무료

---

## 📈 성능 개선 팁

### 1. 더 빠른 학습
```python
# batch_size 증가 (메모리 허용 시)
batch_size=8  # 기본값: 4

# 학습률 증가
learning_rate=2e-5  # 기본값: 1e-5
```

### 2. 더 높은 정확도
```python
# 에포크 증가
num_epochs=5  # 기본값: 3

# LoRA rank 증가
lora_rank=32  # 기본값: 16
```

### 3. 메모리 절약
```python
# batch_size 감소
batch_size=2

# 더 작은 모델 사용
model = "mlx-community/Phi-2-4bit"
```

---

## 🎯 다음 단계

1. **음성 인식 추가**
   ```bash
   pip install openai-whisper
   # 음성 → 텍스트 → 평가
   ```

2. **웹 인터페이스**
   ```bash
   pip install streamlit
   streamlit run web_app.py
   ```

3. **배포**
   - Docker 컨테이너
   - Railway/Render에 배포
   - iOS 앱에 통합 (Core ML 변환)

---

## 📚 참고 자료

- **상세 가이드**: `M2_MAC_SETUP.md`
- **파인튜닝 이론**: `FINETUNING_GUIDE.md`
- **MLX 문서**: https://ml-explore.github.io/mlx/
- **MLX Models**: https://huggingface.co/mlx-community

---

## ✅ 체크리스트

시작 전:
- [ ] M2/M3 Mac 준비
- [ ] 16GB+ RAM (권장)
- [ ] CSV 데이터 50개 이상

설치:
- [ ] `./setup_m2.sh` 실행 완료
- [ ] MLX 설치 확인
- [ ] 테스트 데이터 준비

파인튜닝:
- [ ] 데이터 변환 완료
- [ ] 모델 선택
- [ ] 학습 완료 (1-2시간)
- [ ] 테스트 통과

배포:
- [ ] API 서버 테스트
- [ ] 실제 답변으로 검증
- [ ] 프로덕션 준비

---

## 🎊 완료!

**축하합니다!** M2 Mac에서 TOEFL 평가 AI를 만들었습니다!

문제가 있나요? → `M2_MAC_SETUP.md`의 "문제 해결" 섹션 참고

**Happy Fine-tuning!** 🚀
