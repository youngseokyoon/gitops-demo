# Jenkins를 활용한 Dynamic Secrets

이 가이드는 Jenkins CI/CD 파이프라인에서 Vault Dynamic Secrets를 사용하는 방법을 설명합니다.

## 개요

CI/CD 파이프라인에서 Dynamic Secrets를 사용하면 다음과 같은 이점이 있습니다:

- **보안 강화**: 빌드마다 새로운 자격 증명 사용
- **자동 폐기**: 빌드 완료 후 자격 증명 자동 삭제
- **감사 추적**: 어떤 빌드가 어떤 자격 증명을 사용했는지 추적
- **권한 분리**: 각 프로젝트별로 다른 Vault 권한 부여

## 아키텍처

```mermaid
sequenceDiagram
    participant Jenkins
    participant Vault
    participant DB as Database
    participant App as Application

    Jenkins->>Vault: 1. AppRole로 인증
    Vault-->>Jenkins: Vault Token
    
    Jenkins->>Vault: 2. DB 자격 증명 요청
    Vault->>DB: 3. 새 사용자 생성
    DB-->>Vault: 사용자 생성 완료
    Vault-->>Jenkins: 4. username/password + Lease
    
    Jenkins->>DB: 5. 마이그레이션/테스트 실행
    Jenkins->>App: 6. 애플리케이션 빌드/배포
    
    Jenkins->>Vault: 7. Lease 폐기
    Vault->>DB: 8. 사용자 삭제
```

## 사전 요구사항

### Jenkins 설치

```bash
# Helm으로 Jenkins 설치
helm repo add jenkins https://charts.jenkins.io
helm repo update

# jenkins namespace 생성
kubectl create namespace jenkins

# Jenkins 설치
helm install jenkins jenkins/jenkins \
  --namespace jenkins \
  --set controller.serviceType=NodePort \
  --set controller.nodePort=30080

# 초기 admin 비밀번호 확인
kubectl exec -n jenkins jenkins-0 -- cat /run/secrets/additional/chart-admin-password
```

### Vault 플러그인 설치

Jenkins UI에서:
1. **Manage Jenkins** → **Manage Plugins**
2. **Available** 탭에서 "HashiCorp Vault" 검색
3. **HashiCorp Vault Plugin** 설치
4. Jenkins 재시작

## Vault 설정

### 1. AppRole 인증 방법 활성화

Jenkins는 AppRole 인증 방법을 사용합니다:

```bash
# Vault Pod에 접속
kubectl exec -n vault -it vault-0 -- sh

# AppRole 활성화
vault auth enable approle
```

### 2. Jenkins용 정책 생성

```bash
# Jenkins가 DB Secret을 생성할 수 있는 정책
vault policy write jenkins-policy - <<EOF
# Database Dynamic Secrets 읽기
path "database/creds/readwrite" {
  capabilities = ["read"]
}

# KV Secret 읽기 (빌드 설정 등)
path "secret/data/jenkins/*" {
  capabilities = ["read", "list"]
}

# Token 갱신 허용
path "auth/token/renew-self" {
  capabilities = ["update"]
}

# Token 폐기 허용
path "auth/token/revoke-self" {
  capabilities = ["update"]
}
EOF
```

### 3. AppRole 생성

```bash
# AppRole 생성
vault write auth/approle/role/jenkins \
  token_ttl=1h \
  token_max_ttl=4h \
  policies="jenkins-policy"

# Role ID 가져오기
vault read auth/approle/role/jenkins/role-id

# 출력 예시:
# role_id     1234abcd-56ef-78gh-90ij-klmnopqrstuv

# Secret ID 생성
vault write -f auth/approle/role/jenkins/secret-id

# 출력 예시:
# secret_id   abcd1234-efgh-5678-ijkl-mnopqrstuvwx
```

> [!IMPORTANT]
> Role ID와 Secret ID를 안전하게 보관하세요. 이 두 값으로 Vault에 인증합니다.

### 4. Database Secret Engine 설정 (이미 했다면 생략)

```bash
# Database Secret Engine 활성화
vault secrets enable database

# PostgreSQL 연결 설정
vault write database/config/postgresql \
  plugin_name=postgresql-database-plugin \
  allowed_roles="readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@postgres.default.svc.cluster.local:5432/myappdb?sslmode=disable" \
  username="vaultadmin" \
  password="vaultpassword"

# Role 생성
vault write database/roles/readwrite \
  db_name=postgresql \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="30m" \
  max_ttl="1h"
```

## Jenkins 설정

### 1. Vault 플러그인 전역 설정

Jenkins UI에서:

1. **Manage Jenkins** → **Configure System**
2. **Vault** 섹션으로 스크롤
3. 다음 정보 입력:
   - **Vault URL**: `http://vault.vault.svc.cluster.local:8200`
   - **Vault Credential**: (새로 생성)
     - **Kind**: Vault App Role Credential
     - **Role ID**: (위에서 받은 Role ID)
     - **Secret ID**: (위에서 받은 Secret ID)

### 2. Jenkins Credential 생성 (선택사항)

**Manage Jenkins** → **Manage Credentials** → **Global** → **Add Credentials**

- **Kind**: Vault App Role Credential
- **ID**: vault-approle
- **Role ID**: 1234abcd-56ef-78gh-90ij-klmnopqrstuv
- **Secret ID**: abcd1234-efgh-5678-ijkl-mnopqrstuvwx

## Pipeline 예제

### 예제 1: 기본 사용

```groovy
// examples/Jenkinsfile-basic
@Library('shared-library') _

pipeline {
    agent any
    
    options {
        // Vault 설정
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    environment {
        VAULT_ADDR = 'http://vault.vault.svc.cluster.local:8200'
    }
    
    stages {
        stage('Get Database Credentials') {
            steps {
                script {
                    // Vault에서 Dynamic Secret 가져오기
                    def secrets = [
                        [
                            path: 'database/creds/readwrite',
                            engineVersion: 1,
                            secretValues: [
                                [envVar: 'DB_USERNAME', vaultKey: 'username'],
                                [envVar: 'DB_PASSWORD', vaultKey: 'password']
                            ]
                        ]
                    ]
                    
                    def configuration = [
                        vaultUrl: env.VAULT_ADDR,
                        vaultCredentialId: 'vault-approle',
                        engineVersion: 1
                    ]
                    
                    withVault([configuration: configuration, vaultSecrets: secrets]) {
                        echo "Database Username: ${env.DB_USERNAME}"
                        // 비밀번호는 로그에 출력하지 마세요!
                        
                        // 데이터베이스 마이그레이션
                        sh '''
                            echo "Running database migration..."
                            PGPASSWORD=$DB_PASSWORD psql -h postgres -U $DB_USERNAME -d myappdb -c "SELECT version();"
                        '''
                    }
                }
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building application...'
                sh 'make build'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'make test'
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed. Vault automatically revoked credentials.'
        }
    }
}
```

**특징**:
- `withVault` 블록을 벗어나면 Vault Token이 자동으로 폐기됨
- Pipeline 실패 시에도 자격 증명이 안전하게 폐기됨

### 예제 2: Database 마이그레이션

```groovy
// examples/Jenkinsfile-migration
pipeline {
    agent any
    
    environment {
        VAULT_ADDR = 'http://vault.vault.svc.cluster.local:8200'
        DB_HOST = 'postgres.default.svc.cluster.local'
        DB_NAME = 'myappdb'
    }
    
    stages {
        stage('Run Database Migration') {
            steps {
                script {
                    def secrets = [
                        [
                            path: 'database/creds/readwrite',
                            secretValues: [
                                [envVar: 'DB_USER', vaultKey: 'username'],
                                [envVar: 'DB_PASS', vaultKey: 'password']
                            ]
                        ]
                    ]
                    
                    withVault([
                        vaultSecrets: secrets,
                        configuration: [
                            vaultUrl: env.VAULT_ADDR,
                            vaultCredentialId: 'vault-approle'
                        ]
                    ]) {
                        // Flyway 마이그레이션 예제
                        sh """
                            flyway migrate \
                                -url=jdbc:postgresql://${DB_HOST}:5432/${DB_NAME} \
                                -user=${DB_USER} \
                                -password=${DB_PASS} \
                                -locations=filesystem:./migrations
                        """
                    }
                }
            }
        }
    }
}
```

### 예제 3: 다중 Secret 사용

```groovy
// examples/Jenkinsfile-multi-secrets
pipeline {
    agent any
    
    environment {
        VAULT_ADDR = 'http://vault.vault.svc.cluster.local:8200'
    }
    
    stages {
        stage('Deploy Application') {
            steps {
                script {
                    // 여러 Secret을 동시에 가져오기
                    def secrets = [
                        // Database Dynamic Secret
                        [
                            path: 'database/creds/readwrite',
                            secretValues: [
                                [envVar: 'DB_USERNAME', vaultKey: 'username'],
                                [envVar: 'DB_PASSWORD', vaultKey: 'password']
                            ]
                        ],
                        // API Keys (Static Secret)
                        [
                            path: 'secret/data/jenkins/api-keys',
                            engineVersion: 2,
                            secretValues: [
                                [envVar: 'API_KEY', vaultKey: 'api_key'],
                                [envVar: 'API_SECRET', vaultKey: 'api_secret']
                            ]
                        ]
                    ]
                    
                    withVault([
                        vaultSecrets: secrets,
                        configuration: [
                            vaultUrl: env.VAULT_ADDR,
                            vaultCredentialId: 'vault-approle'
                        ]
                    ]) {
                        // 환경 변수를 사용하여 애플리케이션 빌드
                        sh '''
                            echo "Building with database credentials..."
                            echo "Database User: $DB_USERNAME"
                            
                            # Docker 이미지 빌드 (Secret을 빌드 인자로 전달하지 말 것!)
                            docker build -t myapp:latest .
                            
                            # Kubernetes Secret 생성 (DB 자격 증명)
                            kubectl create secret generic app-db-creds \
                                --from-literal=username=$DB_USERNAME \
                                --from-literal=password=$DB_PASSWORD \
                                --dry-run=client -o yaml | kubectl apply -f -
                            
                            # 애플리케이션 배포
                            kubectl apply -f deployment.yaml
                        '''
                    }
                }
            }
        }
    }
}
```

### 예제 4: Manual Vault 통합 (스크립트)

플러그인을 사용하지 않고 직접 Vault API를 호출:

```groovy
// examples/Jenkinsfile-manual
pipeline {
    agent any
    
    environment {
        VAULT_ADDR = 'http://vault.vault.svc.cluster.local:8200'
        ROLE_ID = credentials('vault-role-id')
        SECRET_ID = credentials('vault-secret-id')
    }
    
    stages {
        stage('Get Vault Token') {
            steps {
                script {
                    // AppRole로 로그인
                    def loginResponse = sh(
                        script: """
                            curl -s -X POST ${VAULT_ADDR}/v1/auth/approle/login \
                                -d '{"role_id":"${ROLE_ID}","secret_id":"${SECRET_ID}"}'
                        """,
                        returnStdout: true
                    ).trim()
                    
                    def jsonSlurper = new groovy.json.JsonSlurper()
                    def loginData = jsonSlurper.parseText(loginResponse)
                    env.VAULT_TOKEN = loginData.auth.client_token
                }
            }
        }
        
        stage('Get Database Credentials') {
            steps {
                script {
                    // Dynamic Secret 생성
                    def credsResponse = sh(
                        script: """
                            curl -s -X GET ${VAULT_ADDR}/v1/database/creds/readwrite \
                                -H "X-Vault-Token: ${VAULT_TOKEN}"
                        """,
                        returnStdout: true
                    ).trim()
                    
                    def jsonSlurper = new groovy.json.JsonSlurper()
                    def credsData = jsonSlurper.parseText(credsResponse)
                    
                    env.DB_USERNAME = credsData.data.username
                    env.DB_PASSWORD = credsData.data.password
                    env.LEASE_ID = credsData.lease_id
                    
                    echo "Got database credentials with lease: ${env.LEASE_ID}"
                }
            }
        }
        
        stage('Run Database Tasks') {
            steps {
                sh '''
                    # 데이터베이스 작업
                    echo "Running database tasks..."
                    PGPASSWORD=$DB_PASSWORD psql -h postgres -U $DB_USERNAME -d myappdb -c "SELECT current_user;"
                '''
            }
        }
    }
    
    post {
        always {
            script {
                if (env.LEASE_ID) {
                    // Lease 폐기
                    sh """
                        curl -s -X PUT ${VAULT_ADDR}/v1/sys/leases/revoke \
                            -H "X-Vault-Token: ${VAULT_TOKEN}" \
                            -d '{"lease_id":"${LEASE_ID}"}'
                    """
                    echo "Revoked lease: ${env.LEASE_ID}"
                }
                
                if (env.VAULT_TOKEN) {
                    // Token 폐기
                    sh """
                        curl -s -X POST ${VAULT_ADDR}/v1/auth/token/revoke-self \
                            -H "X-Vault-Token: ${VAULT_TOKEN}"
                    """
                    echo "Revoked Vault token"
                }
            }
        }
    }
}
```

## Best Practices

### 1. Least Privilege

각 프로젝트별로 별도의 AppRole과 정책 생성:

```bash
# Frontend 프로젝트용
vault policy write frontend-policy - <<EOF
path "secret/data/frontend/*" {
  capabilities = ["read"]
}
EOF

vault write auth/approle/role/frontend \
  policies="frontend-policy" \
  token_ttl=30m

# Backend 프로젝트용
vault policy write backend-policy - <<EOF
path "database/creds/readwrite" {
  capabilities = ["read"]
}
path "secret/data/backend/*" {
  capabilities = ["read"]
}
EOF

vault write auth/approle/role/backend \
  policies="backend-policy" \
  token_ttl=1h
```

### 2. Secret ID 순환

Secret ID를 주기적으로 순환:

```bash
# 새 Secret ID 생성
NEW_SECRET_ID=$(vault write -f -field=secret_id auth/approle/role/jenkins/secret-id)

# Jenkins Credential 업데이트
# (수동 또는 Jenkins API 사용)

# 기존 Secret ID 폐기 (선택사항)
vault write auth/approle/role/jenkins/secret-id-accessor/destroy \
  secret_id_accessor=<OLD_ACCESSOR>
```

### 3. Audit Logging

Vault 감사 로그로 Jenkins 활동 추적:

```bash
# 감사 로그 활성화
vault audit enable file file_path=/vault/logs/audit.log

# Jenkins 활동 확인
kubectl exec -n vault vault-0 -- cat /vault/logs/audit.log | \
  jq 'select(.auth.metadata.role_name == "jenkins")'
```

### 4. 환경 변수 보호

Jenkins Pipeline에서 비밀번호를 로그에 출력하지 않도록:

```groovy
withVault([...]) {
    // ❌ 잘못된 예시
    echo "Password is: ${env.DB_PASSWORD}"  // 로그에 기록됨!
    
    // ✅ 올바른 예시
    sh '''
        # Secret을 직접 사용하되 로그에 출력하지 않음
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST ...
    '''
}
```

### 5. Lease 관리

장시간 실행되는 빌드의 경우 Lease 갱신:

```groovy
stage('Long Running Task') {
    steps {
        script {
            def renewLeaseThread = Thread.start {
                while (currentBuild.isBuilding()) {
                    sleep(time: 10, unit: 'MINUTES')
                    // Lease 갱신 로직
                    sh """
                        curl -X PUT ${VAULT_ADDR}/v1/sys/leases/renew \
                            -H "X-Vault-Token: ${VAULT_TOKEN}" \
                            -d '{"lease_id":"${LEASE_ID}","increment":"1800"}'
                    """
                }
            }
            
            try {
                // 장시간 작업
                sh 'make long-running-task'
            } finally {
                renewLeaseThread.interrupt()
            }
        }
    }
}
```

## 트러블슈팅

### AppRole 인증 실패

```bash
# Role 설정 확인
vault read auth/approle/role/jenkins

# Role ID 확인
vault read auth/approle/role/jenkins/role-id

# Secret ID 목록
vault list auth/approle/role/jenkins/secret-id
```

### Dynamic Secret 생성 실패

```bash
# Database 연결 확인
vault read database/config/postgresql

# Role 확인
vault read database/roles/readwrite

# 수동으로 Secret 생성 테스트
vault read database/creds/readwrite
```

### Jenkins에서 Vault 접근 불가

```bash
# Jenkins Pod에서 Vault 접근 테스트
kubectl exec -n jenkins jenkins-0 -- curl -v http://vault.vault.svc.cluster.local:8200/v1/sys/health

# DNS 확인
kubectl exec -n jenkins jenkins-0 -- nslookup vault.vault.svc.cluster.local
```

## 다음 단계

축하합니다! Vault에 대한 모든 문서를 완료했습니다.

### 실습 체크리스트

- [ ] Kind 클러스터에 Vault 배포
- [ ] Vault Secrets Operator 설치
- [ ] Static Secrets 동기화 테스트
- [ ] Dynamic Secrets 생성 및 사용
- [ ] Jenkins에서 Dynamic Secrets 사용

### 추가 학습 자료

- [Vault Production Hardening](https://developer.hashicorp.com/vault/tutorials/operations/production-hardening)
- [Vault High Availability](https://developer.hashicorp.com/vault/docs/concepts/ha)
- [Vault Disaster Recovery](https://developer.hashicorp.com/vault/tutorials/operations/disaster-recovery)

## 참고 자료

- [HashiCorp Vault Jenkins Plugin](https://plugins.jenkins.io/hashicorp-vault-plugin/)
- [Vault AppRole Auth Method](https://developer.hashicorp.com/vault/docs/auth/approle)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
