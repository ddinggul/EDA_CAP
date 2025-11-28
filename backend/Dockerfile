# TOEFL 스피킹 평가 시스템 - FastAPI 백엔드
FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 업데이트
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY app/ ./app/

# 포트 노출
EXPOSE 8000

# 환경변수 설정
ENV PYTHONUNBUFFERED=1

# 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
