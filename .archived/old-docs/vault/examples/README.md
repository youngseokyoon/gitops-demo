# Vault Examples

이 디렉토리에는 Vault 실습에 필요한 모든 예제 파일이 포함되어 있습니다.

## 파일 목록

### Vault 설치 및 구성

- **vault-values.yaml**: Helm을 사용한 Vault 설치 시 사용하는 values 파일
  
  ```bash
  helm install vault hashicorp/vault -n vault --values vault-values.yaml
  ```

### VSO (Vault Secrets Operator) 리소스

- **vault-connection.yaml**: VSO가 Vault에 연결하는 설정
- **vault-auth.yaml**: VSO가 Vault에 인증하는 방법 정의

  ```bash
  kubectl apply -f vault-connection.yaml
  kubectl apply -f vault-auth.yaml
  ```

### Static Secrets

- **static-secret-example.yaml**: VaultStaticSecret 사용 예제
  - VaultStaticSecret CR
  - ServiceAccount
  - 테스트 Pod

  ```bash
  kubectl apply -f static-secret-example.yaml
  ```

### Dynamic Secrets

- **dynamic-secret-example.yaml**: VaultDynamicSecret 기본 사용 예제
  - VaultDynamicSecret CR
  - 애플리케이션 Deployment

  ```bash
  kubectl apply -f dynamic-secret-example.yaml
  ```

- **postgres-dynamic-secret.yaml**: PostgreSQL Dynamic Secrets 전체 예제
  - PostgreSQL 배포
  - Vault 설정
  - Dynamic Secret 사용

  ```bash
  kubectl apply -f postgres-dynamic-secret.yaml
  ```

### Jenkins

- **Jenkinsfile**: Jenkins Pipeline에서 Vault Dynamic Secrets 사용 예제

## 사용 순서

### 1단계: Vault 설치

```bash
# Vault 설치
helm install vault hashicorp/vault \
  --namespace vault \
  --create-namespace \
  --values vault-values.yaml

# Vault 초기화 (문서 참조)
kubectl exec -n vault vault-0 -- vault operator init
kubectl exec -n vault vault-0 -- vault operator unseal <KEY>
```

### 2단계: VSO 설치

```bash
# VSO 설치
helm install vault-secrets-operator hashicorp/vault-secrets-operator \
  --namespace vault-secrets-operator-system \
  --create-namespace
```

### 3단계: VSO 리소스 배포

```bash
kubectl apply -f vault-connection.yaml
kubectl apply -f vault-auth.yaml
```

### 4단계: Static Secrets 테스트

```bash
# Vault에 Secret 생성
kubectl exec -n vault vault-0 -- vault kv put secret/myapp/database \
  username=dbuser \
  password=dbpassword \
  host=postgres.default.svc.cluster.local \
  port=5432

# VaultStaticSecret 배포
kubectl apply -f static-secret-example.yaml

# 확인
kubectl get secret myapp-database -o yaml
kubectl logs myapp-test
```

### 5단계: Dynamic Secrets 테스트

```bash
# PostgreSQL 배포 (전체 예제)
kubectl apply -f postgres-dynamic-secret.yaml

# Database Secret Engine 설정 (Vault Pod에서)
kubectl exec -n vault vault-0 -- sh
vault secrets enable database
vault write database/config/postgresql \
  plugin_name=postgresql-database-plugin \
  allowed_roles="readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@postgres.default.svc.cluster.local:5432/myappdb?sslmode=disable" \
  username="vaultadmin" \
  password="vaultpassword"

vault write database/roles/readwrite \
  db_name=postgresql \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# 확인
kubectl logs -f deployment/postgres-app
```

## 트러블슈팅

### VaultStaticSecret이 동기화되지 않는 경우

```bash
# VSO 로그 확인
kubectl logs -n vault-secrets-operator-system \
  deployment/vault-secrets-operator-controller-manager

# VaultStaticSecret 상태 확인
kubectl describe vaultstaticsecret myapp-database-secret
```

### VaultDynamicSecret이 작동하지 않는 경우

```bash
# Database 연결 확인
kubectl exec -n vault vault-0 -- vault read database/config/postgresql

# Role 확인
kubectl exec -n vault vault-0 -- vault read database/roles/readwrite

# 수동으로 Secret 생성 테스트
kubectl exec -n vault vault-0 -- vault read database/creds/readwrite
```

## 참고 사항

> [!IMPORTANT]
> 이 예제 파일들은 학습 및 개발 목적입니다. 운영 환경에서는 다음을 고려하세요:
> 
> - TLS 활성화
> - 적절한 리소스 제한
> - High Availability 설정
> - Backup 및 Disaster Recovery 계획
> - 보안 정책 강화

## 관련 문서

- [Vault 개요](../01-vault-overview.md)
- [Kind 클러스터 배포](../03-kind-deployment.md)
- [Vault Secrets Operator](../04-vault-secrets-operator.md)
- [Dynamic Secrets](../05-dynamic-secrets.md)
- [Jenkins 통합](../06-jenkins-integration.md)
