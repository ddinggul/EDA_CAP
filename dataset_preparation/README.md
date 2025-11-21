# 📊 데이터셋 준비 가이드

MFCC 음성 특징 추출 → OpenAI GPT 파인튜닝 데이터 생성

---

## 🎯 목적

100개 학습 데이터 (45초 50개 + 60초 50개)를 활용하여:
1. WAV 파일에서 MFCC 음성 특징 추출
2. CSV에 음성 특징 추가
3. OpenAI GPT 파인튜닝 데이터 생성

---

## 📁 파일 구조

```
dataset_preparation/
├── extract_audio_features.py       # MFCC 특징 추출
├── prepare_openai_finetuning.py   # GPT 학습 데이터 생성
└── README.md                       # 이 파일
```

---

## 🚀 전체 워크플로우

### 1단계: 음성 특징 추출

```bash
python extract_audio_features.py \
  --audio_dir ../audio \
  --csv ../feedback.csv \
  --output feedback_with_features.csv
```

**입력:**
- `../audio/*.wav`: 100개 WAV 파일
- `../feedback.csv`: 기존 피드백

**출력:**
- `feedback_with_features.csv`: 음성 특징이 추가된 CSV

**추출되는 특징:**
- MFCC (13차원 평균/표준편차)
- Pitch (평균, 표준편차)
- Energy (평균, 표준편차)
- 말하기 속도 (speech_rate)
- 휴지 (pause 횟수, 평균 길이)
- Spectral Centroid
- Tempo

---

### 2단계: OpenAI 파인튜닝 데이터 생성

```bash
python prepare_openai_finetuning.py \
  --csv feedback_with_features.csv \
  --output openai_training_data.jsonl
```

**입력:**
- `feedback_with_features.csv`: 음성 특징 포함 CSV

**출력:**
- `openai_training_data.jsonl`: OpenAI 파인튜닝 형식

---

## 📊 데이터 형식

### 기존 CSV (`feedback.csv`)
```csv
텍스트,파일 이름,텍스트 피드백,발음,fluency,내용,문법/표현,total_score
"I prefer studying...","Q1 학생A","#발음: R/L구분","개별 음소 정확성 양호","자연스러운 속도, 적절한 휴지",3.2,2.8,3.1
```

**주의:** `발음`, `fluency` 컬럼은 **교사의 텍스트 피드백**이며 점수가 아닙니다.

### 음성 특징 추가 CSV (`feedback_with_features.csv`)
```csv
텍스트,파일 이름,...,audio_duration,pitch_mean,pitch_std,energy_mean,num_pauses,pause_mean,speech_rate,audio_summary
"I prefer...",Q1 학생A,...,45.2,150.3,30.5,0.045,5,0.8,3.2,"음성 특징 분석: 길이 45.2초..."
```

### OpenAI 학습 데이터 (`openai_training_data.jsonl`)
```json
{
  "messages": [
    {
      "role": "system",
      "content": "당신은 TOEFL 스피킹 평가 전문가입니다..."
    },
    {
      "role": "user",
      "content": "학생 답변: I prefer...\n\n음성 특징 분석:\n- 길이: 45.2초\n- Pitch: 150.3Hz\n- 휴지: 5회..."
    },
    {
      "role": "assistant",
      "content": "평가 결과:\n\n**내용: 3.2/4.0**\n**문법: 2.8/4.0**\n**발음:** 개별 음소 정확성 양호\n**유창성:** 자연스러운 속도..."
    }
  ]
}
```

---

## 🎓 상세 사용법

### extract_audio_features.py

**기본 사용:**
```bash
python extract_audio_features.py \
  --audio_dir ../audio \
  --csv ../feedback.csv
```

**옵션:**
- `--audio_dir`: WAV 파일 디렉토리 (필수)
- `--csv`: 기존 피드백 CSV (필수)
- `--output`: 출력 CSV 파일명 (기본: `feedback_with_features.csv`)

**파일 매칭:**
- WAV 파일명의 stem (확장자 제외)
- CSV의 '파일 이름' 컬럼에 포함된 문자열
- 예: `student_1.wav` → '파일 이름'에 `student_1` 포함

**출력 컬럼:**
```python
'audio_duration'           # 길이 (초)
'pitch_mean'              # 평균 Pitch (Hz)
'pitch_std'               # Pitch 표준편차
'energy_mean'             # 평균 Energy
'num_pauses'              # 휴지 횟수
'pause_mean'              # 평균 휴지 길이 (초)
'speech_rate'             # 말하기 속도 (구간/초)
'audio_summary'           # 텍스트 요약
```

---

### prepare_openai_finetuning.py

**기본 사용:**
```bash
python prepare_openai_finetuning.py \
  --csv feedback_with_features.csv
```

**옵션:**
- `--csv`: 피드백 CSV (음성 특징 포함) (필수)
- `--output`: 출력 JSONL 파일명 (기본: `openai_training_data.jsonl`)
- `--no_audio_features`: 음성 특징 제외 (텍스트만)

**생성되는 학습 데이터:**
- 시스템 프롬프트: TOEFL 평가 전문가
- 사용자 입력:
  - 학생 답변 텍스트
  - Clova API 발음/유창성 점수 (시뮬레이션)
  - 음성 특징 요약 (MFCC, Pitch, Pause 등)
- 모델 응답:
  - 내용/문법 평가
  - 피드백
  - 개선 방향

---

## 💡 음성 특징 활용

### GPT가 학습하는 정보

1. **텍스트 정보**
   - 학생의 답변 내용
   - 문법, 어휘 사용

2. **교사 평가 피드백**
   - 발음 피드백 (텍스트 설명)
   - 유창성 피드백 (텍스트 설명)
   - 내용/문법 점수 (0-4점)

3. **MFCC 음성 특징** ⭐
   - 말하기 속도 → 유창성 판단
   - 휴지 패턴 → 말더듬 감지
   - Pitch 변동 → 억양 평가
   - Energy → 음량 안정성

### 예시 학습 데이터

**입력 (GPT에게 제공):**
```
학생 답변:
I prefer studying subjects that interest me because...

음성 특징 분석:
- 길이: 45.2초
- 말하기 속도: 3.2 구간/초
- 평균 Pitch: 150.3Hz (변동: 30.5)
- 휴지: 5회, 평균 0.8초
- MFCC[0-2]: [12.45, -2.30, 5.67]

특징 해석:
- Pitch 변동 많음 → 풍부한 억양
```

**출력 (GPT가 생성, 교사 피드백 기반):**
```
평가 결과:

**내용: 3.2/4.0**
- 명확한 주장과 이유 제시
- 논리적 구조 양호

**문법: 2.8/4.0**
- 대체로 정확한 문법
- 일부 관사 누락

**발음:**
개별 음소 정확성 양호, R/L 구분 연습 필요

**유창성:**
자연스러운 속도, 적절한 휴지

**종합 점수: 3.1/4.0**

**음성 특징 기반 개선 방향:**
- 억양이 풍부하여 표현력이 좋음
- 휴지 패턴 양호
```

---

## 🔍 검증 및 디버깅

### CSV 매칭 확인
```bash
python extract_audio_features.py \
  --audio_dir ../audio \
  --csv ../feedback.csv

# 출력에서 "✅ 매칭됨" 확인
# "⚠️ 매칭 실패" 있으면 파일명 조정
```

### JSONL 데이터 검증
```bash
python prepare_openai_finetuning.py \
  --csv feedback_with_features.csv

# 자동으로 검증 수행
# "✅ 모든 데이터가 OpenAI 형식에 맞습니다" 확인
```

### 수동 확인
```bash
# 첫 번째 샘플 확인
head -1 openai_training_data.jsonl | python -m json.tool

# 샘플 개수 확인
wc -l openai_training_data.jsonl
```

---

## 📈 예상 결과

### 100개 샘플 기준

**음성 특징 추출:**
- 처리 시간: ~5-10분
- 출력: `feedback_with_features.csv` (100행)

**파인튜닝 데이터:**
- 샘플 수: 100개
- 평균 토큰/샘플: ~500-800
- 총 토큰: ~50,000-80,000
- 학습 비용: ~$5-10

---

## 🐛 문제 해결

### Q1: "CSV에서 매칭 실패"
**A**: 파일명 규칙 확인
```python
# extract_audio_features.py에서
# 매칭 로직 수정 (line ~120):
file_id = audio_file.stem  # "student_1"
matching_rows = df[df['파일 이름'].str.contains(file_id, na=False)]

# 또는 정확히 일치:
# matching_rows = df[df['파일 이름'] == file_id]
```

### Q2: "음성 특징이 CSV에 없습니다"
**A**: 1단계를 먼저 실행
```bash
python extract_audio_features.py --audio_dir ../audio --csv ../feedback.csv
```

### Q3: librosa 설치 오류
**A**:
```bash
pip install librosa soundfile
# macOS에서 soundfile 오류 시:
brew install libsndfile
```

---

## 🎯 다음 단계

1. **데이터 생성 완료 후:**
   ```bash
   ls -lh feedback_with_features.csv
   ls -lh openai_training_data.jsonl
   ```

2. **OpenAI 파인튜닝:**
   ```bash
   # CLI
   openai api fine_tunes.create \
     -t openai_training_data.jsonl \
     -m gpt-3.5-turbo

   # 또는 웹
   # https://platform.openai.com/finetune
   ```

3. **파인튜닝 모델 사용:**
   ```bash
   cd ..
   python toefl_evaluator.py \
     --audio student.wav \
     --model ft:gpt-3.5-turbo:your-org:model-id
   ```

---

## 💡 팁

### 데이터 증강 (선택)
```bash
# 45초 + 60초 샘플 각각 확인
grep "45" feedback_with_features.csv | wc -l
grep "60" feedback_with_features.csv | wc -l
```

### 특징 분석
```bash
# 음성 특징 통계
python -c "
import pandas as pd
df = pd.read_csv('feedback_with_features.csv')
print(df[['audio_duration', 'pitch_mean', 'num_pauses']].describe())
"
```

---

**MFCC 음성 특징으로 더 정확한 GPT 파인튜닝을 하세요!** 🎤📊
