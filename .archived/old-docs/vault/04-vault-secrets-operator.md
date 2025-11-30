# Vault Secrets Operator (VSO)

Vault Secrets Operator (VSO)는 Vault의 Secret을 Kubernetes Secret으로 동기화하는 공식 Kubernetes Operator입니다.

## VSO란?

VSO는 Vault와 Kubernetes를 연결하는 다리 역할을 하며, 다음과 같은 기능을 제공합니다:

- **자동 동기화**: Vault의 Secret을 Kubernetes Secret으로 자동 동기화
- **Dynamic Secrets 지원**: 데이터베이스 자격 증명 등 동적 Secret 관리
- **자동 갱신**: Secret이 만료되기 전에 자동으로 갱신
- **선언적 관리**: Kubernetes CR (Custom Resource)로 Secret 관리

## VSO vs Vault Agent Injector

| 기능 | VSO | Vault Agent Injector |
|------|-----|---------------------|
| 배포 방식 | Operator | Sidecar/Init Container |
| Secret 저장 | Kubernetes Secret | 파일 시스템 |
| 동기화 | 자동 동기화 | Pod 재시작 필요 |
| Dynamic Secrets | ✅ 지원 | ✅ 지원 |
| 리소스 사용 | 낮음 (중앙 집중식) | 높음 (Pod마다 Sidecar) |
| 기존 앱 통합 | 쉬움 | 중간 |

> [!TIP]
> VSO는 기존 애플리케이션을 수정하지 않고 Kubernetes Secret을 사용하는 방식으로 Vault를 도입할 수 있어 마이그레이션이 쉽습니다.

## VSO 아키텍처

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        VSO[Vault Secrets<br/>Operator]
        CRD1[VaultStaticSecret<br/>CR]
        CRD2[VaultDynamicSecret<br/>CR]
        K8sSecret[Kubernetes<br/>Secret]
        Pod[Application<br/>Pod]
    end
    
    subgraph "Vault"
        KV[KV Secret<br/>Engine]
        DB[Database Secret<br/>Engine]
    end
    
    CRD1 --> VSO
    CRD2 --> VSO
    VSO -->|인증| Vault
    VSO -->|Static Secret 읽기| KV
    VSO -->|Dynamic Secret 생성| DB
    VSO -->|생성/업데이트| K8sSecret
    K8sSecret -->|마운트| Pod
```

### 동작 흐름

1. **CR 생성**: 사용자가 `VaultStaticSecret` 또는 `VaultDynamicSecret` CR을 생성
2. **VSO 감지**: Operator가 새로운 CR을 감지
3. **Vault 인증**: VSO가 Kubernetes 인증 방법으로 Vault에 로그인
4. **Secret 가져오기**: 지정된 Vault 경로에서 Secret을 읽음
5. **K8s Secret 생성**: Kubernetes Secret을 생성하거나 업데이트
6. **지속적 동기화**: Secret 변경 사항을 주기적으로 확인하고 동기화

## VSO 설치

### Helm으로 설치

```bash
# Helm 저장소 추가 (이미 있다면 생략)
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

# VSO 설치
helm install vault-secrets-operator hashicorp/vault-secrets-operator \
  --namespace vault-secrets-operator-system \
  --create-namespace

# 설치 확인
kubectl get pods -n vault-secrets-operator-system
```

### 수동 설치 (YAML)

```bash
# 최신 릴리스 다운로드
kubectl apply -f https://github.com/hashicorp/vault-secrets-operator/releases/latest/download/vault-secrets-operator.yaml

# 설치 확인
kubectl get deployment -n vault-secrets-operator-system
```

## VaultConnection 설정

VSO가 Vault에 연결하려면 `VaultConnection` 리소스를 생성해야 합니다.

```yaml
# examples/vault-connection.yaml
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultConnection
metadata:
  name: default
  namespace: default
spec:
  # Vault 주소
  address: http://vault.vault.svc.cluster.local:8200
  
  # Skip TLS verification (개발 환경용)
  skipTLSVerify: true
```

```bash
kubectl apply -f examples/vault-connection.yaml
```

## VaultAuth 설정

VSO가 Vault에 인증하는 방법을 정의합니다.

```yaml
# examples/vault-auth.yaml
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultAuth
metadata:
  name: default
  namespace: default
spec:
  # VaultConnection 참조
  vaultConnectionRef: default
  
  # Kubernetes 인증 방법 사용
  method: kubernetes
  mount: kubernetes
  
  kubernetes:
    role: myapp-role
    serviceAccount: myapp-sa
```

```bash
kubectl apply -f examples/vault-auth.yaml
```

## VaultStaticSecret 사용

정적 Secret (KV Secret Engine)을 동기화합니다.

### 예제 1: 기본 사용

```yaml
# examples/static-secret-example.yaml
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultStaticSecret
metadata:
  name: myapp-database-secret
  namespace: default
spec:
  # VaultAuth 참조
  vaultAuthRef: default
  
  # Vault의 KV 경로
  mount: secret
  type: kv-v2
  path: myapp/database
  
  # 동기화할 Kubernetes Secret
  destination:
    name: myapp-database
    create: true
  
  # 갱신 간격 (기본값: 60초)
  refreshAfter: 30s
```

```bash
kubectl apply -f examples/static-secret-example.yaml

# 생성된 Kubernetes Secret 확인
kubectl get secret myapp-database -o yaml
```

### 예제 2: 특정 필드만 선택

```yaml
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultStaticSecret
metadata:
  name: myapp-api-keys
  namespace: default
spec:
  vaultAuthRef: default
  mount: secret
  type: kv-v2
  path: myapp/api-keys
  
  destination:
    name: myapp-api-keys
    create: true
    
  # 특정 필드만 동기화
  hmacSecretData: false
  
  # 필드 변환
  destination:
    name: api-keys
    create: true
    transformation:
      excludes:
        - internal_key
      includes:
        - public_key
        - private_key
```

### 예제 3: Pod에서 사용

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  namespace: default
spec:
  serviceAccountName: myapp-sa
  containers:
  - name: app
    image: nginx:latest
    env:
    # 환경 변수로 사용
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: myapp-database
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: myapp-database
          key: password
    # 또는 볼륨으로 마운트
    volumeMounts:
    - name: db-creds
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: db-creds
    secret:
      secretName: myapp-database
```

## VaultDynamicSecret 사용

동적 Secret (Database Secret Engine 등)을 관리합니다.

### Vault에서 Database Secret Engine 설정

먼저 Vault에서 Database Secret Engine을 설정해야 합니다:

```bash
# Vault Pod에 접속
kubectl exec -n vault -it vault-0 -- sh

# Database Secret Engine 활성화
vault secrets enable database

# PostgreSQL 연결 설정
vault write database/config/my-postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="myapp-db-role" \
  connection_url="postgresql://{{username}}:{{password}}@postgres.default.svc.cluster.local:5432/mydb?sslmode=disable" \
  username="vaultadmin" \
  password="vaultpassword"

# Role 생성 (동적 자격 증명 정의)
vault write database/roles/myapp-db-role \
  db_name=my-postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# 정책 생성
vault policy write myapp-db-policy - <<EOF
path "database/creds/myapp-db-role" {
  capabilities = ["read"]
}
EOF

# Kubernetes Role 업데이트
vault write auth/kubernetes/role/myapp-role \
  bound_service_account_names=myapp-sa \
  bound_service_account_namespaces=default \
  policies=myapp-policy,myapp-db-policy \
  ttl=24h
```

### VaultDynamicSecret CR 생성

```yaml
# examples/dynamic-secret-example.yaml
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultDynamicSecret
metadata:
  name: myapp-db-creds
  namespace: default
spec:
  vaultAuthRef: default
  
  # Database Secret Engine 경로
  mount: database
  path: creds/myapp-db-role
  
  # 동기화할 Kubernetes Secret
  destination:
    name: myapp-db-dynamic
    create: true
  
  # Lease 설정
  renewalPercent: 67  # TTL의 67%가 지나면 갱신
  revoke: true        # CR 삭제 시 Vault에서 Secret 폐기
  
  # 롤백 설정
  rolloutRestartTargets:
    - kind: Deployment
      name: myapp
```

**주요 설정**:
- `renewalPercent`: Secret을 갱신할 시점 (TTL의 퍼센트)
- `revoke`: CR 삭제 시 Vault에서 Secret 폐기 여부
- `rolloutRestartTargets`: Secret 갱신 시 자동으로 재시작할 리소스

```bash
kubectl apply -f examples/dynamic-secret-example.yaml

# 생성된 Secret 확인
kubectl get secret myapp-db-dynamic -o jsonpath='{.data.username}' | base64 -d
kubectl get secret myapp-db-dynamic -o jsonpath='{.data.password}' | base64 -d
```

### Dynamic Secret 동작 확인

```bash
# VaultDynamicSecret 상태 확인
kubectl describe vaultdynamicsecret myapp-db-creds

# Lease 정보 확인
kubectl get vaultdynamicsecret myapp-db-creds -o jsonpath='{.status.secretLease}'

# Secret 자동 갱신 모니터링
kubectl get secret myapp-db-dynamic -w
```

## 실습: 전체 워크플로우

### 1. PostgreSQL 배포

```yaml
# postgres-deployment.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-init
data:
  init.sql: |
    CREATE USER vaultadmin WITH PASSWORD 'vaultpassword' SUPERUSER;
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: mydb
        - name: POSTGRES_PASSWORD
          value: rootpassword
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: init-script
          mountPath: /docker-entrypoint-initdb.d
      volumes:
      - name: init-script
        configMap:
          name: postgres-init
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

```bash
kubectl apply -f postgres-deployment.yaml
```

### 2. Vault 설정 (위의 Database Secret Engine 설정 실행)

### 3. VSO 리소스 배포

```bash
kubectl apply -f examples/vault-connection.yaml
kubectl apply -f examples/vault-auth.yaml
kubectl apply -f examples/dynamic-secret-example.yaml
```

### 4. 애플리케이션 배포

```yaml
# myapp-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      serviceAccountName: myapp-sa
      containers:
      - name: app
        image: postgres:15-alpine
        command: ['sh', '-c', 'while true; do psql postgresql://$DB_USERNAME:$DB_PASSWORD@postgres:5432/mydb -c "SELECT version();"; sleep 60; done']
        env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: myapp-db-dynamic
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: myapp-db-dynamic
              key: password
```

```bash
kubectl apply -f myapp-deployment.yaml

# 로그에서 데이터베이스 연결 확인
kubectl logs -f deployment/myapp
```

### 5. Secret 자동 갱신 테스트

```bash
# 현재 username 확인
kubectl get secret myapp-db-dynamic -o jsonpath='{.data.username}' | base64 -d

# 1시간 후 (또는 설정한 renewalPercent 시점) username이 변경되는지 확인
# VSO가 자동으로 Secret을 갱신하고 Pod를 재시작합니다
```

## 트러블슈팅

### VSO가 Secret을 동기화하지 않는 경우

```bash
# VSO Operator 로그 확인
kubectl logs -n vault-secrets-operator-system deployment/vault-secrets-operator-controller-manager

# VaultConnection 상태 확인
kubectl describe vaultconnection default

# VaultAuth 상태 확인
kubectl describe vaultauth default

# VaultStaticSecret 또는 VaultDynamicSecret 상태 확인
kubectl describe vaultstaticsecret myapp-database-secret
```

### 인증 실패

```bash
# ServiceAccount 확인
kubectl get serviceaccount myapp-sa

# Vault에서 Role 확인
kubectl exec -n vault vault-0 -- vault read auth/kubernetes/role/myapp-role

# Policy 확인
kubectl exec -n vault vault-0 -- vault policy read myapp-policy
```

### Dynamic Secret이 갱신되지 않는 경우

```bash
# Lease 정보 확인
kubectl get vaultdynamicsecret myapp-db-creds -o yaml

# Vault에서 Lease 확인
kubectl exec -n vault vault-0 -- vault list sys/leases/lookup/database/creds/myapp-db-role
```

## Best Practices

### 1. Namespace 분리

환경별로 Namespace를 분리하고 각각 별도의 VaultAuth를 사용하세요:

```yaml
# dev namespace
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultAuth
metadata:
  name: default
  namespace: dev
spec:
  kubernetes:
    role: dev-role
    serviceAccount: dev-sa
```

### 2. 최소 권한 원칙

각 애플리케이션에 필요한 최소한의 Secret만 접근할 수 있도록 정책을 설정하세요.

### 3. Secret 순환

Dynamic Secrets를 사용하여 자격 증명을 자동으로 순환하세요.

### 4. 모니터링

VSO 메트릭을 모니터링하여 동기화 실패를 감지하세요:

```bash
# Prometheus 메트릭 확인
kubectl port-forward -n vault-secrets-operator-system svc/vault-secrets-operator-controller-manager-metrics-service 8443:8443
curl -k https://localhost:8443/metrics
```

## 다음 단계

VSO를 통해 Vault와 Kubernetes를 성공적으로 통합했습니다. 다음 문서로 진행하세요:

- [Dynamic Secrets](./05-dynamic-secrets.md): Dynamic Secrets의 개념과 다양한 사용 사례

## 참고 자료

- [Vault Secrets Operator 공식 문서](https://developer.hashicorp.com/vault/docs/platform/k8s/vso)
- [VSO GitHub Repository](https://github.com/hashicorp/vault-secrets-operator)
- [VSO API Reference](https://developer.hashicorp.com/vault/docs/platform/k8s/vso/api-reference)
