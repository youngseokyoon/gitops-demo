---
layout: post
title: How to configure ingress-nginx to kind kubernetes cluster
date: 2025-11-07 13:46:28 +09:00
tags:
  - kubernetes
  - ingress-nginx
  - kind
categories:
  - kubernetes
---

# Ingress-nginx
- Kubernetes Ingress Controller 중 하나인 Ingress Nginx 가 공식적으로 은퇴 예정
- 유지보수는 2026년 3월, 기존 Ingress Nginx는 동작하겠지만, 추후 보안 취약점 조치안됨.
- Gateway API 또는 다른 Ingress Controller로 마이그레이션 필요함


## kind kubernetes 에 ingress-nginx 설치하기
```bash
curl -fLO https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

### nodeSelector 설정 추가
- kind 클러스터의 control-plane 노드에 ingress-nginx controller 가 배포되도록 설정 추가
```yaml
      nodeSelector:
        app: ingress-controller
```

### ssh pass-through 설정 추가
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
      - args:
        - --enable-ssl-passthrough
```

## 설치 확인
```bash
kubectl get pods -n ingress-nginx
NAME                                        READY   STATUS    RESTARTS   AGE
ingress-nginx-controller-5c9b7d6f7b-zzx
                        1/1     Running   0          2m34s
```


### Ingress 리소스 생성 예시

1. [kind 에서 제공하는 ingress example](https://kind.sigs.k8s.io/examples/ingress/usage.yaml)
2. argocd.cicd.com 구성을 위한 ingress example
```argocd-ingress.yaml
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
      secretName: argocd-tls
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

### secret argocd-tls 생성
[TLS 인증서가 포함된 secret 생성](./kubernetes-configure-secret-apps.md) 참고

CA root 인증서로 서명된 argocd.cicd.com 도메인 인증서로 secret 생성
```bash
# root CA 생성
openssl genrsa -out cicd-rootCA.key 4096

openssl req -x509 -new -nodes -sha512 -days 3650 \
  -key cicd-rootCA.key \
  -out cicd-rootCA.crt \
  -subj "/CN=cicd-rootCA/O=local-cicd"
  
# argocd.cicd.com 도메인 인증서 생성
openssl genrsa -out argocd.cicd.com.key 2048

openssl req -new -key argocd.cicd.com.key -out argocd.cicd.com.csr \
  -subj "/CN=argocd.cicd.com/O=local-cicd"
  
openssl x509 -req -in argocd.cicd.com.csr -CA cicd-rootCA.crt -CAkey cicd-rootCA.key \
  -CAcreateserial -out argocd.cicd.com.crt -days 825 -sha256 -extfile cicd.ext

# secret 생성
kubectl create secret tls argocd-tls \
  --cert=argocd.cicd.com.crt \
  --key=argocd.cicd.com.key \
  -n argocd --dry-run=client -o yaml > argocd.cicd.com.yaml
  
kubectl apply -f argocd.cicd.com.yaml
```

### cicd.ext 내용
```cicd.ext
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
subjectAltName = @alt_names
[alt_names]
DNS.1=argocd.cicd.com
DNS.2=jenkins.cicd.com
```

## 참고 링크
- https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/
- https://kubernetes.github.io/ingress-nginx/
- https://kind.sigs.k8s.io/docs/user/ingress/

 