# ArgoCD 학습 가이드

GitOps를 위한 선언적 Kubernetes CD(Continuous Delivery) 도구인 ArgoCD를 학습합니다.

## 📚 목차

### [01. ArgoCD 개요](./01-overview.md)
- ArgoCD란 무엇인가
- GitOps CD의 핵심 개념
- ArgoCD 아키텍처
- 주요 기능 및 장점

### [02. Kind에 ArgoCD 설치하기](./02-kind-installation.md)
- Helm을 사용한 ArgoCD 설치
- HTTP/HTTPS 설정
- 초기 설정 및 비밀번호 변경
- Repository 연동

### [03. K3s에 ArgoCD 설치하기](./03-k3s-installation.md) (선택사항)
- K3s 클러스터에 ArgoCD 설치
- Traefik Ingress 설정
- 멀티 노드 환경 구성

### [04. Keycloak SSO 연동](./04-keycloak-sso.md)
- Keycloak과 ArgoCD 통합
- SSO(Single Sign-On) 설정
- RBAC 권한 관리

## 🎯 학습 목표

이 섹션을 통해 다음을 학습할 수 있습니다:

- ✅ ArgoCD의 기본 개념과 GitOps 원칙
- ✅ Kubernetes 환경에 ArgoCD 설치 및 설정
- ✅ Git Repository와 ArgoCD 연동
- ✅ Application 배포 및 자동 동기화
- ✅ SSO를 통한 인증 및 권한 관리

## 💡 권장 학습 경로

1. **개념 이해** → [01-overview.md](./01-overview.md)
2. **환경 구축** → [02-kind-installation.md](./02-kind-installation.md)
3. **실습**:
   - Git Repository 연결
   - Application 생성 및 배포
   - Auto Sync 확인
4. **고급 기능** → [04-keycloak-sso.md](./04-keycloak-sso.md)

## 📝 사전 요구사항

### 필수
- [Kubernetes 클러스터](../02-kubernetes/01-kind-setup.md) 구성 완료
- kubectl 설치 및 클러스터 접근 가능
- Helm 3.x 이상

### 권장
- [Ingress Nginx](../02-kubernetes/03-ingress-nginx.md) 설치
- [TLS 인증서](../02-kubernetes/04-tls-certificates.md) 생성
- Git Repository (GitHub, GitLab 등)

## 🚀 빠른 시작

ArgoCD를 빠르게 설치하려면:

```bash
# 1. Namespace 생성
kubectl create namespace argocd

# 2. ArgoCD 설치 (공식 매니페스트)
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 3. ArgoCD Server를 NodePort로 노출
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "NodePort"}}'

# 4. 초기 admin 비밀번호 확인
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo

# 5. ArgoCD 접속
# localhost:<nodeport> 또는 포트 포워딩
kubectl port-forward svc/argocd-server -n argocd 8080:443
# https://localhost:8080
```

> [!TIP]
> 프로덕션 환경에서는 Helm을 사용한 설치를 권장합니다.
> 자세한 내용은 [02-kind-installation.md](./02-kind-installation.md)를 참조하세요.

## 📦 주요 구성 요소

### ArgoCD Server
- Web UI 및 API 서버
- Git Repository 관리
- Application 관리

### Application Controller
- Kubernetes 리소스 모니터링
- Git과 클러스터 상태 비교
- 자동 동기화 수행

### Repo Server
- Git Repository에서 매니페스트 가져오기
- Helm, Kustomize 등 처리

### Redis
- 캐싱 및 메시징

### Dex (선택사항)
- SSO 인증 제공자
- OIDC, SAML, LDAP 등 지원

## 🛠️ 주요 기능

### 1. GitOps 기반 배포
- Git을 단일 진실 원천(Source of Truth)으로 사용
- 선언적 설정 관리
- 버전 관리 및 추적

### 2. 자동 동기화
- Git Repository 변경 자동 감지
- 클러스터와 Git 상태 자동 동기화
- Health 상태 모니터링

### 3. 멀티 클러스터 지원
- 여러 Kubernetes 클러스터 관리
- 클러스터별 Application 배포

### 4. Rollback 및 히스토리
- 이전 버전으로 쉽게 롤백
- 배포 히스토리 추적

### 5. RBAC
- 세밀한 권한 관리
- 프로젝트별 접근 제어

## 🔗 다음 단계

ArgoCD 설치 및 설정 후:

1. [Jenkins 설치](../04-jenkins/) - CI 파이프라인 구축
2. [Vault 연동](../05-vault/06-jenkins-integration.md) - 시크릿 관리
3. Application 배포 자동화 구현

## 📖 참고 자료

- [ArgoCD 공식 문서](https://argo-cd.readthedocs.io/)
- [ArgoCD GitHub](https://github.com/argoproj/argo-cd)
- [ArgoCD Helm Chart](https://artifacthub.io/packages/helm/argo/argo-cd)
- [GitOps 원칙](https://www.gitops.tech/)

## 🎓 추천 도서

- [예제로 배우는 Argo CD](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000009264605)
- [GitOps Cookbook](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000010494149)
