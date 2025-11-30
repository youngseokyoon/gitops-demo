# Kubernetes 실습 환경 구축 가이드

이 섹션은 GitOps 실습을 위한 Kubernetes 클러스터 환경을 구축하는 방법을 다룹니다.

## 📚 목차

### [01. Kind로 클러스터 구성하기](./01-kind-setup.md) ✨
로컬 환경에서 Kind를 사용하여 Kubernetes 클러스터를 구성하는 완전한 가이드

**주요 내용:**
- Control Plane + 2 Worker 노드 구성
- 포트 매핑 (HTTP/HTTPS, NodePort)
- 영구 볼륨 설정 (HostPath)
- 노드 레이블링을 통한 워크로드 분리
- StorageClass 및 네트워킹 상세 설명
- 7가지 트러블슈팅 시나리오
- 고급 설정 (멀티 클러스터, Private Registry, Feature Gates)

### [02. Multipass로 클러스터 구성하기](./02-multipass-setup.md)
VM 기반 Kubernetes 클러스터를 구성하는 대안적 방법 (선택사항)

**주요 내용:**
- Multipass를 사용한 Ubuntu VM 생성
- K3s 클러스터 구축
- 멀티 노드 환경 설정 및 네트워킹

### [03. Ingress Nginx 설정하기](./03-ingress-nginx.md) ✨
HTTP/HTTPS 트래픽을 라우팅하기 위한 Ingress Controller 설치 및 설정

**주요 내용:**
- Kind 환경을 위한 Ingress Nginx 설치
- 실제 동작 테스트 예제
- TLS Ingress 설정 (ArgoCD, Jenkins)
- Annotations 완전 가이드 (CORS, Basic Auth, Rewrite, Rate Limiting)
- Session affinity 설정 (Jenkins용)
- ConfigMap 커스터마이징 (로깅, SSL, 보안 헤더)
- 상세한 트러블슈팅 가이드

### [04. TLS 인증서 관리](./04-tls-certificates.md) ✨
로컬 개발 환경을 위한 TLS 인증서 생성 및 관리

**주요 내용:**
- 로컬 루트 CA 생성
- 서비스별 도메인 인증서 발급 (SAN 지원)
- Kubernetes TLS Secret 생성
- 와일드카드 인증서 생성
- 인증서 자동 생성 스크립트
- cert-manager 소개
- 인증서 로테이션 절차
- 인증서 포맷 변환 및 상세 검증
- 만료일 자동 확인 스크립트

### [05. Keycloak 인증 시스템](./05-keycloak.md)
SSO(Single Sign-On)를 위한 Keycloak 설치 및 기본 구성

**주요 내용:**
- Keycloak 소개 및 주요 기능
- Kubernetes에 Deploymnet으로 배포
- Ingress 및 Service 설정
- ArgoCD/Jenkins SSO 통합 준비

## 🎯 학습 목표

이 섹션을 통해 다음을 학습할 수 있습니다:

- ✅ 로컬 Kubernetes 클러스터 구축 방법
- ✅ Ingress를 통한 서비스 외부 노출
- ✅ TLS를 사용한 보안 통신 설정
- ✅ 인증 시스템 구축 및 통합

## 💡 권장 학습 경로

1. **Kind 클러스터 구성** → [01-kind-setup.md](./01-kind-setup.md)
2. **Ingress 설정** → [03-ingress-nginx.md](./03-ingress-nginx.md)
3. **TLS 인증서 생성** → [04-tls-certificates.md](./04-tls-certificates.md)
4. **ArgoCD 및 Jenkins 설치** → [ArgoCD](../03-argocd/), [Jenkins](../04-jenkins/)

## 📝 사전 요구사항

### macOS 환경
```bash
# Homebrew 설치 확인
brew --version

# Docker Desktop 설치 확인
docker --version

# Kind 설치
brew install kind

# kubectl 설치
brew install kubectl
```

### 필요한 도구
- **Docker Desktop** - 컨테이너 런타임
- **Kind** - Kubernetes in Docker
- **kubectl** - Kubernetes CLI
- **Helm** (선택) - 패키지 매니저

## 🚀 빠른 시작

최소한의 설정으로 빠르게 시작하려면:

```bash
# 1. Kind 클러스터 생성
kind create cluster --name gitops-demo

# 2. 클러스터 확인
kubectl cluster-info
kubectl get nodes

# 3. Ingress Nginx 설치
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# 4. Ingress Controller 배포 확인
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

```

## 📊 문서 개선 내역

이 섹션의 모든 문서는 실제 Kind 클러스터에서 검증되었으며, 다음과 같은 개선사항이 포함되어 있습니다:

### ✨ 주요 개선사항
- **실습 가능한 예제**: 모든 명령어와 설정이 즉시 실행 가능
- **상세한 설명**: 각 설정 옵션의 의미와 용도 설명
- **트러블슈팅**: 실제 발생할 수 있는 문제와 해결 방법
- **고급 기능**: 프로덕션 환경을 위한 추가 설정
- **검증 절차**: 각 단계별 확인 방법 제공

### 📝 문서별 특징

| 문서 | 주요 추가 내용 |
|------|---------------|
| **01-kind-setup.md** | StorageClass 설명, 멀티 클러스터, Feature Gates, 7가지 트러블슈팅 |
| **03-ingress-nginx.md** | Annotations 가이드, ConfigMap 커스터마이징, Session affinity |
| **04-tls-certificates.md** | 자동화 스크립트, cert-manager, 인증서 로테이션, 포맷 변환 |

## 🔗 다음 단계

Kubernetes 클러스터 구축 후:

1. [ArgoCD 설치](../03-argocd/) - GitOps CD 도구
2. [Jenkins 설치](../04-jenkins/) - CI 파이프라인 도구
3. [Vault 설치](../05-vault/) - 시크릿 관리 도구

## 📖 참고 자료

- [Kind 공식 문서](https://kind.sigs.k8s.io/)
- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [Ingress Nginx](https://kubernetes.github.io/ingress-nginx/)
- [Multipass 문서](https://multipass.run/)
