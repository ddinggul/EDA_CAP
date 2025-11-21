# 🎤 음성 기반 TOEFL 평가 시스템 가이드

음성 파일(WAV) + 대본 + 피드백을 활용한 멀티모달 파인튜닝

---

## 📊 시스템 구조

```
[학생 음성 WAV] ──┬─→ [MFCC/음성 특징 추출] ─→ [LSTM 모델] ─→ 발음/유창성 점수
                  │                                              ↓
[대본/피드백] ─────┴──────────────────────────→ [LLM (Mistral)] ─→ 종합 평가
                                                               ↗
                                                    내용/문법 평가
```

### 모델 구성
1. **음성 분석 모델** (LSTM)
   - 입력: MFCC, Pitch, Energy 등 음성 특징
   - 출력: 발음 점수, 유창성 점수 (0-4점)

2. **LLM 모델** (Mistral-7B)
   - 입력: 대본 + 음성 점수
   - 출력: 내용/문법 평가 + 종합 피드백

---

## 🚀 빠른 시작 (4단계)

### 전제 조건
```
데이터 구조:
/audio/
  ├── student_1.wav
  ├── student_2.wav
  └── ...
feedback.csv (파일이름, 텍스트, 피드백, 점수 컬럼)
```

### 1단계: 음성 특징 추출 (10분)
```bash
python audio_feature_extraction.py \
  --audio_dir ./audio \
  --csv feedback.csv \
  --output audio_features.jsonl
```

**출력**: `audio_features.jsonl` (MFCC, Pitch 등 음성 특징)

### 2단계: 음성 모델 학습 (GPU 서버, 30분-1시간)
```bash
python train_audio_model.py \
  --data audio_features.jsonl \
  --output ./audio_model \
  --epochs 100 \
  --batch_size 32
```

**출력**: `./audio_model/` (발음/유창성 예측 모델)

### 3단계: LLM 파인튜닝 (GPU 서버, 1-2시간)
```bash
# 데이터 준비
python prepare_training_data.py

# 파인튜닝 (HuggingFace on GPU)
python finetune_huggingface.py
```

**출력**: `./toefl_finetuned_model/` (내용/문법 평가 LLM)

### 4단계: 통합 평가 시스템 실행
```bash
# 단일 평가
python integrated_evaluation_system.py \
  --audio ./audio/student_1.wav \
  --transcript "I prefer studying subjects that interest me..." \
  --audio_model ./audio_model \
  --llm_type mlx

# 일괄 평가
python integrated_evaluation_system.py \
  --batch \
  --audio_dir ./audio \
  --csv feedback.csv
```

---

## 📁 데이터 준비

### CSV 형식
```csv
파일 이름,텍스트,텍스트 피드백,발음,fluency,내용,문법/표현,total_score
Q1 학생A,"I prefer studying...",#발음: R/L구분,3.0,3.5,3.2,2.8,3.1
Q2 학생B,"University announced...",#표현: 적절,3.5,3.0,3.8,3.2,3.4
```

### 음성 파일
- **포맷**: WAV (권장), MP3
- **샘플레이트**: 16kHz (권장)
- **비트레이트**: 16-bit
- **길이**: 30초 - 2분

---

## 🔬 음성 특징 상세

### 1. MFCC (Mel-frequency cepstral coefficients)
- **용도**: 발음 분석
- **특징**: 13차원 MFCC + Delta + Delta-Delta
- **분석**: 자음/모음 명확성, 음소 정확도

### 2. Prosody (운율)
- **Pitch (F0)**: 억양, 톤
- **Energy**: 음량, 강조
- **Tempo**: 말하기 속도
- **용도**: 유창성 분석

### 3. Fluency (유창성)
- **Pause Detection**: 휴지 빈도/길이
- **Speech Rate**: 발화 속도
- **Articulation Rate**: 음절 속도
- **용도**: 말더듬, 자연스러움

### 4. Pronunciation (발음)
- **Spectral Contrast**: 자음 명확성
- **Chroma**: 음높이 정확도
- **Formants**: 모음 분석
- **용도**: R/L 구분, 장단모음

---

## 🎯 모델 학습 전략

### Option A: 별도 학습 (권장 ⭐)
```
1. 음성 모델 (LSTM) 학습 → 발음/유창성
2. LLM 파인튜닝 → 내용/문법
3. 추론 시 결합
```

**장점**:
- 각 모델 독립적 개선
- 학습 간단
- 디버깅 용이

### Option B: End-to-End 학습
```
음성 특징 → [Audio Encoder] → [LLM] → 종합 평가
```

**장점**:
- 완전 통합
- 더 나은 성능 (이론적)

**단점**:
- 복잡함
- 데이터 많이 필요 (1000+)

---

## 💻 GPU 서버 학습 가이드

### 클라우드 GPU 옵션
1. **Google Colab** (무료/Pro)
   - 무료: T4 GPU (제한적)
   - Pro ($10/월): V100, 더 긴 시간

2. **Paperspace Gradient** (저렴)
   - P5000 GPU: $0.51/시간
   - RTX 4000: $0.56/시간

3. **RunPod** (가장 저렴)
   - RTX 3090: $0.34/시간
   - A100: $1.39/시간

4. **Lambda Labs**
   - A100: $1.10/시간

### Google Colab에서 실행

```python
# Colab 노트북
!git clone https://github.com/your-repo
%cd EDA_CAP

# 패키지 설치
!pip install -r requirements_finetuning.txt

# 데이터 업로드 (Google Drive)
from google.colab import drive
drive.mount('/content/drive')

# 1. 음성 특징 추출
!python audio_feature_extraction.py \
  --audio_dir /content/drive/MyDrive/audio \
  --csv /content/drive/MyDrive/feedback.csv

# 2. 음성 모델 학습
!python train_audio_model.py \
  --data audio_features.jsonl \
  --epochs 100

# 3. LLM 파인튜닝
!python finetune_huggingface.py

# 결과 다운로드
!zip -r models.zip audio_model toefl_finetuned_model
```

---

## 🧪 평가 및 테스트

### 단일 평가
```python
from integrated_evaluation_system import IntegratedTOEFLEvaluator

# 시스템 초기화
evaluator = IntegratedTOEFLEvaluator(
    audio_model_dir="./audio_model",
    llm_type="mlx",
    llm_model="mlx-community/Mistral-7B-Instruct-v0.2-4bit",
    llm_adapter_path="./toefl_finetuned_mlx"
)

# 평가 실행
result = evaluator.evaluate_complete(
    audio_path="student_1.wav",
    transcript="I prefer studying subjects that interest me..."
)

print(f"발음: {result['pronunciation_score']:.2f}/4.0")
print(f"유창성: {result['fluency_score']:.2f}/4.0")
print(result['content_evaluation'])
```

### 일괄 평가
```python
results = evaluator.batch_evaluate(
    audio_dir="./audio",
    csv_path="feedback.csv",
    output_path="results.jsonl"
)
```

---

## 📊 성능 분석

### 음성 모델 평가
```python
import json
import numpy as np

# 예측 vs 실제
with open('audio_features.jsonl', 'r') as f:
    data = [json.loads(line) for line in f]

predictions = []
ground_truth = []

for item in data:
    # 예측 실행
    pred = predict_audio_scores(item['audio_features'])
    predictions.append([pred['pronunciation'], pred['fluency']])

    # 실제 점수
    gt = item['ground_truth']
    ground_truth.append([gt['pronunciation_score'], gt['fluency_score']])

# RMSE 계산
rmse = np.sqrt(np.mean((np.array(predictions) - np.array(ground_truth))**2))
print(f"RMSE: {rmse:.3f}")
```

### LLM 평가
- Human evaluation (사람이 직접 평가)
- BLEU score (피드백 텍스트 유사도)
- Correlation with human scores (점수 상관관계)

---

## 🎓 학습 팁

### 데이터 증강
```python
# 음성 데이터 증강
import librosa
import numpy as np

def augment_audio(audio_path):
    y, sr = librosa.load(audio_path)

    # 1. 속도 변경 (0.9x - 1.1x)
    y_fast = librosa.effects.time_stretch(y, rate=1.1)
    y_slow = librosa.effects.time_stretch(y, rate=0.9)

    # 2. 피치 변경 (+/- 2 semitones)
    y_high = librosa.effects.pitch_shift(y, sr=sr, n_steps=2)
    y_low = librosa.effects.pitch_shift(y, sr=sr, n_steps=-2)

    # 3. 노이즈 추가
    noise = np.random.randn(len(y)) * 0.005
    y_noise = y + noise

    return [y, y_fast, y_slow, y_high, y_low, y_noise]
```

### Transfer Learning
```python
# 사전학습 모델 활용
# 1. Wav2Vec2 (음성 특징)
from transformers import Wav2Vec2Processor, Wav2Vec2Model

processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")

# 2. Whisper (음성 인식)
import whisper
model = whisper.load_model("base")
result = model.transcribe("audio.wav")
```

---

## 🔧 문제 해결

### Q1: 음성 특징 추출이 너무 느림
**A**: 멀티프로세싱 사용
```python
from multiprocessing import Pool

def process_file(audio_path):
    return extractor.extract_all_features(audio_path)

with Pool(8) as p:
    results = p.map(process_file, audio_files)
```

### Q2: LSTM 모델 과적합
**A**:
- Dropout 증가 (0.3 → 0.5)
- L2 regularization 추가
- 데이터 증강
- Early stopping

### Q3: GPU 메모리 부족
**A**:
- Batch size 감소 (32 → 16)
- Gradient accumulation 사용
- Mixed precision training (fp16)

---

## 📦 필요 패키지

```bash
# 음성 처리
pip install librosa soundfile

# 딥러닝
pip install torch torchvision torchaudio
pip install transformers datasets

# 음성 인식 (선택)
pip install openai-whisper

# MLX (M2 Mac)
pip install mlx mlx-lm

# 기타
pip install pandas numpy scikit-learn
```

---

## 🎯 실전 워크플로우

### 개발 단계
```bash
# 1. 소규모 데이터로 테스트 (10-20개)
python audio_feature_extraction.py --audio_dir ./sample --csv sample.csv

# 2. 음성 모델 프로토타입 (적은 epochs)
python train_audio_model.py --data sample_features.jsonl --epochs 20

# 3. 통합 시스템 테스트
python integrated_evaluation_system.py --audio sample.wav --transcript "..."
```

### 프로덕션 단계
```bash
# 1. 전체 데이터 특징 추출
python audio_feature_extraction.py --audio_dir ./all_audio --csv all_feedback.csv

# 2. GPU 서버에서 음성 모델 학습
python train_audio_model.py --data audio_features.jsonl --epochs 100

# 3. GPU 서버에서 LLM 파인튜닝
python finetune_huggingface.py

# 4. M2 Mac으로 모델 다운로드 및 배포
python integrated_evaluation_system.py --batch --audio_dir ./test --csv test.csv
```

---

## 📈 예상 성능

### 데이터 규모별 성능
| 데이터 수 | 음성 모델 RMSE | LLM 품질 | 학습 시간 |
|----------|--------------|---------|----------|
| 50개 | 0.8-1.0 | ⭐⭐⭐ | 30분 |
| 200개 | 0.5-0.7 | ⭐⭐⭐⭐ | 1-2시간 |
| 500개+ | 0.3-0.5 | ⭐⭐⭐⭐⭐ | 3-4시간 |

---

## ✅ 체크리스트

준비:
- [ ] WAV 파일 50개 이상
- [ ] CSV 파일 (대본 + 피드백)
- [ ] GPU 서버 준비 (Colab/RunPod 등)

학습:
- [ ] 음성 특징 추출 완료
- [ ] 음성 모델 학습 완료 (RMSE < 0.7)
- [ ] LLM 파인튜닝 완료
- [ ] 통합 시스템 테스트

배포:
- [ ] M2 Mac에서 추론 테스트
- [ ] API 서버 구축 (선택)
- [ ] 웹 인터페이스 (선택)

---

**음성 기반 평가로 더 정확하고 실용적인 TOEFL 시스템을 만드세요!** 🎤🎓
