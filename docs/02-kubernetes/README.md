# Kubernetes 실습 환경 구축 가이드

이 섹션은 GitOps 실습을 위한 Kubernetes 클러스터 환경을 구축하는 방법을 다룹니다.

## 📚 목차

### [01. Kind로 클러스터 구성하기](./01-kind-setup.md)
- Kind를 사용한 로컬 Kubernetes 클러스터 생성
- Control Plane 및 Worker 노드 구성
- 포트 매핑 및 영구 볼륨 설정

### [02. Multipass로 클러스터 구성하기](./02-multipass-setup.md) (선택사항)
- Multipass를 사용한 VM 기반 클러스터 구성
- K3s 클러스터 구축
- 멀티 노드 환경 설정

### [03. Ingress Nginx 설정하기](./03-ingress-nginx.md)
- Ingress Controller 설치
- HTTP/HTTPS 라우팅 설정
- Ingress 리소스 구성

### [04. TLS 인증서 관리](./04-tls-certificates.md)
- 로컬 루트 CA 생성
- 서비스별 도메인 인증서 발급
- Kubernetes Secret으로 TLS 인증서 등록

### [05. Keycloak 인증 시스템](./05-keycloak.md)
- Keycloak 설치 및 구성
- SSO(Single Sign-On) 설정
- ArgoCD/Jenkins와 통합

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
