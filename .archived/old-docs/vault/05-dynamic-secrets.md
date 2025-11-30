# Dynamic Secrets

Dynamic Secrets는 Vault의 가장 강력한 기능 중 하나로, 요청 시 동적으로 생성되고 제한된 수명을 가지는 자격 증명입니다.

## Dynamic Secrets란?

### 정의

**Dynamic Secrets**는 애플리케이션이 요청할 때 Vault가 즉석에서 생성하는 임시 자격 증명입니다. 이러한 자격 증명은 사전 정의된 TTL (Time To Live)을 가지며, 만료 시 자동으로 폐기됩니다.

### Static Secrets vs Dynamic Secrets

| 특성 | Static Secrets | Dynamic Secrets |
|------|---------------|-----------------|
| **생성 방식** | 수동으로 생성 및 저장 | 요청 시 자동 생성 |
| **수명** | 명시적으로 삭제하기 전까지 영구 | 제한된 TTL (자동 만료) |
| **순환** | 수동 순환 필요 | 자동 순환 |
| **유출 위험** | 높음 (장기간 유효) | 낮음 (단기간 유효) |
| **감사** | 어려움 | 쉬움 (Lease 추적) |
| **예시** | API 키, 고정 비밀번호 | DB 자격 증명, AWS 임시 키 |

## Dynamic Secrets의 장점

### 1. 보안 강화

```mermaid
graph LR
    subgraph "Static Secrets"
        A1[생성] --> A2[저장]
        A2 --> A3[사용]
        A3 --> A4[영구 유효]
        A4 -.유출 위험.-> A5[⚠️ 장기간 노출]
    end
    
    subgraph "Dynamic Secrets"
        B1[요청] --> B2[동적 생성]
        B2 --> B3[사용]
        B3 --> B4[TTL 만료]
        B4 --> B5[✅ 자동 폐기]
    end
```

**주요 이점**:
- **단기 자격 증명**: 유출되더라도 짧은 시간만 유효
- **자동 폐기**: TTL 만료 시 자동으로 무효화
- **최소 권한 기간**: 필요한 시간만큼만 유효

### 2. 자동 순환

Static Secret은 수동으로 순환해야 하지만, Dynamic Secret은 자동으로 순환됩니다:

```bash
# Static Secret: 수동 순환
vault kv put secret/app/db password=newpassword123  # 수동 변경
# 모든 애플리케이션을 재시작하여 새 비밀번호 로드 필요

# Dynamic Secret: 자동 순환
# Lease 갱신만 하면 Vault가 자동으로 새 자격 증명 생성
```

### 3. 감사 및 추적

모든 Dynamic Secret은 Lease와 연결되어 추적 가능합니다:

```bash
# 누가, 언제, 어떤 자격 증명을 생성했는지 확인
vault list sys/leases/lookup/database/creds/my-role

# 특정 Lease 상세 정보
vault lease lookup database/creds/my-role/abc123
```

### 4. 즉각적인 폐기

보안 사고 발생 시 즉시 모든 자격 증명을 폐기할 수 있습니다:

```bash
# 특정 Lease 폐기
vault lease revoke database/creds/my-role/abc123

# 특정 경로의 모든 Lease 폐기
vault lease revoke -prefix database/creds/my-role
```

## 지원되는 Secret 엔진

Vault는 다양한 시스템을 위한 Dynamic Secrets를 지원합니다:

### 1. Database Secrets Engine

지원 데이터베이스:
- **PostgreSQL**
- **MySQL/MariaDB**
- **MongoDB**
- **Oracle**
- **MSSQL**
- **Cassandra**
- **Redis**

### 2. Cloud Provider Secrets

- **AWS**: IAM 사용자, STS 임시 자격 증명
- **Azure**: Service Principal, 관리 ID
- **GCP**: Service Account 키

### 3. SSH Secrets Engine

- 일회용 SSH 비밀번호 (OTP)
- 서명된 SSH 인증서

### 4. PKI Secrets Engine

- X.509 인증서 동적 발급

### 5. Active Directory/LDAP

- AD 계정 비밀번호 순환

## Database Dynamic Secrets 실습

### 환경 설정

#### 1. PostgreSQL 배포

```yaml
# postgres.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-init
data:
  init.sql: |
    -- Vault가 사용할 관리자 계정 생성
    CREATE USER vaultadmin WITH PASSWORD 'vaultpassword' SUPERUSER;
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
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
          value: myappdb
        - name: POSTGRES_USER
          value: postgres
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
```

```bash
kubectl apply -f postgres.yaml

# PostgreSQL 준비 확인
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
```

#### 2. Vault에서 Database Secret Engine 설정

```bash
# Vault Pod에 접속
kubectl exec -n vault -it vault-0 -- sh

# Database Secret Engine 활성화
vault secrets enable database

# PostgreSQL 연결 설정
vault write database/config/postgresql \
  plugin_name=postgresql-database-plugin \
  allowed_roles="readonly,readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@postgres.default.svc.cluster.local:5432/myappdb?sslmode=disable" \
  username="vaultadmin" \
  password="vaultpassword"

# 연결 테스트
vault read database/config/postgresql
```

#### 3. Role 생성

**읽기 전용 Role**:

```bash
vault write database/roles/readonly \
  db_name=postgresql \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"
```

**읽기/쓰기 Role**:

```bash
vault write database/roles/readwrite \
  db_name=postgresql \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"
```

**설정 설명**:
- `creation_statements`: 새 사용자 생성 시 실행할 SQL
- `{{name}}`: Vault가 생성할 사용자명 (자동 생성)
- `{{password}}`: Vault가 생성할 비밀번호 (자동 생성)
- `{{expiration}}`: 자격 증명 만료 시간
- `default_ttl`: 기본 유효 기간
- `max_ttl`: 최대 유효 기간 (갱신 한계)

### Dynamic Secrets 생성 및 사용

#### CLI에서 테스트

```bash
# Dynamic Secret 생성
vault read database/creds/readonly

# 출력 예시:
# Key                Value
# ---                -----
# lease_id           database/creds/readonly/2f6a614c-4aa2-7b19-24b9-ad944a8d4de6
# lease_duration     1h
# lease_renewable    true
# password           A1a-y0xp0qz7rv3x5t2u
# username           v-root-readonly-x4sva5t8y1s3zu2w-1606833445
```

#### PostgreSQL에서 확인

```bash
# PostgreSQL Pod에 접속
kubectl exec -it deployment/postgres -- psql -U postgres -d myappdb

# 생성된 사용자 확인
\du

# 출력에서 v-root-readonly-... 형태의 사용자 확인
```

#### 생성된 자격 증명으로 접속

```bash
# 위에서 받은 username과 password 사용
kubectl exec -it deployment/postgres -- psql -U v-root-readonly-x4sva5t8y1s3zu2w-1606833445 -d myappdb

# 테이블 조회 (성공)
SELECT * FROM information_schema.tables;

# 테이블 생성 시도 (실패 - 읽기 전용)
CREATE TABLE test (id int);
# ERROR: permission denied for schema public
```

### Lease 관리

#### Lease 확인

```bash
# Lease 상세 정보
vault lease lookup database/creds/readonly/2f6a614c-4aa2-7b19-24b9-ad944a8d4de6

# 출력:
# Key             Value
# ---             -----
# expire_time     2025-11-28T14:30:45Z
# id              database/creds/readonly/2f6a614c-4aa2-7b19-24b9-ad944a8d4de6
# renewable       true
# ttl             59m30s
```

#### Lease 갱신

```bash
# Lease 갱신 (TTL 연장)
vault lease renew database/creds/readonly/2f6a614c-4aa2-7b19-24b9-ad944a8d4de6

# 증분으로 갱신 (30분 연장)
vault lease renew -increment=1800 database/creds/readonly/2f6a614c-4aa2-7b19-24b9-ad944a8d4de6
```

> [!IMPORTANT]
> Lease는 `max_ttl`을 초과하여 갱신할 수 없습니다. `max_ttl`에 도달하면 새로운 자격 증명을 생성해야 합니다.

#### Lease 폐기

```bash
# 특정 Lease 폐기
vault lease revoke database/creds/readonly/2f6a614c-4aa2-7b19-24b9-ad944a8d4de6

# PostgreSQL에서 사용자 삭제 확인
kubectl exec -it deployment/postgres -- psql -U postgres -d myappdb -c "\du"
# v-root-readonly-... 사용자가 삭제됨
```

## 애플리케이션 통합 예제

### Python 애플리케이션

```python
# app.py
import hvac
import psycopg2
import time
from threading import Thread

class VaultDBClient:
    def __init__(self, vault_url, vault_token, db_role):
        self.client = hvac.Client(url=vault_url, token=vault_token)
        self.db_role = db_role
        self.lease_id = None
        self.credentials = None
        self.renew_thread = None
        
    def get_db_credentials(self):
        """Vault에서 DB 자격 증명 가져오기"""
        response = self.client.read(f'database/creds/{self.db_role}')
        self.credentials = {
            'username': response['data']['username'],
            'password': response['data']['password']
        }
        self.lease_id = response['lease_id']
        self.lease_duration = response['lease_duration']
        
        # 자동 갱신 시작
        self.start_lease_renewal()
        return self.credentials
    
    def start_lease_renewal(self):
        """Lease 자동 갱신"""
        def renew_lease():
            # TTL의 2/3 시점에 갱신
            sleep_time = self.lease_duration * 2 / 3
            while True:
                time.sleep(sleep_time)
                try:
                    result = self.client.sys.renew_lease(self.lease_id)
                    print(f"Lease renewed: {result}")
                except Exception as e:
                    print(f"Failed to renew lease: {e}")
                    # 갱신 실패 시 새 자격 증명 가져오기
                    self.get_db_credentials()
                    break
        
        self.renew_thread = Thread(target=renew_lease, daemon=True)
        self.renew_thread.start()
    
    def get_db_connection(self):
        """PostgreSQL 연결"""
        if not self.credentials:
            self.get_db_credentials()
        
        return psycopg2.connect(
            host="postgres.default.svc.cluster.local",
            database="myappdb",
            user=self.credentials['username'],
            password=self.credentials['password']
        )
    
    def revoke_credentials(self):
        """자격 증명 폐기"""
        if self.lease_id:
            self.client.sys.revoke_lease(self.lease_id)

# 사용 예제
if __name__ == "__main__":
    vault_client = VaultDBClient(
        vault_url="http://vault.vault.svc.cluster.local:8200",
        vault_token="your-vault-token",
        db_role="readonly"
    )
    
    # DB 연결
    conn = vault_client.get_db_connection()
    cursor = conn.cursor()
    
    # 쿼리 실행
    cursor.execute("SELECT version();")
    print(cursor.fetchone())
    
    # 종료 시 자격 증명 폐기
    vault_client.revoke_credentials()
```

### Kubernetes CronJob 예제

주기적으로 실행되는 Job에 Dynamic Secrets 사용:

```yaml
# examples/cronjob-dynamic-secrets.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"  # 매일 오전 2시
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: myapp-sa
          initContainers:
          # Vault에서 자격 증명 가져오기
          - name: vault-agent
            image: hashicorp/vault:latest
            command:
            - sh
            - -c
            - |
              vault login -method=kubernetes role=myapp-role
              vault read -format=json database/creds/readwrite > /vault/secrets/db-creds.json
            env:
            - name: VAULT_ADDR
              value: "http://vault.vault.svc.cluster.local:8200"
            volumeMounts:
            - name: vault-secrets
              mountPath: /vault/secrets
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - sh
            - -c
            - |
              export PGUSER=$(cat /vault/secrets/db-creds.json | jq -r '.data.username')
              export PGPASSWORD=$(cat /vault/secrets/db-creds.json | jq -r '.data.password')
              pg_dump -h postgres -d myappdb > /backup/backup-$(date +%Y%m%d).sql
            volumeMounts:
            - name: vault-secrets
              mountPath: /vault/secrets
            - name: backup
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: vault-secrets
            emptyDir:
              medium: Memory  # 메모리에 저장 (보안 강화)
          - name: backup
            persistentVolumeClaim:
              claimName: backup-pvc
```

## Best Practices

### 1. 적절한 TTL 설정

```bash
# 단기 작업 (5분)
default_ttl="5m"
max_ttl="15m"

# 장시간 실행 애플리케이션 (1시간)
default_ttl="1h"
max_ttl="24h"
```

### 2. Graceful Degradation

자격 증명 갱신 실패 시 대비:

```python
def get_db_connection_with_retry(vault_client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return vault_client.get_db_connection()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                vault_client.get_db_credentials()  # 새 자격 증명
            else:
                raise
```

### 3. Lease 갱신 타이밍

TTL의 50-67% 시점에 갱신하는 것이 권장됩니다:

```python
renewal_time = lease_duration * 0.67
```

### 4. 보안 사고 대응

```bash
# 즉시 모든 DB 자격 증명 폐기
vault lease revoke -prefix database/creds/

# 특정 앱의 자격 증명만 폐기
vault lease revoke -prefix database/creds/myapp-role/
```

## 다음 단계

Dynamic Secrets의 개념과 사용법을 이해했습니다. 다음 문서로 진행하세요:

- [Jenkins를 활용한 Dynamic Secrets](./06-jenkins-integration.md): CI/CD 파이프라인에서 Dynamic Secrets 사용

## 참고 자료

- [Database Secrets Engine](https://developer.hashicorp.com/vault/docs/secrets/databases)
- [Lease, Renew, and Revoke](https://developer.hashicorp.com/vault/docs/concepts/lease)
- [Dynamic Secrets Best Practices](https://developer.hashicorp.com/vault/tutorials/secrets-management/database-secrets)
