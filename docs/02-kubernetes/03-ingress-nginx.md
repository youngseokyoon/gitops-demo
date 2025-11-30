# Ingress Nginx 설정하기

Kubernetes 클러스터에 Ingress Nginx Controller를 설치하고 설정하는 방법을 설명합니다.

## 📋 개요

Ingress Controller는 클러스터 외부에서 내부 서비스로의 HTTP/HTTPS 라우팅을 제공합니다.

### Ingress와 Ingress Controller

**Ingress 리소스**: Kubernetes 리소스로, 라우팅 규칙을 정의합니다.
**Ingress Controller**: 실제로 Ingress 규칙을 구현하는 컨트롤러 (nginx, traefik, haproxy 등)

### 주요 기능
- ✅ **HTTP/HTTPS 라우팅**: 도메인별, 경로별 라우팅
- ✅ **TLS 종료**: HTTPS 트래픽 처리
- ✅ **가상 호스팅**: 여러 도메인을 하나의 IP로
- ✅ **로드 밸런싱**: 트래픽 분산

> [!WARNING]
> Kubernetes Ingress Nginx는 **2026년 3월에 공식 유지보수가 종료**됩니다.
> 이후에는 보안 패치가 제공되지 않으므로, 프로덕션 환경에서는 대안 중 하나를 고려해야 합니다:
> - **Gateway API** (Kubernetes 공식 차세대 라우팅 API)
> - **Traefik**
> - **Contour**
> - **Istio Ingress Gateway**

## 🔧 설치 방법

### 1. Kind 클러스터용 Ingress Nginx 매니페스트 다운로드

```bash
curl -fLO https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

### 2. 설정 커스터마이징

다운로드한 `deploy.yaml` 파일을 편집하여 다음 설정을 추가합니다.

#### nodeSelector 추가

Control Plane 노드에 Ingress Controller를 배포하도록 설정:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  template:
    spec:
      # 이 부분 추가
      nodeSelector:
        app: ingress-controller
      containers:
      - name: controller
        # ... 기존 설정
```

#### SSL Passthrough 활성화

HTTPS 트래픽을 백엔드로 직접 전달하려면:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  template:
    spec:
      containers:
      - name: controller
        args:
          - /nginx-ingress-controller
          # 이 라인 추가
          - --enable-ssl-passthrough
```

### 3. Ingress Nginx 설치

```bash
kubectl apply -f deploy.yaml
```

### 4. 설치 확인

```bash
# Pod 상태 확인
kubectl get pods -n ingress-nginx

# 출력 예시:
# NAME                                        READY   STATUS      RESTARTS   AGE
# ingress-nginx-admission-create-xxxxx        0/1     Completed   0          2m
# ingress-nginx-admission-patch-xxxxx         0/1     Completed   0          2m
# ingress-nginx-controller-5c9b7d6f7b-xxxxx   1/1     Running     0          2m34s

# 배포 완료 대기
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### 5. Service 확인

Kind 환경에서 Ingress Nginx Service는 NodePort 타입으로 동작합니다:

```bash
kubectl get svc -n ingress-nginx
```

**예상 출력:**
```
NAME                                 TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx-controller             NodePort    10.96.xxx.xxx   <none>        80:xxxxx/TCP,443:xxxxx/TCP   2m
ingress-nginx-controller-admission   ClusterIP   10.96.xxx.xxx   <none>        443/TCP                      2m
```

### 6. 기본 동작 테스트

간단한 테스트 Deployment를 생성하여 Ingress가 작동하는지 확인:

```bash
# 테스트 Deployment 생성
kubectl create deployment hello-world --image=gcr.io/google-samples/hello-app:1.0
kubectl expose deployment hello-world --port=8080

# 테스트 Ingress 생성
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hello-world-ingress
spec:
  ingressClassName: nginx
  rules:
    - host: hello.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: hello-world
                port:
                  number: 8080
EOF

# /etc/hosts 에 추가
sudo sh -c 'echo "127.0.0.1 hello.local" >> /etc/hosts'

# 테스트
curl http://hello.local

# 정리
kubectl delete ingress hello-world-ingress
kubectl delete svc hello-world
kubectl delete deployment hello-world
```

## 🌐 Ingress 리소스 생성

### 기본 Ingress 예제

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  ingressClassName: nginx
  rules:
    - host: myapp.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-service
                port:
                  number: 80
```

### TLS를 사용하는 Ingress 예제 (ArgoCD)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-ingress
  namespace: argocd
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - argocd.cicd.com
      secretName: argocd-tls  # TLS Secret 이름
  rules:
    - host: argocd.cicd.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: argocd-server
                port:
                  number: 80
```

### Jenkins용 Ingress 예제

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jenkins-ingress
  namespace: cicd-jenkins
  annotations:
    kubernetes.io/ingress.class: nginx
    # Jenkins는 세션 유지를 위해 session affinity 필요
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "jenkins-route"
    nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - jenkins.cicd.com
      secretName: jenkins-tls
  rules:
    - host: jenkins.cicd.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: jenkins
                port:
                  number: 8080
```

## 📝 Ingress Annotations 가이드

Ingress Nginx는 다양한 annotations를 통해 동작을 커스터마이징할 수 있습니다:

### 기본 Annotations

```yaml
annotations:
  # IngressClass 지정 (레거시 방식)
  kubernetes.io/ingress.class: nginx
  
  # 리다이렉트 (HTTP → HTTPS)
  nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
  
  # 리라이트 제한
  nginx.ingress.kubernetes.io/limit-rps: "10"
  
  # 업로드 크기 제한
  nginx.ingress.kubernetes.io/proxy-body-size: "100m"
  
  # 타임아웃 설정
  nginx.ingress.kubernetes.io/proxy-connect-timeout: "600"
  nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
```

### CORS 설정

```yaml
annotations:
  nginx.ingress.kubernetes.io/enable-cors: "true"
  nginx.ingress.kubernetes.io/cors-allow-origin: "https://example.com"
  nginx.ingress.kubernetes.io/cors-allow-methods: "GET, PUT, POST, DELETE, PATCH, OPTIONS"
  nginx.ingress.kubernetes.io/cors-allow-headers: "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization"
```

### Basic Auth 설정

```bash
# htpasswd 파일 생성
htpasswd -c auth myuser

# Secret 생성
kubectl create secret generic basic-auth --from-file=auth -n default
```

```yaml
annotations:
  nginx.ingress.kubernetes.io/auth-type: basic
  nginx.ingress.kubernetes.io/auth-secret: basic-auth
  nginx.ingress.kubernetes.io/auth-realm: 'Authentication Required'
```

### Rewrite Rules

```yaml
annotations:
  # URL 재작성
  nginx.ingress.kubernetes.io/rewrite-target: /$2
  # 예: /api/v1/users -> /users
```

**사용 예:**
```yaml
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /api/v1(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: api-service
                port:
                  number: 8080
```

### Whitelist IP

```yaml
annotations:
  nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/8,172.16.0.0/12"
```

## 🔒 TLS Secret 생성

Ingress에서 HTTPS를 사용하려면 TLS Secret이 필요합니다.

자세한 내용은 [TLS 인증서 관리](./04-tls-certificates.md) 문서를 참조하세요.

간단한 예시:

```bash
# Self-signed 인증서 생성 (테스트용)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=myapp.local/O=myapp"

# Secret 생성
kubectl create secret tls myapp-tls \
  --cert=tls.crt \
  --key=tls.key \
  -n default
```

## 🧪 테스트

### 로컬 DNS 설정

`/etc/hosts` 파일에 도메인 추가:

```bash
sudo vi /etc/hosts
```

다음 라인 추가:
```
127.0.0.1 argocd.cicd.com
127.0.0.1 jenkins.cicd.com
127.0.0.1 myapp.local
```

### 접속 테스트

```bash
# HTTP 테스트
curl http://myapp.local

# HTTPS 테스트 (self-signed 인증서)
curl -k https://argocd.cicd.com

# 헤더 확인
curl -I http://myapp.local
```

### 브라우저에서 접속

- ArgoCD: `https://argocd.cicd.com`
- Jenkins: `https://jenkins.cicd.com`

> [!NOTE]
> Self-signed 인증서를 사용하는 경우, 브라우저에서 보안 경고가 표시됩니다.
> "고급" → "계속 진행"을 클릭하여 접속하세요.

## 🛠️ 유용한 명령어

### Ingress 목록 확인
```bash
kubectl get ingress --all-namespaces
```

### 특정 Ingress 상세 정보
```bash
kubectl describe ingress <ingress-name> -n <namespace>
```

### Ingress Controller 로그 확인
```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

### Ingress Nginx ConfigMap 확인
```bash
kubectl get configmap -n ingress-nginx
kubectl describe configmap ingress-nginx-controller -n ingress-nginx
```

```

## ⚙️ ConfigMap 커스터마이징

Ingress Nginx의 전역 설정은 `ingress-nginx-controller` ConfigMap을 통해 변경할 수 있습니다:

```bash
# ConfigMap 편집
kubectl edit configmap ingress-nginx-controller -n ingress-nginx
```

### 주요 설정 옵션

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
data:
  # 로그 레벨 설정
  error-log-level: "info"  # debug, info, notice, warn, error
  
  # 클라이언트 body 크기 제한
  proxy-body-size: "100m"
  
  # 버퍼 크기
  proxy-buffer-size: "16k"
  
  # Keep-alive 타임아웃
  keep-alive: "75"
  
  # Upstream keep-alive 연결 수
  upstream-keepalive-connections: "100"
  
  # SSL 프로토콜
  ssl-protocols: "TLSv1.2 TLSv1.3"
  
  # SSL Ciphers
  ssl-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256"
  
  # HSTS 활성화
  hsts: "true"
  hsts-max-age: "31536000"
  hsts-include-subdomains: "true"
  
  # 사용자 정의 헤더
  add-headers: "ingress-nginx/custom-headers"
  
  # Rate limiting
  limit-req-status-code: "429"
  
  # 로그 포맷
  log-format-upstream: '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"'
```

### Custom Headers 추가

```bash
# Custom headers ConfigMap 생성
kubectl create configmap custom-headers -n ingress-nginx \
  --from-literal=X-Frame-Options=DENY \
  --from-literal=X-Content-Type-Options=nosniff \
  --from-literal=X-XSS-Protection="1; mode=block"
```

### 설정 적용 확인

```bash
# Ingress Controller Pod 재시작 (설정 적용)
kubectl rollout restart deployment ingress-nginx-controller -n ingress-nginx

# 상태 확인
kubectl rollout status deployment ingress-nginx-controller -n ingress-nginx

# 로그 확인
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

## 🔍 트러블슈팅

### Ingress가 작동하지 않을 때

1. **Pod 상태 확인**
```bash
kubectl get pods -n ingress-nginx
```

2. **Service 확인**
```bash
kubectl get svc -n ingress-nginx
```

3. **로그 확인**
```bash
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### 502 Bad Gateway 오류

- 백엔드 Service가 존재하는지 확인
- Pod가 Running 상태인지 확인
- Service의 selector와 Pod의 label이 일치하는지 확인

```bash
kubectl get svc <service-name> -n <namespace>
kubectl get pods -n <namespace> --show-labels
```

### 404 Not Found 오류

- Ingress 규칙의 host와 path가 올바른지 확인
- `/etc/hosts`에 도메인이 등록되어 있는지 확인

```bash
kubectl describe ingress <ingress-name> -n <namespace>
```

## 📚 다음 단계

Ingress Nginx 설치 후:

1. [TLS 인증서 생성 및 등록](./04-tls-certificates.md)
2. [ArgoCD Ingress 설정](../03-argocd/02-kind-installation.md)
3. [Jenkins Ingress 설정](../04-jenkins/02-kind-installation.md)

## 🔗 참고 자료

- [Ingress Nginx 공식 문서](https://kubernetes.github.io/ingress-nginx/)
- [Kind Ingress 가이드](https://kind.sigs.k8s.io/docs/user/ingress/)
- [Kubernetes Ingress 문서](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Ingress Nginx 은퇴 공지](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/)
