# 🚀 배포 가이드

TOEFL Speaking AI Consultant를 Vercel (프론트엔드) + Render (백엔드)에 배포하는 방법입니다.

---

## 📋 배포 전 체크리스트

- [ ] GitHub 계정
- [ ] Vercel 계정 (https://vercel.com/signup)
- [ ] Render 계정 (https://render.com/signup)
- [ ] Naver Clova API 키
- [ ] OpenAI API 키

---

## 1️⃣ GitHub 레포지토리 생성 및 푸시

### 1-1. GitHub에서 새 레포지토리 생성

1. https://github.com/new 접속
2. Repository name: `toefl-speaking-ai` (원하는 이름)
3. Public 또는 Private 선택
4. **"Create repository"** 클릭

### 1-2. 로컬 코드를 GitHub에 푸시

터미널에서 프로젝트 디렉토리로 이동 후:

```bash
cd /Users/junseo/PycharmProjects/EDA_CAP

# Git 초기화 (이미 되어있다면 생략)
git init

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit for deployment"

# GitHub 레포지토리 연결 (YOUR_USERNAME를 본인 GitHub 계정명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/toefl-speaking-ai.git

# 푸시
git branch -M main
git push -u origin main
```

---

## 2️⃣ 백엔드 배포 (Render)

### 2-1. Render에서 Web Service 생성

1. https://dashboard.render.com 로그인
2. **"New +"** → **"Web Service"** 클릭
3. **"Connect a repository"** → GitHub 연결
4. 방금 생성한 레포지토리 선택
5. 설정 입력:
   - **Name**: `toefl-backend` (원하는 이름)
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### 2-2. 환경 변수 설정

**"Environment Variables"** 섹션에서 추가:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11` |
| `NAVER_CLOVA_SECRET_KEY` | `여기에_Naver_API_키_입력` |
| `OPENAI_API_KEY` | `여기에_OpenAI_API_키_입력` |
| `OPENAI_MODEL_NAME` | `gpt-4o-mini` |

### 2-3. 배포 시작

1. **"Create Web Service"** 클릭
2. 배포 로그 확인 (5-10분 소요)
3. 배포 완료 후 URL 복사: `https://toefl-backend-XXXX.onrender.com`

### 2-4. 백엔드 동작 확인

브라우저에서 접속:
```
https://toefl-backend-XXXX.onrender.com/health
```

응답이 `{"status":"healthy"}`이면 성공!

---

## 3️⃣ 프론트엔드 배포 (Vercel)

### 3-1. Vercel에서 프로젝트 Import

1. https://vercel.com/new 접속
2. GitHub 레포지토리 Import
3. **"Configure Project"** 화면에서:
   - **Project Name**: `toefl-speaking` (원하는 이름)
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3-2. 환경 변수 설정

**"Environment Variables"** 섹션에서 추가:

| Name | Value |
|------|-------|
| `VITE_API_BASE_URL` | `https://toefl-backend-XXXX.onrender.com` |

⚠️ **중요**: 위에서 복사한 Render 백엔드 URL을 입력하세요!

### 3-3. 배포 시작

1. **"Deploy"** 클릭
2. 배포 로그 확인 (2-3분 소요)
3. 배포 완료 후 **"Visit"** 클릭

---

## 4️⃣ 배포 확인 및 테스트

### 프론트엔드 URL
```
https://toefl-speaking-XXXX.vercel.app
```

### 테스트 절차

1. 프론트엔드 URL 접속
2. "실전 모의고사 시작" 클릭
3. Part 2 문제 선택
4. 문제 풀기 및 녹음
5. 평가 결과 확인

---

## 5️⃣ 문제 해결

### 백엔드가 응답하지 않는 경우

**Render 대시보드**에서:
1. Logs 탭 확인
2. Environment Variables 재확인
3. Manual Deploy로 재배포

### 프론트엔드에서 백엔드에 연결 안 되는 경우

**Vercel 대시보드**에서:
1. Settings → Environment Variables 확인
2. `VITE_API_BASE_URL`이 올바른 Render URL인지 확인
3. Deployments → Redeploy

### CORS 에러가 발생하는 경우

1. 백엔드 `app/main.py`의 CORS 설정 확인
2. Vercel 도메인이 allow_origins에 포함되어 있는지 확인

---

## 6️⃣ 재배포 방법

### 코드 수정 후 재배포

```bash
# 변경사항 커밋
git add .
git commit -m "Update: 변경 내용 설명"
git push origin main
```

- **Vercel**: 자동으로 재배포됨 (1-2분)
- **Render**: 자동으로 재배포됨 (5-10분)

---

## 7️⃣ 비용

- **Vercel (프론트엔드)**: 무료 플랜 (충분함)
- **Render (백엔드)**: 무료 플랜 (15분 비활성 후 슬립 모드)

⚠️ **참고**: Render 무료 플랜은 15분간 요청이 없으면 슬립 모드로 전환됩니다.
첫 요청 시 30초 정도 웨이크업 시간이 필요합니다.

---

## 📌 최종 체크리스트

- [ ] GitHub에 코드 푸시 완료
- [ ] Render 백엔드 배포 완료
- [ ] Render 환경 변수 설정 완료
- [ ] Vercel 프론트엔드 배포 완료
- [ ] Vercel 환경 변수 설정 완료
- [ ] 백엔드 헬스체크 성공
- [ ] 프론트엔드에서 문제 목록 로드 성공
- [ ] 녹음 및 평가 테스트 성공

---

## 🎉 배포 완료!

이제 다음 URL로 접속하여 TOEFL Speaking 연습을 시작할 수 있습니다:

- **프론트엔드**: https://toefl-speaking-XXXX.vercel.app
- **백엔드 API**: https://toefl-backend-XXXX.onrender.com

과제 제출 시 **프론트엔드 URL**을 제출하세요!
