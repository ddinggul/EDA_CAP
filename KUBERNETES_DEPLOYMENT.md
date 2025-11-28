# ☸️ Kubernetes 배포 가이드

TOEFL 스피킹 평가 시스템을 Kubernetes 클러스터에 배포하는 가이드입니다.

---

## 📋 구조

```
k8s/
├── configmap.yaml              # 애플리케이션 설정
├── secrets.yaml.example        # 비밀 정보 템플릿
├── flask-api-deployment.yaml   # Flask API 서버 배포
├── backend-deployment.yaml     # FastAPI 백엔드 배포
├── frontend-deployment.yaml    # React 프론트엔드 배포
├── ingress.yaml                # Ingress 라우팅
└── kustomization.yaml          # Kustomize 설정
```

---

## 🚀 빠른 시작

### 1. 사전 요구사항

- Kubernetes 클러스터 (minikube, GKE, EKS, AKS 등)
- kubectl 설치 및 클러스터 연결
- Docker 이미지 빌드 및 레지스트리 푸시

```bash
# kubectl 설치 확인
kubectl version --client

# 클러스터 연결 확인
kubectl cluster-info

# Docker 설치 확인
docker --version
```

### 2. Docker 이미지 빌드 및 푸시

```bash
# Docker 이미지 빌드
docker build -t your-registry/toefl-flask-api:latest .
docker build -t your-registry/toefl-backend:latest ./backend
docker build -t your-registry/toefl-frontend:latest ./frontend

# 이미지 푸시 (Docker Hub, GCR, ECR 등)
docker push your-registry/toefl-flask-api:latest
docker push your-registry/toefl-backend:latest
docker push your-registry/toefl-frontend:latest
```

### 3. Secret 생성

```bash
# Secret 파일 생성
cd k8s
cp secrets.yaml.example secrets.yaml

# 실제 키 값으로 수정 (stringData 사용)
# vim secrets.yaml
```

**secrets.yaml** 예시:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: toefl-secrets
type: Opaque
stringData:
  clova-secret-key: "your_actual_clova_key"
  openai-api-key: "sk-your_actual_openai_key"
```

또는 kubectl로 직접 생성:
```bash
kubectl create secret generic toefl-secrets \
  --from-literal=clova-secret-key='your_clova_key' \
  --from-literal=openai-api-key='sk-your_openai_key'
```

### 4. 배포

#### 방법 A: kubectl로 개별 배포

```bash
cd k8s

# ConfigMap 생성
kubectl apply -f configmap.yaml

# Secret 생성
kubectl apply -f secrets.yaml

# 서비스 배포
kubectl apply -f flask-api-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Ingress 생성
kubectl apply -f ingress.yaml
```

#### 방법 B: Kustomize로 일괄 배포 (권장)

```bash
cd k8s

# kustomization.yaml 수정 (이미지 레지스트리 경로)
# vim kustomization.yaml

# 일괄 배포
kubectl apply -k .

# 또는
kustomize build . | kubectl apply -f -
```

---

## 🔍 배포 확인

### Pod 상태 확인

```bash
# 모든 Pod 확인
kubectl get pods

# 실시간 모니터링
kubectl get pods -w

# 특정 Pod 상세 정보
kubectl describe pod flask-api-xxxxx
```

예상 출력:
```
NAME                          READY   STATUS    RESTARTS   AGE
flask-api-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
flask-api-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
backend-xxxxxxxxxx-xxxxx      1/1     Running   0          2m
backend-xxxxxxxxxx-xxxxx      1/1     Running   0          2m
frontend-xxxxxxxxxx-xxxxx     1/1     Running   0          2m
frontend-xxxxxxxxxx-xxxxx     1/1     Running   0          2m
```

### Service 확인

```bash
# 서비스 목록
kubectl get svc

# 상세 정보
kubectl describe svc flask-api
kubectl describe svc backend
kubectl describe svc frontend
```

### Ingress 확인

```bash
# Ingress 확인
kubectl get ingress

# 상세 정보
kubectl describe ingress toefl-ingress
```

---

## 🌐 접속

### Ingress를 통한 접속

Ingress 설정 후 도메인을 통해 접속:

```bash
# Ingress IP 확인
kubectl get ingress toefl-ingress

# /etc/hosts에 추가 (로컬 테스트)
# <INGRESS_IP> toefl.example.com
```

접속 URL:
- **프론트엔드**: http://toefl.example.com/
- **Flask API**: http://toefl.example.com/api/v1/
- **FastAPI**: http://toefl.example.com/api/v2/

### LoadBalancer를 통한 접속 (프론트엔드)

```bash
# 외부 IP 확인
kubectl get svc frontend

# EXTERNAL-IP로 접속
curl http://<EXTERNAL-IP>
```

### Port Forward를 통한 로컬 접속

```bash
# Flask API
kubectl port-forward svc/flask-api 5000:5000

# FastAPI 백엔드
kubectl port-forward svc/backend 8000:8000

# 프론트엔드
kubectl port-forward svc/frontend 3000:80
```

접속:
- Flask API: http://localhost:5000
- FastAPI: http://localhost:8000
- Frontend: http://localhost:3000

---

## 🔧 관리 및 운영

### 로그 확인

```bash
# 실시간 로그
kubectl logs -f deployment/flask-api
kubectl logs -f deployment/backend
kubectl logs -f deployment/frontend

# 특정 Pod 로그
kubectl logs flask-api-xxxxx-xxxxx

# 이전 컨테이너 로그
kubectl logs flask-api-xxxxx-xxxxx --previous

# 모든 Pod 로그 (Stern 사용)
stern flask-api
```

### 스케일링

```bash
# Replica 수 조정
kubectl scale deployment flask-api --replicas=3
kubectl scale deployment backend --replicas=3
kubectl scale deployment frontend --replicas=3

# HorizontalPodAutoscaler 생성 (CPU 기반)
kubectl autoscale deployment flask-api \
  --cpu-percent=70 \
  --min=2 \
  --max=10

# HPA 확인
kubectl get hpa
```

### 업데이트

```bash
# 이미지 업데이트
kubectl set image deployment/flask-api \
  flask-api=your-registry/toefl-flask-api:v2.0

# 롤링 업데이트 상태 확인
kubectl rollout status deployment/flask-api

# 롤백
kubectl rollout undo deployment/flask-api

# 특정 리비전으로 롤백
kubectl rollout undo deployment/flask-api --to-revision=2

# 업데이트 히스토리
kubectl rollout history deployment/flask-api
```

### 설정 업데이트

```bash
# ConfigMap 수정
kubectl edit configmap toefl-config

# Secret 수정
kubectl edit secret toefl-secrets

# Pod 재시작 (설정 반영)
kubectl rollout restart deployment/flask-api
kubectl rollout restart deployment/backend
```

---

## 🐛 문제 해결

### Pod가 Running 상태가 안 됨

```bash
# Pod 상태 확인
kubectl get pods
kubectl describe pod <pod-name>

# 이벤트 확인
kubectl get events --sort-by=.metadata.creationTimestamp

# 로그 확인
kubectl logs <pod-name>
```

주요 원인:
- 이미지 pull 실패: imagePullPolicy 확인
- Secret 없음: `kubectl get secret toefl-secrets`
- 리소스 부족: `kubectl top nodes`

### ImagePullBackOff 오류

```bash
# 이미지 확인
kubectl describe pod <pod-name> | grep Image

# 레지스트리 인증 설정 (필요 시)
kubectl create secret docker-registry regcred \
  --docker-server=<your-registry> \
  --docker-username=<username> \
  --docker-password=<password>

# Deployment에 imagePullSecrets 추가
```

### CrashLoopBackOff 오류

```bash
# 로그 확인
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# 환경 변수 확인
kubectl exec <pod-name> -- env

# Secret 확인
kubectl get secret toefl-secrets -o yaml
```

### Service 연결 안 됨

```bash
# Service 엔드포인트 확인
kubectl get endpoints flask-api

# Service와 Pod 레이블 일치 확인
kubectl get pods --show-labels
kubectl describe svc flask-api

# Pod 내부에서 테스트
kubectl exec -it <pod-name> -- curl http://flask-api:5000/health
```

### Ingress 작동 안 함

```bash
# Ingress Controller 확인
kubectl get pods -n ingress-nginx

# Ingress 리소스 확인
kubectl describe ingress toefl-ingress

# Ingress Controller 로그
kubectl logs -n ingress-nginx <ingress-controller-pod>
```

---

## 📊 모니터링

### 리소스 사용량

```bash
# Node 리소스
kubectl top nodes

# Pod 리소스
kubectl top pods

# 특정 네임스페이스
kubectl top pods -n default
```

### Metrics Server 설치 (필요 시)

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### 프로메테우스 & 그라파나 (선택사항)

```bash
# Helm으로 설치
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack
```

---

## 🔒 보안

### Secret 관리

```bash
# Secret을 Git에 커밋하지 말 것!
echo "k8s/secrets.yaml" >> .gitignore

# Sealed Secrets 사용 (권장)
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# kubeseal로 암호화
kubeseal --format=yaml < secrets.yaml > sealed-secrets.yaml
```

### RBAC 설정

```bash
# ServiceAccount 생성
kubectl create serviceaccount toefl-sa

# Role 생성
kubectl create role toefl-role --verb=get,list --resource=pods

# RoleBinding 생성
kubectl create rolebinding toefl-binding \
  --role=toefl-role \
  --serviceaccount=default:toefl-sa
```

### Network Policy (선택사항)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: toefl-network-policy
spec:
  podSelector:
    matchLabels:
      app: toefl-evaluator
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: toefl-evaluator
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: toefl-evaluator
```

---

## 🌍 프로덕션 배포

### 1. Namespace 분리

```bash
# 네임스페이스 생성
kubectl create namespace production

# 네임스페이스에 배포
kubectl apply -k k8s/ -n production

# 기본 네임스페이스 설정
kubectl config set-context --current --namespace=production
```

### 2. 리소스 제한 설정

Deployment에 리소스 제한 추가 (이미 설정됨):
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### 3. Health Check 설정

Liveness/Readiness Probe 설정 (이미 설정됨):
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
readinessProbe:
  httpGet:
    path: /health
    port: 5000
```

### 4. 영구 볼륨 (필요 시)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: toefl-data
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### 5. SSL/TLS 설정

```bash
# cert-manager 설치
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# ClusterIssuer 생성
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## 📚 클러스터 환경별 가이드

### Minikube (로컬 개발)

```bash
# Minikube 시작
minikube start --cpus=4 --memory=8192

# Ingress 활성화
minikube addons enable ingress

# Minikube IP로 접속
minikube service frontend --url

# Minikube에서 로컬 이미지 사용
eval $(minikube docker-env)
docker build -t toefl-flask-api:latest .
```

### GKE (Google Cloud)

```bash
# 클러스터 생성
gcloud container clusters create toefl-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-2

# kubectl 연결
gcloud container clusters get-credentials toefl-cluster

# Ingress Controller 설치 (GCE)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/cloud/deploy.yaml
```

### EKS (AWS)

```bash
# eksctl로 클러스터 생성
eksctl create cluster \
  --name toefl-cluster \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3

# Ingress Controller 설치
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/aws/deploy.yaml
```

### AKS (Azure)

```bash
# 클러스터 생성
az aks create \
  --resource-group toefl-rg \
  --name toefl-cluster \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3

# kubectl 연결
az aks get-credentials --resource-group toefl-rg --name toefl-cluster

# Ingress Controller 설치
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/cloud/deploy.yaml
```

---

## 🧹 정리

```bash
# 전체 리소스 삭제
kubectl delete -k k8s/

# 또는 개별 삭제
kubectl delete -f k8s/ingress.yaml
kubectl delete -f k8s/frontend-deployment.yaml
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete -f k8s/flask-api-deployment.yaml
kubectl delete -f k8s/secrets.yaml
kubectl delete -f k8s/configmap.yaml

# 네임스페이스 삭제 (전체)
kubectl delete namespace production
```

---

## 💡 베스트 프랙티스

1. **이미지 태그 관리**: `latest` 대신 버전 태그 사용 (예: `v1.0.0`)
2. **Secret 관리**: Git에 커밋하지 말고 별도 관리
3. **리소스 제한**: 모든 컨테이너에 requests/limits 설정
4. **Health Check**: Liveness/Readiness Probe 필수 설정
5. **로그 집중화**: ELK, Loki 등 로그 수집 시스템 구축
6. **모니터링**: Prometheus + Grafana 설정
7. **백업**: 중요 데이터는 PersistentVolume 사용
8. **네임스페이스**: 환경별 네임스페이스 분리 (dev, staging, prod)

---

**Kubernetes로 확장 가능한 TOEFL 평가 시스템을 운영하세요!** ☸️
