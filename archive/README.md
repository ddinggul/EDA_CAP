# 📚 Archive - 참고 자료

파인튜닝 관련 참고 문서 및 스크립트

---

## 📋 내용물

이 폴더에는 **LLM 파인튜닝** 관련 자료가 보관되어 있습니다.
현재 프로젝트는 **웹 서버 운영**과 **데이터셋 준비**에 집중하고 있으므로,
파인튜닝이 필요할 경우에만 참고하세요.

---

## 📖 가이드 문서

### 🍎 M2 Mac 관련
- **M2_MAC_SETUP.md** - M2 Mac에서 MLX 파인튜닝 상세 가이드
- **QUICKSTART_M2.md** - 5분 빠른 시작 가이드

### 🎓 파인튜닝 이론
- **FINETUNING_GUIDE.md** - LLM 파인튜닝 완벽 가이드
- **README_TOEFL_FINETUNING.md** - TOEFL 평가 파인튜닝 개요

### 🎤 음성 평가
- **AUDIO_MULTIMODAL_GUIDE.md** - 음성 기반 멀티모달 평가 가이드

### 🔧 기타
- **CLOVA_SPEECH_GUIDE.md** - Naver CLOVA Speech API 가이드
- **SETUP_GUIDE.md** - 일반 설정 가이드

---

## 🚀 파인튜닝 스크립트

### M2 Mac (MLX)
- **finetune_m2_mac.py** - Apple Silicon 최적화 파인튜닝
- **setup_m2.sh** - M2 Mac 자동 설치 스크립트
- **requirements_m2.txt** - M2 Mac 패키지

### GPU 서버
- **finetune_huggingface.py** - HuggingFace 모델 파인튜닝
- **requirements_finetuning.txt** - GPU 서버 패키지

### OpenAI
- **finetune_openai.py** - OpenAI GPT 파인튜닝

---

## 🎯 사용 시기

### LLM 파인튜닝이 필요한 경우

1. **초기 모델 학습**: 처음으로 TOEFL 평가 모델을 만들 때
2. **모델 개선**: 기존 모델의 성능을 향상시킬 때
3. **도메인 적응**: 새로운 평가 기준이나 스타일 적용

### 파인튜닝 방법

#### Option 1: M2 Mac (무료, 로컬)
```bash
# 가이드 참고
cat M2_MAC_SETUP.md

# 실행
python finetune_m2_mac.py
```

#### Option 2: GPU 서버 (RunPod, Colab)
```bash
# 가이드 참고
cat FINETUNING_GUIDE.md

# 실행
python finetune_huggingface.py
```

#### Option 3: OpenAI (간단, 유료)
```bash
# 실행
python finetune_openai.py
```

---

## 📚 권장 읽기 순서

1. **FINETUNING_GUIDE.md** - 파인튜닝 이론 이해
2. **M2_MAC_SETUP.md** 또는 **AUDIO_MULTIMODAL_GUIDE.md** - 실전 가이드
3. 해당 스크립트 실행

---

## ⚠️ 주의사항

- 이 파일들은 **참고용**입니다
- 실제 프로젝트는 **상위 폴더**에서 실행하세요
- 파인튜닝은 **데이터 준비 후** 필요시에만 진행

---

## 🔗 메인 프로젝트로 돌아가기

```bash
cd ..
cat README.md
```

---

**필요할 때 참고하세요!** 📖
