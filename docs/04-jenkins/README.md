# Jenkins 학습 가이드

CI/CD 파이프라인 도구인 Jenkins를 Kubernetes 환경에서 학습합니다.

## 📚 목차

### [01. Jenkins 개요](./01-overview.md)
- Jenkins란 무엇인가
- GitOps에서 Jenkins의 역할
- CI/CD 파이프라인 개념
- Kubernetes와의 통합

### [02. Kind에 Jenkins 설치하기](./02-kind-installation.md)
- Helm을 사용한 Jenkins 설치
- 영구 스토리지 구성
- Ingress 설정
- 초기 설정 및 플러그인

### [03. Kubernetes Pipeline 구성](./03-kubernetes-pipeline.md)
- Kubernetes Plugin을 사용한 동적 Agent
- Pipeline as Code (Jenkinsfile)
- Docker 이미지 빌드 및 푸시
- 실습 예제

## 🎯 학습 목표

이 섹션을 통해 다음을 학습할 수 있습니다:

- ✅ Jenkins의 기본 개념과 CI/CD 원칙
- ✅ Kubernetes 환경에 Jenkins 설치 및 설정
- ✅ Kubernetes Plugin을 활용한 동적 빌드 환경
- ✅ Pipeline을 통한 자동화된 빌드/테스트/배포
- ✅ GitOps 워크플로우와의 통합

## 💡 권장 학습 경로

1. **개념 이해** → [01-overview.md](./01-overview.md)
2. **환경 구축** → [02-kind-installation.md](./02-kind-installation.md)
3. **Pipeline 실습** → [03-kubernetes-pipeline.md](./03-kubernetes-pipeline.md)
4. **GitOps 통합**:
   - Jenkins로 빌드 및 이미지 푸시
   - ArgoCD로 배포 자동화

## 📝 사전 요구사항

### 필수
- [Kubernetes 클러스터](../02-kubernetes/01-kind-setup.md) 구성 완료
- kubectl 설치 및 클러스터 접근 가능
- Helm 3.x 이상

### 권장
- [Ingress Nginx](../02-kubernetes/03-ingress-nginx.md) 설치
- [TLS 인증서](../02-kubernetes/04-tls-certificates.md) 생성
- Docker Hub 또는 Container Registry 계정

## 🚀 빠른 시작

Jenkins를 빠르게 설치하려면:

```bash
# 1. Helm Repository 추가
helm repo add jenkins https://charts.jenkins.io
helm repo update

# 2. Namespace 생성
kubectl create namespace cicd-jenkins

# 3. Jenkins 설치 (기본 설정)
helm install jenkins jenkins/jenkins -n cicd-jenkins

# 4. Admin 비밀번호 확인
kubectl exec --namespace cicd-jenkins -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/additional/chart-admin-password && echo

# 5. Jenkins 접속
kubectl port-forward svc/jenkins -n cicd-jenkins 8080:8080
# http://localhost:8080
```

> [!TIP]
> 프로덕션 환경에서는 영구 볼륨과 Ingress를 사용한 설치를 권장합니다.
> 자세한 내용은 [02-kind-installation.md](./02-kind-installation.md)를 참조하세요.

## 📦 주요 구성 요소

### Jenkins Controller
- Web UI 제공
- Job 관리 및 스케줄링
- Plugin 관리
- 시스템 설정

### Jenkins Agent
- 실제 빌드 작업 수행
- Kubernetes Pod로 동적 생성
- 작업 완료 후 자동 삭제

### Persistent Volume
- Jenkins 홈 디렉토리 저장
- Job 설정 및 히스토리 보존

## 🛠️ 주요 기능

### 1. Kubernetes Plugin
- 동적 Agent 생성
- 리소스 효율적 활용
- 격리된 빌드 환경

### 2. Pipeline as Code
- Jenkinsfile을 Git에서 관리
- 버전 관리 및 리뷰 가능
- 재사용 가능한 스크립트

### 3. 다양한 통합
- Git (GitHub, GitLab, Gitea 등)
- Container Registry (Docker Hub, GHCR 등)
- Kubernetes
- Vault (시크릿 관리)
- Slack, Email (알림)

### 4. Declarative Pipeline
- 읽기 쉬운 구문
- 표준화된 구조
- 강력한 플러그인 생태계

## 💡 GitOps 워크플로우

Jenkins는 GitOps 워크플로우에서 **CI(Continuous Integration)** 역할을 담당합니다:

```
1. Developer → Git Push (코드 변경)
2. Jenkins → 자동 빌드 트리거
3. Jenkins → 테스트 실행
4. Jenkins → Docker 이미지 빌드
5. Jenkins → Container Registry에 푸시
6. Jenkins → Manifest Repository 업데이트 (이미지 태그)
7. ArgoCD → Manifest 변경 감지
8. ArgoCD → Kubernetes에 자동 배포
```

## 🔗 다음 단계

Jenkins 설치 및 설정 후:

1. [ArgoCD와 통합](../03-argocd/) - GitOps CD 구현
2. [Vault 연동](../05-vault/06-jenkins-integration.md) - 안전한 시크릿 관리
3. 실제 애플리케이션 CI/CD 파이프라인 구축

## 📖 참고 자료

- [Jenkins 공식 문서](https://www.jenkins.io/doc/)
- [Jenkins Kubernetes Plugin](https://plugins.jenkins.io/kubernetes/)
- [Jenkins Helm Chart](https://artifacthub.io/packages/helm/jenkinsci/jenkins)
- [Pipeline 문법](https://www.jenkins.io/doc/book/pipeline/syntax/)

## 🎓 추천 도서

- [GitOps Cookbook](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000010494149)
- Jenkins 공식 핸드북
