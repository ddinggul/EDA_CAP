# TOEFL 스피킹 평가 시스템 - React 프론트엔드

# 빌드 스테이지
FROM node:20-alpine AS builder

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY package*.json ./
RUN npm ci

# 소스 코드 복사
COPY . .

# 프로덕션 빌드
RUN npm run build

# 프로덕션 스테이지 - Nginx로 정적 파일 서빙
FROM nginx:alpine

# Nginx 설정 파일 복사 (선택사항)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# 빌드된 파일 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# 포트 노출
EXPOSE 80

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
