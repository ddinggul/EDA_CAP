# 🐳 Docker 배포 가이드

TOEFL 스피킹 평가 시스템을 Docker로 배포하는 가이드입니다.

---

## 📋 구조

```
프로젝트/
├── Dockerfile                  # Flask API 서버
├── docker-compose.yml          # 전체 시스템 오케스트레이션
├── backend/
│   └── Dockerfile             # FastAPI 백엔드
└── frontend/
    └── Dockerfile             # React 프론트엔드
```

---

## 🚀 빠른 시작

### 1. 환경 변수 설정

루트 디렉토리에 `.env` 파일을 생성하거나 기존 `.env` 파일을 확인하세요:

```bash
# Naver Clova Speech API
NAVER_CLOVA_SECRET_KEY=your_clova_secret_key

# OpenAI API
OPENAI_API_KEY=sk-your_openai_api_key

# 파인튜닝된 모델 (선택, 없으면 gpt-3.5-turbo 사용)
OPENAI_FINETUNED_MODEL=ft:gpt-3.5-turbo:your-org:model-id
```

### 2. 전체 시스템 실행

```bash
# 모든 서비스 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

### 3. 서비스 접속

실행 후 다음 주소로 접속 가능합니다:

- **프론트엔드**: http://localhost:3000
- **FastAPI 백엔드**: http://localhost:8000
- **Flask API 서버**: http://localhost:5000

---

## 📦 개별 서비스 실행

### Flask API 서버만 실행

```bash
# 루트 디렉토리에서
docker build -t toefl-flask-api .
docker run -p 5000:5000 --env-file .env toefl-flask-api
```

### FastAPI 백엔드만 실행

```bash
cd backend
docker build -t toefl-backend .
docker run -p 8000:8000 --env-file .env toefl-backend
```

### React 프론트엔드만 실행

```bash
cd frontend
docker build -t toefl-frontend .
docker run -p 3000:80 toefl-frontend
```

---

## 🛠️ Docker Compose 명령어

### 서비스 관리

```bash
# 전체 서비스 시작
docker-compose up

# 전체 서비스 시작 (백그라운드)
docker-compose up -d

# 전체 서비스 중지
docker-compose down

# 전체 서비스 중지 (볼륨 포함)
docker-compose down -v

# 특정 서비스만 시작
docker-compose up flask-api
docker-compose up backend
docker-compose up frontend
```

### 로그 확인

```bash
# 전체 로그
docker-compose logs

# 실시간 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs flask-api
docker-compose logs backend
docker-compose logs frontend
```

### 재빌드

```bash
# 전체 재빌드
docker-compose build

# 특정 서비스만 재빌드
docker-compose build flask-api
docker-compose build backend
docker-compose build frontend

# 재빌드 후 실행
docker-compose up --build
```

---

## 🔍 상태 확인

### 컨테이너 상태

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 모든 컨테이너 확인
docker ps -a
```

### 헬스 체크

```bash
# Flask API 서버
curl http://localhost:5000/health

# FastAPI 백엔드
curl http://localhost:8000/

# 프론트엔드
curl http://localhost:3000
```

---

## 🧪 API 테스트

### Flask API 서버 테스트

```bash
# 음성 파일 평가
curl -X POST http://localhost:5000/evaluate \
  -F "file=@student.wav"

# 텍스트만 평가
curl -X POST http://localhost:5000/evaluate_text \
  -H "Content-Type: application/json" \
  -d '{"text": "I prefer studying subjects that interest me..."}'
```

### FastAPI 백엔드 테스트

```bash
# API 문서 확인
curl http://localhost:8000/docs

# 또는 브라우저에서
open http://localhost:8000/docs
```

---

## 🔧 개발 환경 설정

### 개발 모드로 실행 (볼륨 마운트)

`docker-compose.yml`에 이미 볼륨이 마운트되어 있어, 로컬 코드 변경이 즉시 반영됩니다:

```yaml
volumes:
  - ./toefl_evaluator.py:/app/toefl_evaluator.py
  - ./api_server.py:/app/api_server.py
```

코드 변경 후 서비스 재시작:

```bash
docker-compose restart flask-api
# 또는
docker-compose restart backend
```

---

## 📊 리소스 모니터링

### 컨테이너 리소스 사용량

```bash
# 실시간 모니터링
docker stats

# 특정 컨테이너만
docker stats toefl-flask-api
docker stats toefl-backend
docker stats toefl-frontend
```

### 디스크 사용량

```bash
# Docker 전체 사용량
docker system df

# 상세 정보
docker system df -v
```

---

## 🧹 정리

### 컨테이너 및 이미지 정리

```bash
# 중지된 컨테이너 모두 삭제
docker container prune

# 사용하지 않는 이미지 삭제
docker image prune

# 사용하지 않는 볼륨 삭제
docker volume prune

# 전체 정리 (주의!)
docker system prune -a
```

### 프로젝트 관련 리소스만 정리

```bash
# 컨테이너 중지 및 삭제
docker-compose down

# 볼륨까지 삭제
docker-compose down -v

# 이미지도 삭제
docker-compose down --rmi all
```

---

## 🐛 문제 해결

### Q1: 포트가 이미 사용 중입니다

**A**: `docker-compose.yml`에서 포트를 변경하세요:

```yaml
services:
  flask-api:
    ports:
      - "5001:5000"  # 5001로 변경
```

### Q2: 환경 변수가 로드되지 않습니다

**A**: `.env` 파일이 올바른 위치에 있는지 확인:

```bash
# 루트 디렉토리에 .env 파일 확인
ls -la .env

# 내용 확인
cat .env
```

### Q3: 빌드 중 오류 발생

**A**: 캐시를 무시하고 재빌드:

```bash
docker-compose build --no-cache
docker-compose up
```

### Q4: 컨테이너가 계속 재시작됩니다

**A**: 로그를 확인하여 원인 파악:

```bash
docker-compose logs flask-api
docker-compose logs backend
```

---

## 🌐 프로덕션 배포

### 환경 변수 분리

프로덕션 환경에서는 별도의 환경 변수 파일 사용:

```bash
# .env.production 파일 생성
cp .env .env.production

# 프로덕션 환경으로 실행
docker-compose --env-file .env.production up -d
```

### 리소스 제한

`docker-compose.yml`에 리소스 제한 추가:

```yaml
services:
  flask-api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 로그 관리

```yaml
services:
  flask-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 📚 추가 정보

### Dockerfile 위치

- **Flask API**: `/Dockerfile`
- **FastAPI 백엔드**: `/backend/Dockerfile`
- **React 프론트엔드**: `/frontend/Dockerfile`

### 네트워크

모든 서비스는 `toefl-network`라는 브리지 네트워크로 연결됩니다.

서비스 간 통신:
- Flask API: `http://flask-api:5000`
- FastAPI 백엔드: `http://backend:8000`
- 프론트엔드: `http://frontend:80`

---

## 💡 팁

1. **빠른 재시작**: 코드 변경 후 `docker-compose restart [service-name]`
2. **로그 실시간 확인**: `docker-compose logs -f [service-name]`
3. **특정 서비스만 재빌드**: `docker-compose up -d --no-deps --build [service-name]`
4. **컨테이너 내부 접속**: `docker exec -it toefl-flask-api bash`

---

**간편한 Docker 배포로 TOEFL 평가 시스템을 실행하세요!** 🚀
