# TLS 인증서 관리

Kubernetes 클러스터에서 사용할 TLS 인증서를 생성하고 Secret으로 등록하는 방법을 설명합니다.

## 📋 개요

로컬 개발 환경에서 HTTPS를 사용하기 위해:
1. 로컬 루트 CA(Certificate Authority) 생성
2. 서비스별 도메인 인증서 발급
3. Kubernetes TLS Secret으로 등록

## 🎯 목표

- `argocd.cicd.com` - ArgoCD용 TLS 인증서
- `jenkins.cicd.com` - Jenkins용 TLS 인증서
- 필요에 따라 추가 도메인 인증서

## 🔧 1단계: 로컬 루트 CA 생성

### CA 개인키 생성

```bash
openssl genrsa -out cicd-rootCA.key 4096
```

### CA 인증서 생성

```bash
openssl req -x509 -new -nodes -sha512 -days 3650 \
  -key cicd-rootCA.key \
  -out cicd-rootCA.crt \
  -subj "/CN=cicd-rootCA/O=local-cicd"
```

**생성된 파일:**
- `cicd-rootCA.key` - CA 개인키 (절대 공유하지 말 것)
- `cicd-rootCA.crt` - CA 인증서 (시스템에 신뢰할 수 있는 인증서로 추가 가능)

## 📝 2단계: SAN 설정 파일 생성

여러 도메인을 하나의 인증서로 처리하기 위한 SAN(Subject Alternative Name) 설정:

`cicd.ext` 파일 생성:

```bash
cat > cicd.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
subjectAltName = @alt_names

[alt_names]
DNS.1=argocd.cicd.com
DNS.2=jenkins.cicd.com
DNS.3=keycloak.cicd.com
EOF
```

> [!TIP]
> 필요한 도메인을 추가하려면 `DNS.4=newdomain.cicd.com` 형식으로 추가하세요.

## 🔐 3단계: 서비스 도메인 인증서 생성

### ArgoCD 인증서 생성

```bash
# 1. 개인키 생성
openssl genrsa -out argocd.cicd.com.key 2048

# 2. CSR (Certificate Signing Request) 생성
openssl req -new -key argocd.cicd.com.key \
  -out argocd.cicd.com.csr \
  -subj "/CN=argocd.cicd.com/O=local-cicd"

# 3. CA로 서명하여 인증서 생성
openssl x509 -req -in argocd.cicd.com.csr \
  -CA cicd-rootCA.crt \
  -CAkey cicd-rootCA.key \
  -CAcreateserial \
  -out argocd.cicd.com.crt \
  -days 825 \
  -sha256 \
  -extfile cicd.ext
```

**생성된 파일:**
- `argocd.cicd.com.key` - ArgoCD 개인키
- `argocd.cicd.com.csr` - 인증서 서명 요청 (이후 삭제 가능)
- `argocd.cicd.com.crt` - ArgoCD 인증서

### Jenkins 인증서 생성

```bash
# 1. 개인키 생성
openssl genrsa -out jenkins.cicd.com.key 2048

# 2. CSR 생성
openssl req -new -key jenkins.cicd.com.key \
  -out jenkins.cicd.com.csr \
  -subj "/CN=jenkins.cicd.com/O=local-cicd"

# 3. CA로 서명하여 인증서 생성
openssl x509 -req -in jenkins.cicd.com.csr \
  -CA cicd-rootCA.crt \
  -CAkey cicd-rootCA.key \
  -CAcreateserial \
  -out jenkins.cicd.com.crt \
  -days 825 \
  -sha256 \
  -extfile cicd.ext
```

### Keycloak 인증서 생성 (선택사항)

```bash
# 1. 개인키 생성
openssl genrsa -out keycloak.cicd.com.key 2048

# 2. CSR 생성
openssl req -new -key keycloak.cicd.com.key \
  -out keycloak.cicd.com.csr \
  -subj "/CN=keycloak.cicd.com/O=local-cicd"

# 3. CA로 서명하여 인증서 생성
openssl x509 -req -in keycloak.cicd.com.csr \
  -CA cicd-rootCA.crt \
  -CAkey cicd-rootCA.key \
  -CAcreateserial \
  -out keycloak.cicd.com.crt \
  -days 825 \
  -sha256 \
  -extfile cicd.ext
```

## ☸️ 4단계: Kubernetes TLS Secret 생성

### ArgoCD TLS Secret

```bash
# Namespace 생성 (아직 없는 경우)
kubectl create namespace argocd

# TLS Secret 생성
kubectl create secret tls argocd-tls \
  --cert=argocd.cicd.com.crt \
  --key=argocd.cicd.com.key \
  -n argocd

# Secret 확인
kubectl get secret argocd-tls -n argocd
```

**YAML 파일로 생성 (GitOps 방식):**

```bash
kubectl create secret tls argocd-tls \
  --cert=argocd.cicd.com.crt \
  --key=argocd.cicd.com.key \
  -n argocd \
  --dry-run=client -o yaml > argocd-tls-secret.yaml

kubectl apply -f argocd-tls-secret.yaml
```

### Jenkins TLS Secret

```bash
# Namespace 생성
kubectl create namespace cicd-jenkins

# TLS Secret 생성
kubectl create secret tls jenkins-tls \
  --cert=jenkins.cicd.com.crt \
  --key=jenkins.cicd.com.key \
  -n cicd-jenkins

# Secret 확인
kubectl get secret jenkins-tls -n cicd-jenkins
```

### Keycloak TLS Secret (선택사항)

```bash
# Namespace 생성
kubectl create namespace keycloak

# TLS Secret 생성
kubectl create secret tls keycloak-tls \
  --cert=keycloak.cicd.com.crt \
  --key=keycloak.cicd.com.key \
  -n keycloak
```

## 🖥️ 5단계: 로컬 환경 설정

### macOS에 CA 인증서 추가

시스템에서 생성한 CA를 신뢰하도록 설정:

```bash
# Keychain에 CA 인증서 추가
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  cicd-rootCA.crt
```

또는 Keychain Access 앱을 사용:
1. `cicd-rootCA.crt` 파일을 더블클릭
2. Keychain Access 앱이 열리면 "System" Keychain에 추가
3. 인증서를 찾아서 더블클릭
4. "Trust" 섹션에서 "Always Trust" 선택

### /etc/hosts 설정

```bash
sudo vi /etc/hosts
```

다음 라인 추가:
```
127.0.0.1 argocd.cicd.com
127.0.0.1 jenkins.cicd.com
127.0.0.1 keycloak.cicd.com
```

## 🧪 인증서 검증

### 인증서 내용 확인

```bash
# 인증서 정보 출력
openssl x509 -in argocd.cicd.com.crt -text -noout

# 주요 필드 확인
openssl x509 -in argocd.cicd.com.crt -noout -subject -issuer -dates
```

**예상 출력:**
```
subject=CN = argocd.cicd.com, O = local-cicd
issuer=CN = cicd-rootCA, O = local-cicd
notBefore=Nov 30 11:00:00 2025 GMT
notAfter=Mar  6 11:00:00 2027 GMT
```

### 인증서 체인 검증

```bash
# CA로 서명된 인증서인지 확인
openssl verify -CAfile cicd-rootCA.crt argocd.cicd.com.crt
```

**예상 출력:**
```
argocd.cicd.com.crt: OK
```

### HTTPS 연결 테스트

```bash
# ArgoCD 서비스가 실행 중인 경우
curl -v --cacert cicd-rootCA.crt https://argocd.cicd.com

# 또는 시스템 CA를 신뢰하도록 추가했다면
curl -v https://argocd.cicd.com
```

## 📁 파일 정리

생성된 파일들을 정리:

```bash
# 중요 파일 (안전한 곳에 보관)
# - cicd-rootCA.key       (CA 개인키 - 절대 공유 금지)
# - cicd-rootCA.crt       (CA 인증서)
# - *.key                 (서비스별 개인키)
# - *.crt                 (서비스별 인증서)

# 삭제 가능한 파일
rm *.csr                  # CSR 파일들
rm cicd-rootCA.srl        # Serial 파일
```

## 🛠️ 유용한 명령어

### Secret 목록 확인
```bash
kubectl get secrets --all-namespaces | grep tls
```

### Secret 상세 정보
```bash
kubectl describe secret argocd-tls -n argocd
```

### Secret 내용 확인 (Base64 디코딩)
```bash
kubectl get secret argocd-tls -n argocd -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout
```

### Secret 삭제 및 재생성
```bash
kubectl delete secret argocd-tls -n argocd
kubectl create secret tls argocd-tls \
  --cert=argocd.cicd.com.crt \
  --key=argocd.cicd.com.key \
  -n argocd
```

## 🔍 트러블슈팅

### 인증서 만료 경고

```bash
# 인증서 만료일 확인
openssl x509 -in argocd.cicd.com.crt -noout -dates

# 새 인증서 생성 (3단계 반복)
```

### 브라우저 인증서 오류

1. CA 인증서가 시스템에 추가되었는지 확인
2. 브라우저 재시작
3. 인증서 캐시 삭제

### Secret이 인식되지 않을 때

```bash
# Namespace 확인
kubectl get namespaces

# Secret이 올바른 Namespace에 있는지 확인
kubectl get secrets -n argocd

# Secret 형식 확인
kubectl get secret argocd-tls -n argocd -o yaml
```

## 📚 다음 단계

TLS Secret 생성 후:

1. [Ingress에 TLS 설정 추가](./03-ingress-nginx.md#tls를-사용하는-ingress-예제-argocd)
2. [ArgoCD HTTPS 접속 설정](../03-argocd/02-kind-installation.md)
3. [Jenkins HTTPS 접속 설정](../04-jenkins/02-kind-installation.md)

## 🔗 참고 자료

- [OpenSSL 공식 문서](https://www.openssl.org/docs/)
- [Kubernetes TLS Secret](https://kubernetes.io/docs/concepts/configuration/secret/#tls-secrets)
- [X.509 인증서 표준](https://datatracker.ietf.org/doc/html/rfc5280)
