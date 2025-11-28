# TOEFL Evaluator Helm Chart

Helm chart for deploying the TOEFL Speaking Evaluation System on Kubernetes.

## 설치

### 1. 기본 설치

```bash
# Helm 레포지토리 추가 (필요 시)
helm repo add toefl https://your-repo.example.com
helm repo update

# 차트 설치
helm install toefl-evaluator ./helm/toefl-evaluator \
  --set secrets.clovaSecretKey="your_clova_key" \
  --set secrets.openaiApiKey="sk-your_openai_key"
```

### 2. 커스텀 설정으로 설치

```bash
# values.yaml 복사 및 수정
cp helm/toefl-evaluator/values.yaml my-values.yaml
vim my-values.yaml

# 커스텀 values로 설치
helm install toefl-evaluator ./helm/toefl-evaluator \
  -f my-values.yaml \
  --set secrets.clovaSecretKey="your_clova_key" \
  --set secrets.openaiApiKey="sk-your_openai_key"
```

### 3. 네임스페이스 지정

```bash
# 네임스페이스 생성
kubectl create namespace production

# 네임스페이스에 설치
helm install toefl-evaluator ./helm/toefl-evaluator \
  --namespace production \
  --set secrets.clovaSecretKey="your_clova_key" \
  --set secrets.openaiApiKey="sk-your_openai_key"
```

## 설정

### 주요 설정 값

| 파라미터 | 설명 | 기본값 |
|---------|------|--------|
| `flaskApi.replicaCount` | Flask API 레플리카 수 | `2` |
| `backend.replicaCount` | 백엔드 레플리카 수 | `2` |
| `frontend.replicaCount` | 프론트엔드 레플리카 수 | `2` |
| `ingress.enabled` | Ingress 활성화 | `true` |
| `ingress.hosts[0].host` | 도메인 이름 | `toefl.example.com` |
| `secrets.clovaSecretKey` | Clova API 키 | 필수 |
| `secrets.openaiApiKey` | OpenAI API 키 | 필수 |

### 리소스 설정

```bash
helm install toefl-evaluator ./helm/toefl-evaluator \
  --set flaskApi.resources.requests.memory=1Gi \
  --set flaskApi.resources.limits.memory=2Gi
```

### 오토스케일링 활성화

```bash
helm install toefl-evaluator ./helm/toefl-evaluator \
  --set flaskApi.autoscaling.enabled=true \
  --set flaskApi.autoscaling.minReplicas=2 \
  --set flaskApi.autoscaling.maxReplicas=10
```

## 업그레이드

```bash
# 업그레이드
helm upgrade toefl-evaluator ./helm/toefl-evaluator \
  -f my-values.yaml

# 업그레이드 (새 이미지 태그)
helm upgrade toefl-evaluator ./helm/toefl-evaluator \
  --set flaskApi.image.tag=v2.0.0
```

## 롤백

```bash
# 이전 버전으로 롤백
helm rollback toefl-evaluator

# 특정 리비전으로 롤백
helm rollback toefl-evaluator 2
```

## 삭제

```bash
# 차트 삭제
helm uninstall toefl-evaluator

# 네임스페이스도 삭제
helm uninstall toefl-evaluator -n production
kubectl delete namespace production
```

## 상태 확인

```bash
# 릴리스 목록
helm list

# 릴리스 상태
helm status toefl-evaluator

# 릴리스 히스토리
helm history toefl-evaluator

# 차트 값 확인
helm get values toefl-evaluator
```

## 개발

### 차트 검증

```bash
# 문법 체크
helm lint ./helm/toefl-evaluator

# 템플릿 렌더링 (실제 배포 없이)
helm template toefl-evaluator ./helm/toefl-evaluator

# Dry-run
helm install toefl-evaluator ./helm/toefl-evaluator --dry-run --debug
```

### 차트 패키징

```bash
# 차트 패키징
helm package ./helm/toefl-evaluator

# 인덱스 생성
helm repo index .
```
