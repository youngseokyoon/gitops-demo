# Kind로 Kubernetes 클러스터 구성하기

Kind(Kubernetes in Docker)를 사용하여 macOS 환경에서 로컬 Kubernetes 클러스터를 생성하는 방법을 설명합니다.

## 📋 개요

Kind(Kubernetes in Docker)는 Docker 컨테이너를 Kubernetes 노드로 사용하는 도구로, 로컬 개발 및 테스트에 이상적입니다.

### 주요 특징
- 🚀 **빠른 설정**: 몇 분 안에 클러스터 구성 가능
- 🔄 **재현 가능한 환경**: YAML 파일로 클러스터 구성 정의
- 🧪 **테스트 친화적**: CI/CD 파이프라인에서 사용 가능
- 💻 **리소스 효율적**: 실제 VM보다 가벼움

### 클러스터 구성
이 가이드에서 설정할 클러스터:

- **Control Plane**: 1개 (Kubernetes API, etcd, scheduler 등)
- **Worker 노드**: 2개 (실제 워크로드 실행)
- **포트 매핑**: 
  - HTTP/HTTPS: 80, 443 (Ingress용)
  - NodePort: 30000~30005 (서비스 노출용)
- **영구 볼륨**: Jenkins 및 ArgoCD용 HostPath 마운트
- **노드 레이블**: 워크로드 스케줄링을 위한 레이블 설정

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
  # API 서버가 모든 네트워크 인터페이스에서 수신하도록 설정
  apiServerAddress: "0.0.0.0"
  # 기본 PodCIDR (변경 가능)
  # podSubnet: "10.244.0.0/16"
  # 기본 ServiceCIDR (변경 가능)
  # serviceSubnet: "10.96.0.0/12"
  
nodes:
  # Control Plane 노드 (마스터)
  - role: control-plane
    # Kubernetes 버전 지정 (이미지 태그로 확인 가능)
    image: kindest/node:v1.32.8
    # Ingress Controller를 이 노드에 스케줄링하기 위한 레이블
    labels:
      app: ingress-controller
      ingress-ready: "true"
    # 컨테이너 포트를 호스트로 매핑
    extraPortMappings:
      # HTTP/HTTPS 포트 (Ingress Nginx용)
      - containerPort: 80
        hostPort: 80
        protocol: TCP
      - containerPort: 443
        hostPort: 443
        protocol: TCP
      
      # NodePort 범위 (서비스를 외부에 노출할 때 사용)
      - containerPort: 30000
        hostPort: 30000
      - containerPort: 30001
        hostPort: 30001
      - containerPort: 30002  # ArgoCD용
        hostPort: 30002
      - containerPort: 30003  # Jenkins용
        hostPort: 30003
      - containerPort: 30004
        hostPort: 30004
      - containerPort: 30005
        hostPort: 30005
        
  # Worker 노드 1 (Jenkins 워크로드용)
  - role: worker
    image: kindest/node:v1.32.8
    # NodeSelector를 사용하여 Jenkins Pod를 이 노드에만 스케줄링
    labels:
      app: jenkins
      workload-type: ci
    # 호스트 경로를 컨테이너 내부로 마운트 (영구 스토리지)
    extraMounts:
      - hostPath: /private/var/persist/jenkins
        containerPath: /private/var/persist/jenkins
        readOnly: false
        # selinuxRelabel: false  # Linux에서만 필요
        # propagation: None      # 마운트 전파 설정
        
  # Worker 노드 2 (ArgoCD 워크로드용)
  - role: worker
    image: kindest/node:v1.32.8
    labels:
      app: argocd
      workload-type: cd
    extraMounts:
      - hostPath: /private/var/persist/argocd
        containerPath: /private/var/persist/argocd
        readOnly: false
```

### 설정 파일 설명

#### Networking 섹션
- **apiServerAddress**: API 서버 바인딩 주소. `0.0.0.0`으로 설정하면 모든 네트워크 인터페이스에서 접근 가능
- **podSubnet**: Pod IP 주소 범위 (기본값: `10.244.0.0/16`)
- **serviceSubnet**: Service IP 주소 범위 (기본값: `10.96.0.0/12`)

#### 노드 레이블 (`labels`)
노드 레이블은 Pod 스케줄링 시 `nodeSelector` 또는 `affinity`로 특정 노드 지정에 사용됩니다:

```yaml
# Pod에서 노드 선택 예시
spec:
  nodeSelector:
    app: jenkins  # app=jenkins 레이블이 있는 노드에만 스케줄링
```

#### 포트 매핑 (`extraPortMappings`)
Kind 컨테이너의 포트를 호스트 머신으로 매핑:
- **80/443**: Ingress를 통한 HTTP/HTTPS 트래픽
- **30000-30005**: NodePort 서비스를 위한 포트 범위

#### 볼륨 마운트 (`extraMounts`)
호스트의 디렉토리를 Kind 노드 내부로 마운트하여 영구 스토리지 제공:
- Jenkins: 빌드 기록, 설정, 플러그인 등을 보존
- ArgoCD: 애플리케이션 상태, 설정 등을 보존

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
# 모든 레이블 표시
kubectl get nodes --show-labels

# 특정 레이블만 확인
kubectl get nodes -L app,workload-type
```

**예상 출력:**
```
NAME                  STATUS   ROLES           AGE   VERSION   APP         WORKLOAD-TYPE
myk8s-control-plane   Ready    control-plane   2m    v1.32.8   ingress-controller   
myk8s-worker          Ready    <none>          2m    v1.32.8   jenkins     ci
myk8s-worker2         Ready    <none>          2m    v1.32.8   argocd      cd
```

### 5. StorageClass 확인

Kind는 기본적으로 `standard` StorageClass를 제공합니다:

```bash
# StorageClass 목록 확인
kubectl get storageclass
```

**예상 출력:**
```
NAME                 PROVISIONER                    RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard (default)   rancher.io/local-path          Delete          WaitForFirstConsumer   false                  2m
```

#### StorageClass 사용 예시

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard  # Kind의 기본 StorageClass
  resources:
    requests:
      storage: 1Gi
```

### 6. 클러스터 정보 상세 확인

```bash
# API 서버 주소 및 CoreDNS 확인
kubectl cluster-info

# 모든 네임스페이스의 Pod 확인
kubectl get pods --all-namespaces

# 시스템 Pod 상태 확인 (CoreDNS, kube-proxy 등)
kubectl get pods -n kube-system
```

### 7. Docker 컨테이너 확인

```bash
# Kind 노드들이 Docker 컨테이너로 실행 중인지 확인
docker ps --filter "name=myk8s"
```

**예상 출력:**
```
CONTAINER ID   IMAGE                  NAMES
xxxxxxxxxxxx   kindest/node:v1.32.8   myk8s-control-plane
xxxxxxxxxxxx   kindest/node:v1.32.8   myk8s-worker
xxxxxxxxxxxx   kindest/node:v1.32.8   myk8s-worker2
```

## 📊 포트 매핑 정보

| 포트  | 서비스        | 설명                | 접속 방법             | 볼륨 마운트                      |
|-------|---------------|---------------------|----------------------|----------------------------------|
| 80    | Ingress       | HTTP                | http://localhost     | -                                |
| 443   | Ingress       | HTTPS               | https://localhost    | -                                |
| 30000 | (예약)        | 사용자 정의 서비스   | http://localhost:30000 | -                              |
| 30001 | (예약)        | 사용자 정의 서비스   | http://localhost:30001 | -                              |
| 30002 | ArgoCD        | ArgoCD UI/API       | http://localhost:30002 | /private/var/persist/argocd    |
| 30003 | Jenkins       | Jenkins UI/API      | http://localhost:30003 | /private/var/persist/jenkins   |
| 30004 | (예약)        | 사용자 정의 서비스   | http://localhost:30004 | -                              |
| 30005 | (예약)        | 사용자 정의 서비스   | http://localhost:30005 | -                              |

### NodePort 서비스 예시

NodePort를 사용하여 서비스를 외부에 노출하는 예:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
    - port: 80          # 클러스터 내부 포트
      targetPort: 8080  # Pod 포트
      nodePort: 30000   # 외부 노출 포트 (30000-32767 범위)
```

이렇게 설정하면 `http://localhost:30000`으로 서비스에 접근할 수 있습니다.

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

**증상:**
```
ERROR: failed to create cluster: failed to ensure docker network: ... address already in use
```

**해결 방법:**
```bash
# 포트 사용 확인 (macOS)
lsof -i :80
lsof -i :443
lsof -i :30000-30005

# 프로세스 종료 (필요한 경우)
kill -9 <PID>

# 또는 Docker Desktop 재시작
# Docker Desktop 앱 → Restart
```

### 영구 볼륨 권한 문제

**증상:**
Jenkins나 ArgoCD Pod가 `CrashLoopBackOff` 상태

**해결 방법:**
```bash
# 권한 확인
ls -la /private/var/persist/

# 권한 재설정
sudo chmod -R 777 /private/var/persist/jenkins
sudo chmod -R 777 /private/var/persist/argocd

# 소유자 확인 및 변경 (필요시)
sudo chown -R $(whoami) /private/var/persist/jenkins
```

### 클러스터가 시작되지 않을 때

**증상:**
클러스터 생성 중 멈추거나 실패

**해결 방법:**
```bash
# 1. 기존 클러스터 완전 삭제
kind delete cluster --name myk8s

# 2. Docker 네트워크 정리
docker network prune -f

# 3. Docker 컨테이너 정리
docker container prune -f

# 4. (선택) Docker 이미지 정리 (조심!)
docker image prune -a -f

# 5. Docker Desktop 재시작

# 6. 재생성
kind create cluster --config kind-cluster.yaml
```

### 노드가 NotReady 상태

**증상:**
```
NAME                  STATUS     ROLES           AGE   VERSION
myk8s-worker          NotReady   <none>          2m    v1.32.8
```

**해결 방법:**
```bash
# 노드 상태 상세 확인
kubectl describe node myk8s-worker

# CNI Pod 상태 확인
kubectl get pods -n kube-system | grep kindnet

# 문제가 있는 Pod 로그 확인
kubectl logs -n kube-system <pod-name>

# CNI 재시작
kubectl delete pod -n kube-system -l app=kindnet
```

### Docker Desktop 메모리 부족

**증상:**
Pod가 Pending 상태로 남아있거나 Evicted 됨

**해결 방법:**
```bash
# Docker Desktop 설정에서 메모리 증가
# Docker Desktop → Settings → Resources → Memory (8GB 이상 권장)

# 노드 리소스 확인
kubectl top nodes  # metrics-server 설치 필요

# Pod 리소스 사용량 확인
kubectl top pods --all-namespaces
```

### kubeconfig 접근 문제

**증상:**
```
The connection to the server localhost:8080 was refused
```

**해결 방법:**
```bash
# kubeconfig 파일 확인
echo $KUBECONFIG

# 기본 kubeconfig로 설정
export KUBECONFIG=~/.kube/config

# Kind 컨텍스트로 전환
kubectl config use-context kind-myk8s

# 컨텍스트 목록 확인
kubectl config get-contexts
```

### 이미지 풀 실패

**증상:**
```
ImagePullBackOff 또는 ErrImagePull
```

**해결 방법:**
```bash
# Pod 상세 정보 확인
kubectl describe pod <pod-name>

# Docker Hub 레이트 리미트 확인
# Docker 로그인 후 재시도
docker login

# Kind 클러스터에 직접 이미지 로드
docker pull <image-name>
kind load docker-image <image-name> --name myk8s
```

```

## 🚀 고급 설정

### 리소스 제한 설정

각 노드에 CPU와 메모리 제한을 설정할 수 있습니다:

```yaml
nodes:
  - role: control-plane
    # ...기존 설정...
    # 이 기능은 아직 실험적 상태이며 cgroup v2가 필요할 수 있음
    # kubeadmConfigPatches:
    #   - |
    #     kind: InitConfiguration
    #     nodeRegistration:
    #       kubeletExtraArgs:
    #         system-reserved: memory=1Gi,cpu=500m
    #         kube-reserved: memory=1Gi,cpu=500m
```

### 컨테이너 런타임 설정

Kind는 기본적으로 containerd를 사용하지만, 설정을 커스터마이징할 수 있습니다:

```yaml
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:5000"]
    endpoint = ["http://localhost:5000"]
```

### Private Registry 사용

Private container registry를 사용하려면:

```yaml
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".registry.configs."myregistry.com".auth]
    username = "myuser"
    password = "mypassword"
```

또는 더 안전하게 Docker config를 사용:

```bash
# Docker 로그인
docker login myregistry.com

# Kind 클러스터 생성 시 Docker config 사용
kind create cluster --config kind-cluster.yaml
```

### 멀티 클러스터 환경

여러 Kind 클러스터를 동시에 실행할 수 있습니다:

```bash
# 첫 번째 클러스터 (dev)
cat << EOF > kind-dev.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: dev-cluster
networking:
  apiServerAddress: "0.0.0.0"
  apiServerPort: 6443
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 80
        hostPort: 8080
EOF

kind create cluster --config kind-dev.yaml

# 두 번째 클러스터 (staging)
cat << EOF > kind-staging.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: staging-cluster
networking:
  apiServerAddress: "0.0.0.0"
  apiServerPort: 6444  # 다른 포트
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 80
        hostPort: 9080  # 다른 포트
EOF

kind create cluster --config kind-staging.yaml

# 컨텍스트 전환
kubectl config use-context kind-dev-cluster
kubectl config use-context kind-staging-cluster
```

### Feature Gates 활성화

Kubernetes의 실험적 기능을 활성화하려면:

```yaml
featureGates:
  "EphemeralContainers": true
  "PodSecurity": true
  
nodes:
  - role: control-plane
    kubeadmConfigPatches:
    - |
      kind: ClusterConfiguration
      apiServer:
        extraArgs:
          "feature-gates": "EphemeralContainers=true,PodSecurity=true"
      controller-manager:
        extraArgs:
          "feature-gates": "EphemeralContainers=true,PodSecurity=true"
      scheduler:
        extraArgs:
          "feature-gates": "EphemeralContainers=true,PodSecurity=true"
    - |
      kind: InitConfiguration
      nodeRegistration:
        kubeletExtraArgs:
          "feature-gates": "EphemeralContainers=true,PodSecurity=true"
```

### 로컬 이미지 로드

로컬에서 빌드한 이미지를 Kind 클러스터에 로드:

```bash
# 이미지 빌드
docker build -t myapp:latest .

# Kind 클러스터에 로드
kind load docker-image myapp:latest --name myk8s

# 로드된 이미지 확인
docker exec -it myk8s-control-plane crictl images | grep myapp
```

### HostPath를 사용한 PersistentVolume 생성

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: jenkins-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /private/var/persist/jenkins
    type: DirectoryOrCreate
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: app
          operator: In
          values:
          - jenkins
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
