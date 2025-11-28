# Kind 클러스터에서 Vault 배포

이 가이드는 macOS 환경에서 Kind (Kubernetes in Docker) 클러스터에 HashiCorp Vault를 배포하는 방법을 단계별로 설명합니다.

## 사전 요구사항

### 필수 도구 설치

```bash
# Homebrew 설치 (이미 설치되어 있다면 생략)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Docker Desktop 설치
brew install --cask docker

# Kind 설치
brew install kind

# kubectl 설치
brew install kubectl

# Helm 설치
brew install helm

# jq 설치 (JSON 파싱용)
brew install jq
```

### Docker Desktop 실행

Docker Desktop을 실행하고 Docker daemon이 시작될 때까지 기다립니다.

```bash
# Docker 상태 확인
docker ps
```

## 1단계: Kind 클러스터 생성

### 클러스터 설정 파일 생성

```bash
cat <<EOF > kind-vault-cluster.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: vault-demo
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30000
    hostPort: 8200
    protocol: TCP
  - containerPort: 30001
    hostPort: 8201
    protocol: TCP
EOF
```

**설정 설명**:
- `extraPortMappings`: Vault UI(8200) 및 API(8201) 포트를 로컬에서 접근 가능하도록 매핑

### 클러스터 생성

```bash
kind create cluster --config kind-vault-cluster.yaml
```

### 클러스터 확인

```bash
kubectl cluster-info
kubectl get nodes
```

## 2단계: Vault Helm Chart 설치

### Helm 저장소 추가

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
```

### Vault values 파일 생성

`examples/vault-values.yaml` 파일을 생성합니다 (이미 제공된 경우 사용):

```yaml
# Vault 서버 설정
server:
  # 개발 모드로 실행 (운영 환경에서는 사용하지 마세요)
  dev:
    enabled: false
    
  # Standalone 모드로 실행
  standalone:
    enabled: true
    config: |
      ui = true
      
      listener "tcp" {
        tls_disable = 1
        address = "[::]:8200"
        cluster_address = "[::]:8201"
      }
      storage "file" {
        path = "/vault/data"
      }
  
  # NodePort 서비스로 외부 접근 허용
  service:
    type: NodePort
    nodePort: 30000
  
  # 데이터 영구 저장
  dataStorage:
    enabled: true
    size: 10Gi
  
  # 리소스 제한
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

# Vault UI 활성화
ui:
  enabled: true
  serviceType: NodePort
  serviceNodePort: 30000

# Injector (사이드카 방식, VSO 사용 시 불필요할 수 있음)
injector:
  enabled: true
```

### Vault 설치

```bash
# vault namespace 생성
kubectl create namespace vault

# Helm으로 Vault 설치
helm install vault hashicorp/vault \
  --namespace vault \
  --values examples/vault-values.yaml

# Pod 상태 확인
kubectl get pods -n vault -w
```

## 3단계: Vault 초기화 및 Unsealing

### Vault Pod에 접속

```bash
kubectl exec -n vault -it vault-0 -- sh
```

### Vault 초기화

```bash
# Vault 초기화 (5개의 키 조각, 3개로 unsealing)
vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -format=json > /tmp/vault-init.json

# 출력 확인
cat /tmp/vault-init.json
```

**중요**: 출력된 Unseal Keys와 Root Token을 안전한 곳에 저장하세요!

### 초기화 결과를 로컬에 저장

```bash
# 다른 터미널에서 실행
kubectl cp vault/vault-0:/tmp/vault-init.json ./vault-init.json

# Unseal Keys 추출
cat vault-init.json | jq -r '.unseal_keys_b64[]'

# Root Token 추출
cat vault-init.json | jq -r '.root_token'
```

### Vault Unsealing

```bash
# Vault Pod 내에서 실행
# Unseal Key 3개를 순서대로 입력
vault operator unseal <KEY_1>
vault operator unseal <KEY_2>
vault operator unseal <KEY_3>

# Unseal 상태 확인
vault status
```

**출력 예시**:
```
Sealed          false
```

### Root Token으로 로그인

```bash
vault login <ROOT_TOKEN>
```

## 4단계: Kubernetes 인증 방법 설정

Kubernetes Pod가 Vault에 인증할 수 있도록 설정합니다.

### Kubernetes 인증 활성화

```bash
# Vault Pod 내에서 실행
vault auth enable kubernetes
```

### Kubernetes 인증 구성

```bash
# Kubernetes API 서버 정보 설정
vault write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"
```

### 테스트용 정책 생성

```bash
# myapp-policy 생성
vault policy write myapp-policy - <<EOF
path "secret/data/myapp/*" {
  capabilities = ["read", "list"]
}
EOF
```

### Kubernetes Role 생성

```bash
vault write auth/kubernetes/role/myapp-role \
  bound_service_account_names=myapp-sa \
  bound_service_account_namespaces=default \
  policies=myapp-policy \
  ttl=24h
```

**설명**:
- `bound_service_account_names`: 허용할 ServiceAccount 이름
- `bound_service_account_namespaces`: 허용할 Namespace
- `policies`: 이 Role에 연결할 정책
- `ttl`: 토큰 유효 기간

## 5단계: KV Secret Engine 활성화 및 테스트

### KV v2 Secret Engine 활성화

```bash
vault secrets enable -version=2 -path=secret kv
```

### 테스트 Secret 생성

```bash
vault kv put secret/myapp/database \
  username="dbuser" \
  password="dbpassword" \
  host="postgres.default.svc.cluster.local" \
  port="5432"

# Secret 읽기 (vault read 사용 권장)
vault read secret/data/myapp/database

# 또는 vault kv get 사용 (UI 권한 필요)
# vault kv get secret/myapp/database
```

## 6단계: 로컬에서 Vault 접근

### 환경 변수 설정

```bash
# 로컬 터미널에서 실행
export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='<ROOT_TOKEN>'

# Vault 상태 확인
vault status
```

### Vault UI 접근

브라우저에서 `http://localhost:8200`을 엽니다.

1. Root Token으로 로그인
2. Secrets 엔진 확인
3. 생성한 Secret 확인

## 7단계: ServiceAccount 및 Pod 테스트

### ServiceAccount 생성

```bash
# 로컬 터미널에서 실행
kubectl create serviceaccount myapp-sa
```

### 테스트 Pod 배포

```yaml
# test-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: vault-test
spec:
  serviceAccountName: myapp-sa
  containers:
  - name: vault-client
    image: hashicorp/vault:latest
    command: ['sh', '-c', 'sleep 3600']
    env:
    - name: VAULT_ADDR
      value: "http://vault.vault.svc.cluster.local:8200"
```

```bash
kubectl apply -f test-pod.yaml

# Pod가 실행될 때까지 대기
kubectl wait --for=condition=ready pod/vault-test --timeout=60s
```

### Pod에서 Vault 인증 테스트

```bash
# Pod에 접속
kubectl exec -it vault-test -- sh

# ServiceAccount 토큰 가져오기
KUBE_TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)

# Vault에 로그인
VAULT_TOKEN=$(vault write -field=token auth/kubernetes/login \
  role=myapp-role \
  jwt=$KUBE_TOKEN)

export VAULT_TOKEN

# Secret 읽기 - vault read 명령어 사용
vault read secret/data/myapp/database
```

**성공 시 출력**:
```
====== Data ======
Key         Value
---         -----
host        postgres.default.svc.cluster.local
password    dbpassword
port        5432
username    dbuser
```

## 운영 환경을 위한 고려사항

> [!WARNING]
> 이 가이드의 설정은 **학습 및 개발 목적**입니다. 운영 환경에서는 다음을 고려해야 합니다:

### 1. High Availability (HA)

```yaml
# HA 모드 설정 예시
server:
  ha:
    enabled: true
    replicas: 3
  standalone:
    enabled: false
```

### 2. Auto-Unseal

```yaml
# AWS KMS를 사용한 Auto-Unseal 예시
server:
  extraEnvironmentVars:
    VAULT_SEAL_TYPE: awskms
    VAULT_AWSKMS_SEAL_KEY_ID: "your-kms-key-id"
```

### 3. TLS 활성화

```yaml
listener "tcp" {
  tls_disable = 0
  tls_cert_file = "/vault/tls/tls.crt"
  tls_key_file = "/vault/tls/tls.key"
}
```

### 4. 영구 스토리지 백엔드

운영 환경에서는 Consul, etcd, 또는 클라우드 스토리지를 사용하세요:

```yaml
storage "consul" {
  address = "consul.service.consul:8500"
  path = "vault/"
}
```

### 5. 감사 로그 활성화

```bash
vault audit enable file file_path=/vault/logs/audit.log
```

## 트러블슈팅

### Vault Pod가 시작되지 않는 경우

```bash
# Pod 로그 확인
kubectl logs -n vault vault-0

# Pod 상세 정보 확인
kubectl describe pod -n vault vault-0
```

### Unsealing이 되지 않는 경우

```bash
# Vault 상태 확인
kubectl exec -n vault vault-0 -- vault status

# 수동으로 Unseal
kubectl exec -n vault vault-0 -- vault operator unseal <KEY>
```

### Kubernetes 인증 실패 시

```bash
# Vault에서 Kubernetes 인증 설정 확인
kubectl exec -n vault vault-0 -- vault read auth/kubernetes/config

# ServiceAccount 확인
kubectl get serviceaccount myapp-sa
kubectl describe serviceaccount myapp-sa
```

## 다음 단계

Vault가 성공적으로 배포되었습니다! 다음 문서로 진행하세요:

- [Vault Secrets Operator (VSO)](./04-vault-secrets-operator.md): Kubernetes Secret을 Vault와 동기화

## 참고 자료

- [Vault on Kubernetes Deployment Guide](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-raft-deployment-guide)
- [Vault Helm Chart](https://github.com/hashicorp/vault-helm)
- [Kind Documentation](https://kind.sigs.k8s.io/)
