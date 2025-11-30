---
layout: post
title: How to deploy keycloak
date: 2025-11-08 23:46:28 +09:00
tags:
  - kubernetes
  - keycloak
categories:
  - kubernetes
---

# Keycloak
## Keycloak 소개
- Keycloak 은 오픈소스 아이덴티티 및 액세스 관리 솔루션이다.
- SSO(Single Sign-On), OIDC, OAuth2, SAML 등 다양한 인증
- 사용자 관리, 역할 기반 액세스 제어(RBAC), 소셜 로그인 등 기능 제공

## Keycloak 배포
- Keycloak 을 Kubernetes 클러스터에 배포
- Helm 차트 또는 Operator 사용 가능

## keycloak 배포
### keycloak Deployment
```keycloak.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
  namespace: keycloak
  labels:
    app: keycloak
spec:
  replicas: 1
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
        - name: keycloak
          image: quay.io/keycloak/keycloak:26.4.0
          args:
            - start
            - --hostname=keycloak.cicd.com
            - --http-port=8080
            - --hostname-strict=false
            - --http-enabled=true
            - --proxy-headers=xforwarded # Note: use xforwarded for ingress controllers
            - --verbose
          env:
            - name: KC_BOOTSTRAP_ADMIN_USERNAME
              value: admin
            - name: KC_BOOTSTRAP_ADMIN_PASSWORD
              value: admin
          ports:
            - containerPort: 8080
```

```keycloak-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: keycloak
  namespace: keycloak
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - keycloak.cicd.com
      secretName: keycloak-tls
  rules:
    - host: keycloak.cicd.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: keycloak
                port:
                  number: 8080
```

```keycloak-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: keycloak
  namespace: keycloak
spec:
  selector:
    app: keycloak
  ports:
    - name: http
      port: 8080
      targetPort: 8080
```


---

Helm 차트로 Keycloak 배포
- bitnami 유지보수 문제로 인해 정상적인 배포가 어려워, codecentric 차트를 사용하는 것으로 변경
- 배포 실패, 추후 재검토 필요


```bash
helm repo add codecentric https://codecentric.github.io/helm-charts
helm repo update
kubectl create namespace keycloak

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

kubectl create namespace keycloak

# keycloak admin 비밀번호 생성 
kubectl create secret generic keycloak-admin \
  --from-literal=admin-password='keycloakpassword' \
  -n keycloak
```

helm repo add bitnami https://charts.bitnami.com/bitnami
helm install keycloak-postgresql bitnami/postgresql \
--namespace keycloak \
--set auth.username=keycloak \
--set auth.password=keycloakpassword \
--set auth.database=keycloak \
--set persistence.enabled=true

## 참고 링크
- [keycloak 공식 문서](https://www.keycloak.org/)
- [keycloak codecentric github Helm charts](https://github.com/codecentric/helm-charts/tree/master/charts/keycloak)
  - > This Keycloak chart is for the old Wildfly Keycloak distribution. It is no longer maintained. For current and new installations, be sure to use the Keycloak-X chart, which we maintain and keep up to date.
- [keycloakx codecentric github Helm charts](https://github.com/codecentric/helm-charts/tree/master/charts/keycloakx)
- [quay.io keycloak](https://quay.io/repository/keycloak/keycloak)
- [docker hub bitnami/postgresql](https://hub.docker.com/r/bitnami/postgresql)
