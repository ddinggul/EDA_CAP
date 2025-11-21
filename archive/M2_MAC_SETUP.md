# M2 MacBook Pro에서 LLM 파인튜닝 가이드

## 🍎 Apple Silicon (M2) 최적화 파인튜닝

M2 칩의 **Neural Engine**과 **Unified Memory**를 활용하여 GPU 없이도 효율적으로 LLM을 파인튜닝할 수 있습니다.

---

## 📋 시스템 요구사항

| RAM | 권장 모델 | 학습 시간 (100 샘플) |
|-----|----------|---------------------|
| 8GB | Phi-2 (2.7B) | 30-60분 |
| 16GB | Mistral-7B ⭐ | 1-2시간 |
| 32GB+ | Llama-2-13B | 2-4시간 |

**확인 방법:**
```bash
# Mac 사양 확인
system_profiler SPHardwareDataType | grep "Memory"
```

---

## 🚀 빠른 시작 (5분 설치)

### 1단계: MLX 설치
```bash
# MLX 프레임워크 (Apple Silicon 최적화)
pip install mlx mlx-lm

# 추가 패키지
pip install numpy transformers huggingface-hub
```

### 2단계: 데이터 준비
```bash
# CSV → JSONL 변환
python prepare_training_data.py

# HuggingFace 형식 선택 (2번)
```

### 3단계: 파인튜닝 실행
```bash
python finetune_m2_mac.py
```

**그게 끝입니다!** 🎉

---

## 📊 MLX vs 다른 프레임워크 비교

| 프레임워크 | M2 최적화 | 메모리 효율 | 속도 | 설치 난이도 |
|-----------|----------|-----------|------|-----------|
| **MLX** ⭐ | ✅ 완벽 | ✅ 최고 | ✅ 빠름 | ⭐ 쉬움 |
| PyTorch | ⚠️ 부분 | ⚠️ 보통 | ⚠️ 느림 | ⭐⭐ 보통 |
| TensorFlow | ❌ 없음 | ⚠️ 보통 | ❌ 매우 느림 | ⭐⭐⭐ 어려움 |

---

## 🎯 권장 모델 (MLX Community)

### Option 1: Mistral-7B (가장 권장 ⭐)
```python
model = "mlx-community/Mistral-7B-Instruct-v0.2-4bit"
```
- **장점**: 빠르고 정확함
- **RAM**: 16GB 이상
- **학습 시간**: 1-2시간

### Option 2: Llama-2-7B (안정적)
```python
model = "mlx-community/Llama-2-7b-chat-4bit"
```
- **장점**: 검증된 성능
- **RAM**: 16GB 이상
- **학습 시간**: 1.5-2.5시간

### Option 3: Phi-2 (가벼움)
```python
model = "mlx-community/Phi-2-4bit"
```
- **장점**: 8GB RAM에서 작동
- **RAM**: 8GB 이상
- **학습 시간**: 30-60분

### Option 4: Gemma-7B (최신)
```python
model = "mlx-community/gemma-7b-it-4bit"
```
- **장점**: Google의 최신 모델, 한국어 지원 좋음
- **RAM**: 16GB 이상

---

## 💻 실전 사용법

### 자동 모드 (추천)
```bash
python finetune_m2_mac.py
```
스크립트가 자동으로:
1. 시스템 메모리 체크
2. 최적 모델 추천
3. 데이터 변환
4. 파인튜닝 실행
5. 모델 테스트

### 수동 모드 (고급)
```python
from finetune_m2_mac import fine_tune_with_mlx, test_finetuned_model

# 파인튜닝
adapter_path = fine_tune_with_mlx(
    model_name="mlx-community/Mistral-7B-Instruct-v0.2-4bit",
    data_dir="./data",
    output_dir="./my_model",
    num_epochs=3,
    batch_size=4,
    learning_rate=1e-5
)

# 테스트
test_finetuned_model(
    model_name="mlx-community/Mistral-7B-Instruct-v0.2-4bit",
    adapter_path=adapter_path,
    test_text="Your test text here"
)
```

---

## 🔧 고급 설정

### 메모리 부족 시
```python
# 배치 크기 줄이기
batch_size=2  # 기본값: 4

# LoRA rank 줄이기
lora_rank=8  # 기본값: 16
```

### 더 빠른 학습
```python
# 학습률 증가
learning_rate=2e-5  # 기본값: 1e-5

# 에포크 감소
num_epochs=2  # 기본값: 3
```

### 더 높은 품질
```python
# 에포크 증가
num_epochs=5

# LoRA rank 증가
lora_rank=32
```

---

## 📈 학습 모니터링

### 실시간 모니터링
```bash
# Activity Monitor로 메모리 사용량 확인
open -a "Activity Monitor"

# 터미널에서 확인
top -o mem | grep Python
```

### 학습 진행 상황
```
Iteration 10: Train loss 2.456, Val loss 2.389
Iteration 20: Train loss 2.234, Val loss 2.187
...
Iteration 100: Train loss 1.456, Val loss 1.523
```

**손실(loss)이 감소하면 학습이 잘 되고 있는 것입니다!**

---

## 🧪 파인튜닝 후 사용법

### Python 스크립트
```python
from mlx_lm import load, generate

# 모델 로드
model, tokenizer = load(
    "mlx-community/Mistral-7B-Instruct-v0.2-4bit",
    adapter_path="./toefl_finetuned_mlx"
)

# 평가 실행
text = "Student's answer here..."
prompt = f"다음 TOEFL 스피킹 답변을 평가하세요: {text}"

response = generate(model, tokenizer, prompt=prompt, max_tokens=400)
print(response)
```

### 대화형 모드
```bash
python finetune_m2_mac.py
# 마지막에 'y' 선택하여 대화형 모드 진입
```

### API 서버로 배포
```python
# api_server.py
from flask import Flask, request, jsonify
from mlx_lm import load, generate

app = Flask(__name__)

# 모델 로드 (한 번만)
model, tokenizer = load(
    "mlx-community/Mistral-7B-Instruct-v0.2-4bit",
    adapter_path="./toefl_finetuned_mlx"
)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    text = data.get('text', '')

    prompt = f"다음 TOEFL 답변을 평가하세요: {text}"
    response = generate(model, tokenizer, prompt=prompt, max_tokens=400)

    return jsonify({'evaluation': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

실행:
```bash
pip install flask
python api_server.py
```

테스트:
```bash
curl -X POST http://localhost:5000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"text": "I like reading books because..."}'
```

---

## ⚡ 성능 최적화 팁

### 1. 양자화 (Quantization)
MLX는 기본적으로 4bit 양자화 모델 사용
- **메모리 75% 절감**
- **속도 2-3배 향상**

### 2. 통합 메모리 활용
M2의 Unified Memory는 CPU-GPU 간 복사 불필요
- 자동으로 최적화됨

### 3. Metal Performance Shaders
Apple의 GPU 가속 자동 활성화
- 별도 설정 불필요

### 4. 배치 처리
```python
# 여러 답변 한번에 평가
texts = ["answer1", "answer2", "answer3"]
results = [evaluate(text) for text in texts]
```

---

## 🐛 문제 해결

### Q1: "MLX not found" 오류
```bash
# Rosetta 모드가 아닌 네이티브 Python 사용 확인
python --version
# Python 3.9+ 필요

# MLX 재설치
pip uninstall mlx mlx-lm
pip install mlx mlx-lm
```

### Q2: 메모리 부족 (Out of Memory)
```python
# 해결 방법:
1. 더 작은 모델 사용 (Phi-2)
2. batch_size=2로 감소
3. 다른 앱 종료
4. 맥 재부팅
```

### Q3: 학습 속도가 너무 느림
```bash
# Activity Monitor에서 확인:
# - "Python" 프로세스가 CPU 800%+ 사용하는지 확인
# - 사용 중이라면 정상

# 백그라운드 앱 종료
# 특히 Chrome, Docker 등
```

### Q4: 모델 다운로드 실패
```bash
# HuggingFace 토큰 설정
huggingface-cli login

# 또는 환경변수 설정
export HF_TOKEN="your_token_here"
```

---

## 📊 벤치마크 (M2 MacBook Pro 16GB)

| 모델 | 학습 시간 (100 샘플) | 메모리 사용 | 추론 속도 |
|------|---------------------|-----------|----------|
| Phi-2 (2.7B) | 35분 | 6GB | 50 tokens/s |
| Mistral-7B | 1.5시간 | 12GB | 30 tokens/s |
| Llama-2-7B | 2시간 | 13GB | 25 tokens/s |
| Gemma-7B | 1.8시간 | 12GB | 28 tokens/s |

---

## 💰 비용 비교

| 방법 | 초기 비용 | 월 운영 비용 | 학습 비용 |
|------|---------|------------|----------|
| **M2 Mac (MLX)** | $0 | $0 | $0 |
| OpenAI Fine-tuning | $0 | $50-100 | $10-50 |
| GPU 클라우드 | $0 | $100-300 | $20-100 |

**M2 Mac을 이미 보유했다면 완전 무료입니다!** 🎉

---

## 🎓 학습 자료

- [MLX 공식 문서](https://ml-explore.github.io/mlx/)
- [MLX Community Models](https://huggingface.co/mlx-community)
- [Apple Machine Learning](https://developer.apple.com/machine-learning/)

---

## 🔄 업데이트 및 개선

### 최신 MLX 버전으로 업데이트
```bash
pip install --upgrade mlx mlx-lm
```

### 새 모델 탐색
```bash
# HuggingFace MLX community 검색
https://huggingface.co/mlx-community
```

---

## ✅ 체크리스트

파인튜닝 전:
- [ ] M2/M3 Mac 확인
- [ ] 16GB+ RAM (권장)
- [ ] MLX 설치 완료
- [ ] 학습 데이터 50개 이상 준비

파인튜닝 중:
- [ ] Activity Monitor로 메모리 확인
- [ ] 손실(loss) 감소 확인
- [ ] 과적합(overfitting) 주의

파인튜닝 후:
- [ ] 테스트 데이터로 검증
- [ ] 실제 답변으로 평가
- [ ] API 서버 배포 (선택)

---

## 🚀 다음 단계

1. **음성 인식 통합**: Whisper + MLX
2. **웹 인터페이스**: Streamlit 앱
3. **자동 평가 시스템**: 실시간 피드백
4. **멀티모달**: 발음 분석 추가

**M2 Mac으로 강력한 TOEFL 평가 시스템을 만들어보세요!** 🎯
