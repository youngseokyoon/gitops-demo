# Kubernetes TLS, Secret 생성하기

## 개요
- 로컬 루트 CA를 생성.
- `argocd.cicd.com`, `jenkins.cicd.com`, `keycloak.cicd.com` 도메인용 인증서를 생성.
- kubernetes에 secret으로 등록.
- Docker registry 인증을 위한 secret 생성.

## 순서
1. 로컬 루트 CA 생성
2. 서비스 도메인 인증서 생성
3. Kubernetes TLS secret 생성

---

## 루트 CA 생성 (로컬)
> cicd-rootCA

```
openssl genrsa -out cicd-rootCA.key 4096

openssl req -x509 -new -nodes -sha512 -days 3650 \
  -key cicd-rootCA.key \
  -out cicd-rootCA.crt \
  -subj "/CN=cicd-rootCA/O=local-cicd"
```

## 서비스 도메인 인증서 생성
> argocd.cicd.com

### SAN (Subject Alternative Name) 설정 파일 생성
[cicd.ext](./cicd.ext)

```cicd.ext
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
subjectAltName = @alt_names
[alt_names]
DNS.1=argocd.cicd.com
DNS.2=jenkins.cicd.com
```

### argocd.cicd.com 도메인 인증서 생성
- argocd.cicd.com.key
- argocd.cicd.com.csr
- argocd.cicd.com.crt

```bash
openssl genrsa -out argocd.cicd.com.key 2048

openssl req -new -key argocd.cicd.com.key -out argocd.cicd.com.csr \
  -subj "/CN=argocd.cicd.com/O=local-cicd"
  
openssl x509 -req -in argocd.cicd.com.csr -CA cicd-rootCA.crt -CAkey cicd-rootCA.key \
  -CAcreateserial -out argocd.cicd.com.crt -days 825 -sha256 -extfile cicd.ext
```

### jenkins.cicd.com 도메인 인증서 생성
- jenkins.cicd.com.key
- jenkins.cicd.com.csr
- jenkins.cicd.com.crt

```bash
openssl genrsa -out jenkins.cicd.com.key 2048

openssl req -new -key jenkins.cicd.com.key -out jenkins.cicd.com.csr \
  -subj "/CN=jenkins.cicd.com/O=local-cicd"
  
openssl x509 -req -in jenkins.cicd.com.csr -CA cicd-rootCA.crt -CAkey cicd-rootCA.key \
  -CAcreateserial -out jenkins.cicd.com.crt -days 825 -sha256 -extfile cicd.ext
```

### keycloak.cicd.com 도메인 인증서 생성
- keycloak.cicd.com.key
- keycloak.cicd.com.csr
- keycloak.cicd.com.crt

```bash
openssl genrsa -out keycloak.cicd.com.key 2048

openssl req -new -key keycloak.cicd.com.key -out keycloak.cicd.com.csr \
  -subj "/CN=keycloak.cicd.com/O=local-cicd"

openssl x509 -req -in keycloak.cicd.com.csr -CA cicd-rootCA.crt -CAkey cicd-rootCA.key \
    -CAcreateserial -out keycloak.cicd.com.crt -days 825 -sha256 -extfile cicd.ext
```

## Kubernetes TLS secret 생성
### argocd.cicd.com 도메인 인증서 등록
- namespace: argocd
- argocd-tls

```bash
kubectl create secret tls argocd-tls \
  --cert=argocd.cicd.com.crt \
  --key=argocd.cicd.com.key \
  -n argocd --dry-run=client -o yaml > argocd.cicd.com.yaml
```

### jenkins.cicd.com 도메인 인증서 등록
- namespace: cicd-jenkins
- jenkins-tls

```bash
kubectl create secret tls jenkins-tls \
    --cert=jenkins.cicd.com.crt \
    --key=jenkins.cicd.com.key \
    -n cicd-jenkins --dry-run=client -o yaml > jenkins.cicd.com.yaml
```

### keycloak.cicd.com 도메인 인증서 등록
- namespace: keycloak
- keycloak-tls

```bash
kubectl create secret tls keycloak-tls \
    --cert=keycloak.cicd.com.crt \
    --key=keycloak.cicd.com.key \
    -n keycloak --dry-run=client -o yaml > keycloak.cicd.com.yaml
```
