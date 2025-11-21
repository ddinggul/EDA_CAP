# 📁 프로젝트 구조

TOEFL 스피킹 평가 시스템 - 전체 파일 구조 및 사용 가이드

---

## 🗂️ 폴더 구조

```
EDA_CAP/
│
├── 📂 dataset_preparation/          # 데이터셋 준비 도구 ⭐
│   ├── README.md                    # 데이터셋 준비 가이드
│   ├── audio_feature_extraction.py  # 음성 특징 추출 (MFCC, Pitch 등)
│   ├── train_audio_model.py         # 음성 평가 모델 학습 (LSTM)
│   ├── prepare_training_data.py     # LLM 파인튜닝 데이터 변환
│   └── create_full_dataset.py       # 전체 파이프라인 통합 스크립트
│
├── 📂 models/                       # 학습된 모델 저장 (생성됨)
│   ├── audio_model/                 # LSTM 발음/유창성 모델
│   └── toefl_finetuned_mlx/         # 파인튜닝된 LLM
│
├── 📂 processed_data/               # 처리된 데이터 (생성됨)
│   ├── audio_features.jsonl         # 음성 특징
│   └── training_data_*.jsonl        # LLM 학습 데이터
│
├── 🎓 파인튜닝 스크립트
│   ├── finetune_m2_mac.py          # M2 Mac 최적화 파인튜닝 (MLX)
│   ├── finetune_huggingface.py     # HuggingFace 모델 파인튜닝 (GPU)
│   └── finetune_openai.py          # OpenAI GPT 파인튜닝
│
├── 🚀 실행 스크립트
│   ├── integrated_evaluation_system.py  # 통합 평가 시스템 ⭐⭐⭐
│   ├── api_server_mlx.py                # REST API 서버
│   └── setup_m2.sh                      # M2 Mac 자동 설치
│
├── 📖 가이드 문서
│   ├── QUICKSTART_M2.md            # 🚀 5분 빠른 시작
│   ├── M2_MAC_SETUP.md             # M2 Mac 상세 가이드
│   ├── AUDIO_MULTIMODAL_GUIDE.md   # 음성 기반 평가 가이드
│   ├── FINETUNING_GUIDE.md         # 파인튜닝 이론 및 가이드
│   ├── PROJECT_STRUCTURE.md        # 이 파일
│   └── README_TOEFL_FINETUNING.md  # 프로젝트 개요
│
├── ⚙️ 설정 파일
│   ├── requirements_m2.txt         # M2 Mac 패키지
│   ├── requirements_audio.txt      # 음성 처리 패키지
│   ├── requirements_finetuning.txt # 일반 파인튜닝 패키지
│   └── toefl_evaluations_template.csv  # CSV 템플릿
│
└── 📊 데이터 (사용자 준비)
    ├── audio/                      # WAV 파일들
    │   ├── student_1.wav
    │   ├── student_2.wav
    │   └── ...
    └── feedback.csv                # 대본 + 피드백
```

---

## 🎯 시스템 구성

### 1️⃣ 데이터 준비 단계 (`dataset_preparation/`)

```bash
# 전체 자동화
cd dataset_preparation
python create_full_dataset.py \
  --audio_dir ../audio \
  --csv ../feedback.csv \
  --train_audio_model
```

**출력**:
- `processed_data/audio_features.jsonl`: 음성 특징
- `models/audio_model/`: LSTM 모델
- `processed_data/training_data_*.jsonl`: LLM 데이터

---

### 2️⃣ 모델 학습 단계 (GPU 서버)

#### Option A: M2 Mac (MLX)
```bash
python finetune_m2_mac.py
# → models/toefl_finetuned_mlx/
```

#### Option B: GPU 서버 (HuggingFace)
```bash
python finetune_huggingface.py
# → models/toefl_finetuned_model/
```

---

### 3️⃣ 평가/배포 단계 (M2 Mac)

#### 통합 평가 시스템
```bash
python integrated_evaluation_system.py \
  --audio student.wav \
  --transcript "I prefer studying..." \
  --audio_model ./models/audio_model \
  --llm_type mlx
```

#### API 서버
```bash
python api_server_mlx.py
# → http://localhost:5000
```

---

## 🚀 빠른 시작 시나리오

### 시나리오 1: 처음부터 끝까지 (추천)

```bash
# 1. 설치
./setup_m2.sh

# 2. 데이터 준비 (음성 특징 + 음성 모델 + LLM 데이터)
cd dataset_preparation
python create_full_dataset.py \
  --audio_dir ../audio \
  --csv ../feedback.csv \
  --train_audio_model

# 3. LLM 파인튜닝 (M2 Mac)
cd ..
python finetune_m2_mac.py

# 4. 통합 평가 실행
python integrated_evaluation_system.py \
  --audio audio/test.wav \
  --transcript "Your answer..." \
  --audio_model ./models/audio_model
```

---

### 시나리오 2: GPU 서버 활용

```bash
# === 로컬 (M2 Mac) ===
# 1. 음성 특징만 추출
cd dataset_preparation
python audio_feature_extraction.py \
  --audio_dir ../audio \
  --csv ../feedback.csv

# 2. LLM 데이터 준비
python prepare_training_data.py

# 3. GPU 서버로 업로드
scp audio_features.jsonl user@gpu-server:/workspace/
scp training_data_huggingface.jsonl user@gpu-server:/workspace/

# === GPU 서버 ===
# 4. 음성 모델 학습
python train_audio_model.py \
  --data audio_features.jsonl \
  --epochs 100

# 5. LLM 파인튜닝
python finetune_huggingface.py

# 6. 모델 다운로드
scp -r user@gpu-server:/workspace/models ./

# === 로컬 (M2 Mac) ===
# 7. 통합 평가
python integrated_evaluation_system.py --audio test.wav ...
```

---

### 시나리오 3: LLM만 파인튜닝

```bash
# 음성 분석은 기존 모델 사용, LLM만 파인튜닝
cd dataset_preparation
python create_full_dataset.py \
  --csv ../feedback.csv \
  --only_llm_data \
  --llm_format huggingface

cd ..
python finetune_m2_mac.py
```

---

## 📊 데이터 흐름

```
[원본 데이터]
  ├── audio/student_1.wav
  └── feedback.csv
         │
         ↓
[dataset_preparation/]
         │
         ├─→ audio_feature_extraction.py
         │      ↓
         │   audio_features.jsonl (MFCC, Pitch, Energy...)
         │      ↓
         │   train_audio_model.py
         │      ↓
         │   models/audio_model/ (LSTM 발음/유창성 모델)
         │
         └─→ prepare_training_data.py
                ↓
             training_data_*.jsonl
                ↓
[파인튜닝]
  ├── finetune_m2_mac.py → models/toefl_finetuned_mlx/
  └── finetune_huggingface.py → models/toefl_finetuned_model/
         │
         ↓
[통합 평가]
  integrated_evaluation_system.py
    ├── 음성 → audio_model → 발음/유창성 점수
    └── 텍스트 → LLM → 내용/문법 평가
         │
         ↓
  종합 평가 리포트 (JSON)
```

---

## 🎓 사용 패턴별 가이드

### 패턴 1: 연구/프로토타입 (소규모 데이터)
```bash
# 50-100개 샘플로 빠르게 테스트
cd dataset_preparation
python create_full_dataset.py \
  --audio_dir ../audio \
  --csv ../feedback.csv \
  --audio_epochs 50  # 적은 에포크

# M2 Mac에서 파인튜닝
python ../finetune_m2_mac.py
```

### 패턴 2: 프로덕션 (대규모 데이터)
```bash
# 500+ 샘플로 고품질 모델
# GPU 서버 사용

# 1. 데이터 준비
cd dataset_preparation
python create_full_dataset.py \
  --audio_dir ../audio \
  --csv ../feedback.csv \
  --no_train_audio  # GPU 서버에서 학습

# 2. GPU 서버로 업로드
# 3. GPU 서버에서 학습
python train_audio_model.py --epochs 200
python finetune_huggingface.py

# 4. 모델 다운로드 및 배포
```

### 패턴 3: API 서비스
```bash
# 학습된 모델로 API 서버 실행
python api_server_mlx.py \
  --model mlx-community/Mistral-7B-Instruct-v0.2-4bit \
  --adapter ./models/toefl_finetuned_mlx \
  --port 5000

# 다른 터미널에서 테스트
curl -X POST http://localhost:5000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"text": "I prefer studying..."}'
```

---

## 📚 주요 파일 역할

### 데이터 준비 도구
| 파일 | 역할 | 입력 | 출력 |
|------|------|------|------|
| `audio_feature_extraction.py` | 음성 특징 추출 | WAV + CSV | audio_features.jsonl |
| `train_audio_model.py` | LSTM 모델 학습 | audio_features.jsonl | models/audio_model/ |
| `prepare_training_data.py` | LLM 데이터 변환 | CSV | training_data_*.jsonl |
| `create_full_dataset.py` | 전체 파이프라인 | WAV + CSV | 모든 출력 |

### 파인튜닝 도구
| 파일 | 플랫폼 | 모델 | 특징 |
|------|--------|------|------|
| `finetune_m2_mac.py` | M2 Mac | Mistral-7B | MLX, 무료, 로컬 |
| `finetune_huggingface.py` | GPU 서버 | Llama/Mistral | 오픈소스 |
| `finetune_openai.py` | 클라우드 | GPT-3.5/4 | 간단, 유료 |

### 실행 도구
| 파일 | 역할 | 사용 시기 |
|------|------|----------|
| `integrated_evaluation_system.py` | 통합 평가 | 학습 후 평가 |
| `api_server_mlx.py` | REST API | 서비스 배포 |

---

## 🔧 환경별 설정

### M2 Mac
```bash
# 설치
./setup_m2.sh

# 또는 수동
pip install -r requirements_m2.txt
pip install -r requirements_audio.txt
```

### GPU 서버 (Linux)
```bash
pip install -r requirements_finetuning.txt
pip install -r requirements_audio.txt

# CUDA 확인
python -c "import torch; print(torch.cuda.is_available())"
```

### Google Colab
```python
!pip install -r requirements_audio.txt
!pip install transformers datasets accelerate peft
```

---

## 💡 팁 & 트릭

### 빠른 테스트
```bash
# 샘플 데이터로 전체 파이프라인 테스트
cd dataset_preparation
python create_full_dataset.py \
  --audio_dir ../audio_sample \
  --csv ../feedback_sample.csv \
  --audio_epochs 10  # 빠르게
```

### 증분 업데이트
```bash
# 새 데이터 추가 시
python audio_feature_extraction.py \
  --audio_dir ../audio_new \
  --csv ../feedback_new.csv \
  --output audio_features_new.jsonl

# 병합
cat audio_features.jsonl audio_features_new.jsonl > audio_features_all.jsonl
```

### 디버깅
```bash
# 단계별 확인
python -c "
import json
with open('processed_data/audio_features.jsonl', 'r') as f:
    data = [json.loads(line) for line in f]
    print(f'샘플 수: {len(data)}')
    print(f'첫 샘플 키: {data[0].keys()}')
"
```

---

## 📖 추가 문서

- **빠른 시작**: `QUICKSTART_M2.md`
- **음성 평가**: `AUDIO_MULTIMODAL_GUIDE.md`
- **M2 Mac 설정**: `M2_MAC_SETUP.md`
- **파인튜닝 이론**: `FINETUNING_GUIDE.md`
- **데이터 준비**: `dataset_preparation/README.md`

---

## ✅ 체크리스트

프로젝트 시작:
- [ ] `./setup_m2.sh` 실행
- [ ] `audio/` 폴더에 WAV 파일 준비
- [ ] `feedback.csv` 파일 준비

데이터 준비:
- [ ] `create_full_dataset.py` 실행
- [ ] `audio_features.jsonl` 생성 확인
- [ ] 음성 모델 학습 완료

파인튜닝:
- [ ] LLM 데이터 생성 확인
- [ ] M2 Mac 또는 GPU 서버에서 파인튜닝
- [ ] 모델 저장 확인

배포:
- [ ] 통합 평가 시스템 테스트
- [ ] API 서버 실행 (선택)

---

**체계적인 프로젝트 구조로 효율적인 개발을 하세요!** 🚀
