#!/bin/bash

# M2 Mac TOEFL 평가 시스템 자동 설치 스크립트

echo "================================================"
echo "🍎 M2 Mac TOEFL 평가 시스템 설치"
echo "================================================"
echo ""

# Python 버전 확인
echo "1️⃣  Python 버전 확인..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python $python_version 감지됨"

if [[ ! "$python_version" =~ ^3\.(9|10|11|12) ]]; then
    echo "   ⚠️  Python 3.9 이상 필요합니다."
    echo "   Homebrew로 설치: brew install python@3.11"
    exit 1
fi

echo "   ✅ Python 버전 OK"
echo ""

# 가상환경 생성 (선택)
read -p "가상환경을 생성하시겠습니까? (권장) [y/N]: " create_venv
if [[ "$create_venv" =~ ^[Yy]$ ]]; then
    echo ""
    echo "2️⃣  가상환경 생성 중..."
    python3 -m venv venv
    source venv/bin/activate
    echo "   ✅ 가상환경 활성화됨"
    echo "   (다음부터는 'source venv/bin/activate' 실행)"
else
    echo "   ⏭️  가상환경 건너뛰기"
fi

echo ""

# 시스템 정보
echo "3️⃣  시스템 정보 확인..."
total_ram=$(sysctl hw.memsize | awk '{print $2/1024/1024/1024}')
echo "   총 RAM: ${total_ram} GB"

if (( $(echo "$total_ram < 8" | bc -l) )); then
    echo "   ⚠️  RAM이 부족할 수 있습니다. Phi-2 모델 권장"
elif (( $(echo "$total_ram >= 16" | bc -l) )); then
    echo "   ✅ Mistral-7B 모델 사용 가능"
else
    echo "   ⚠️  Phi-2 또는 작은 모델 권장"
fi

echo ""

# MLX 설치
echo "4️⃣  MLX 프레임워크 설치 중..."
pip install --upgrade pip
pip install mlx mlx-lm

if [ $? -eq 0 ]; then
    echo "   ✅ MLX 설치 완료"
else
    echo "   ❌ MLX 설치 실패"
    exit 1
fi

echo ""

# 기타 패키지 설치
echo "5️⃣  필수 패키지 설치 중..."
pip install pandas numpy transformers huggingface-hub

echo "   ✅ 패키지 설치 완료"
echo ""

# HuggingFace CLI 로그인 (선택)
read -p "HuggingFace에 로그인하시겠습니까? (일부 모델 필요) [y/N]: " login_hf
if [[ "$login_hf" =~ ^[Yy]$ ]]; then
    pip install huggingface-hub[cli]
    huggingface-cli login
fi

echo ""

# 설치 확인
echo "6️⃣  설치 확인 중..."
python3 -c "import mlx; print('✅ MLX 버전:', mlx.__version__)"
python3 -c "import pandas; print('✅ Pandas 버전:', pandas.__version__)"

echo ""
echo "================================================"
echo "✅ 설치 완료!"
echo "================================================"
echo ""
echo "다음 단계:"
echo "1. CSV 파일을 'toefl_evaluations.csv'로 저장"
echo "2. python prepare_training_data.py 실행"
echo "3. python finetune_m2_mac.py 실행"
echo ""
echo "상세 가이드: M2_MAC_SETUP.md"
echo ""
