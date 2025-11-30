# Kind로 Kubernetes 클러스터 구성하기

Kind(Kubernetes in Docker)를 사용하여 macOS 환경에서 로컬 Kubernetes 클러스터를 생성하는 방법을 설명합니다.

## 📋 개요

Kind는 Docker 컨테이너를 Kubernetes 노드로 사용하는 도구로, 로컬 개발 및 테스트에 적합합니다.

### 클러스터 구성
- **Control Plane**: 1개
- **Worker 노드**: 2개
- **포트 매핑**: 30000~30005, 80, 443
- **영구 볼륨**: Jenkins 및 ArgoCD용 HostPath

## 🔧 사전 준비

```bash
# Docker Desktop이 실행 중인지 확인
docker ps

# Kind 설치 (macOS)
brew install kind

# kubectl 설치
brew install kubectl
```

## 📝 클러스터 설정 파일

다음 내용으로 `kind-cluster.yaml` 파일을 생성합니다:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: myk8s
networking:
  apiServerAddress: "0.0.0.0"
nodes:
  - role: control-plane
    image: kindest/node:v1.32.8
    labels:
      app: ingress-controller
    extraPortMappings:
      # HTTP/HTTPS 포트 (Ingress용)
      - containerPort: 80
        hostPort: 80
        protocol: TCP
      - containerPort: 443
        hostPort: 443
        protocol: TCP
      # NodePort 범위
      - containerPort: 30000
        hostPort: 30000
      - containerPort: 30001
        hostPort: 30001
      - containerPort: 30002
        hostPort: 30002
      - containerPort: 30003
        hostPort: 30003
      - containerPort: 30004
        hostPort: 30004
      - containerPort: 30005
        hostPort: 30005
        
  - role: worker
    image: kindest/node:v1.32.8
    labels:
      app: jenkins
    extraMounts:
      - hostPath: /private/var/persist/jenkins
        containerPath: /private/var/persist/jenkins
        
  - role: worker
    image: kindest/node:v1.32.8
    labels:
      app: argocd
    extraMounts:
      - hostPath: /private/var/persist/argocd
        containerPath: /private/var/persist/argocd
```

## 🚀 클러스터 생성

### 1. 영구 볼륨 디렉토리 생성

```bash
# Jenkins용 디렉토리
sudo mkdir -p /private/var/persist/jenkins
sudo chmod 777 /private/var/persist/jenkins

# ArgoCD용 디렉토리
sudo mkdir -p /private/var/persist/argocd
sudo chmod 777 /private/var/persist/argocd
```

### 2. 클러스터 생성

```bash
kind create cluster --config kind-cluster.yaml
```

**예상 출력:**
```
Creating cluster "myk8s" ...
 ✓ Ensuring node image (kindest/node:v1.32.8) 🖼
 ✓ Preparing nodes 📦 📦 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
 ✓ Joining worker nodes 🚜
Set kubectl context to "kind-myk8s"
You can now use your cluster with:

kubectl cluster-info --context kind-myk8s
```

### 3. 클러스터 확인

```bash
# 컨텍스트 확인
kubectl config current-context
# 출력: kind-myk8s

# 노드 확인
kubectl get nodes
```

**예상 출력:**
```
NAME                  STATUS   ROLES           AGE   VERSION
myk8s-control-plane   Ready    control-plane   2m    v1.32.8
myk8s-worker          Ready    <none>          2m    v1.32.8
myk8s-worker2         Ready    <none>          2m    v1.32.8
```

### 4. 노드 레이블 확인

```bash
kubectl get nodes --show-labels | grep app
```

## 📊 포트 매핑 정보

| 포트  | 서비스        | 설명                | 볼륨 마운트                      |
|-------|---------------|---------------------|----------------------------------|
| 80    | Ingress       | HTTP                | -                                |
| 443   | Ingress       | HTTPS               | -                                |
| 30000 | (예약)        | TBD                 | -                                |
| 30001 | (예약)        | TBD                 | -                                |
| 30002 | ArgoCD        | ArgoCD HTTP         | /private/var/persist/argocd      |
| 30003 | Jenkins       | Jenkins HTTP        | /private/var/persist/jenkins     |
| 30004 | (예약)        | TBD                 | -                                |
| 30005 | (예약)        | TBD                 | -                                |

## 🛠️ 유용한 명령어

### 클러스터 목록 확인
```bash
kind get clusters
```

### 클러스터 삭제
```bash
kind delete cluster --name myk8s
```

### 클러스터 재생성 (데이터 초기화)
```bash
kind delete cluster --name myk8s
kind create cluster --config kind-cluster.yaml
```

### 특정 노드의 Docker 컨테이너 확인
```bash
docker ps | grep myk8s
```

### 노드 내부 접속 (디버깅용)
```bash
docker exec -it myk8s-control-plane bash
```

## 🔍 트러블슈팅

### 포트가 이미 사용 중인 경우
```bash
# 포트 사용 확인 (macOS)
lsof -i :80
lsof -i :443

# Docker Desktop 재시작
# Docker Desktop 앱 → Restart
```

### 영구 볼륨 권한 문제
```bash
# 권한 재설정
sudo chmod -R 777 /private/var/persist/jenkins
sudo chmod -R 777 /private/var/persist/argocd
```

### 클러스터가 시작되지 않을 때
```bash
# 기존 클러스터 완전 삭제
kind delete cluster --name myk8s

# Docker 이미지 정리
docker system prune -a

# 재생성
kind create cluster --config kind-cluster.yaml
```

## 📚 다음 단계

클러스터가 정상적으로 생성되었다면:

1. [Ingress Nginx 설치](./03-ingress-nginx.md)
2. [TLS 인증서 생성](./04-tls-certificates.md)
3. [ArgoCD 설치](../03-argocd/02-kind-installation.md)
4. [Jenkins 설치](../04-jenkins/02-kind-installation.md)

## 🔗 참고 자료

- [Kind 공식 문서](https://kind.sigs.k8s.io/)
- [Kind 설정 옵션](https://kind.sigs.k8s.io/docs/user/configuration/)
- [Kind Ingress 가이드](https://kind.sigs.k8s.io/docs/user/ingress/)
