# GitOps 학습 가이드

이 repository는 GitOps에 대한 체계적인 학습을 위한 자료를 제공합니다.

## 📚 학습 경로

### 1️⃣ [GitOps Cookbook](./docs/01-gitops-cookbook/)
GitOps의 기본 개념과 원칙을 학습합니다.

**주요 내용:**
- GitOps 소개 및 핵심 원칙
- 필수 요구사항 및 도구
- 컨테이너 기초
- Kustomize와 Helm
- Cloud Native CI/CD

### 2️⃣ [Kubernetes 실습 환경](./docs/02-kubernetes/)
GitOps 실습을 위한 Kubernetes 클러스터를 구성합니다.

**주요 내용:**
- Kind를 사용한 로컬 클러스터 구축
- Multipass를 사용한 VM 기반 클러스터 (선택)
- Ingress Nginx 설정
- TLS 인증서 관리
- Keycloak 인증 시스템

### 3️⃣ [ArgoCD](./docs/03-argocd/)
선언적 GitOps CD 도구인 ArgoCD를 학습합니다.

**주요 내용:**
- ArgoCD 개요 및 아키텍처
- Kind/K3s 환경에 설치
- Repository 연동 및 Application 배포
- Auto Sync 및 Self-Healing
- Keycloak SSO 통합

### 4️⃣ [Jenkins](./docs/04-jenkins/)
CI/CD 파이프라인을 구축합니다.

**주요 내용:**
- Jenkins 개요 및 GitOps에서의 역할
- Kubernetes 환경에 설치
- Kubernetes Plugin을 활용한 동적 Agent
- Pipeline as Code (Jenkinsfile)
- Docker 이미지 빌드 및 배포

### 5️⃣ [HashiCorp Vault](./docs/05-vault/)
시크릿 관리 및 보안을 강화합니다.

**주요 내용:**
- Vault 기본 개념 및 아키텍처
- Kind 클러스터에 배포
- Vault Secrets Operator (VSO)
- Dynamic Secrets
- Jenkins 통합

## 🎯 추천 학습 순서

처음 시작하시는 분들을 위한 추천 학습 경로:

```
1. GitOps 이론 학습
   └─> GitOps Cookbook 읽기
   
2. 실습 환경 구축
   ├─> Kubernetes 클러스터 구성 (Kind)
   ├─> Ingress Nginx 설치
   └─> TLS 인증서 생성

3. CD 도구 학습
   ├─> ArgoCD 설치
   ├─> Repository 연동
   └─> Application 배포 실습

4. CI 도구 학습
   ├─> Jenkins 설치
   ├─> Pipeline 작성
   └─> 이미지 빌드 자동화

5. 보안 강화
   └─> Vault로 시크릿 관리
```

## 💡 GitOps 워크플로우

이 학습 자료를 완료하면 다음과 같은 완전한 GitOps 워크플로우를 구현할 수 있습니다:

```
┌─────────────────────────────────────────────────────────────┐
│                   GitOps Workflow                            │
└─────────────────────────────────────────────────────────────┘

1. Developer
   └─> Git Push (소스 코드)

2. Jenkins (CI) ← 학습 항목
   ├─> 자동 빌드 트리거
   ├─> 테스트 실행
   ├─> Docker 이미지 빌드
   ├─> Container Registry에 푸시
   └─> Manifest Repository 업데이트

3. ArgoCD (CD) ← 학습 항목
   ├─> Manifest 변경 감지
   ├─> Kubernetes와 비교
   └─> 자동 배포

4. Vault (Secrets) ← 학습 항목
   ├─> Dynamic Secrets 생성
   └─> Jenkins/Application에 주입

5. Kubernetes Cluster ← 학습 항목
   └─> Application 실행
```

## 📖 참고 도서

이 학습 자료는 다음 도서들을 참고하여 작성되었습니다:

- [GitOps Cookbook](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000010494149) - GitOps 기본 개념과 실습
- [예제로 배우는 Argo CD](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000009264605) - ArgoCD 심화 학습
- [Getting Started with HashiCorp Vault](https://www.amazon.com/Getting-Started-HashiCorp-Vault-hands-ebook/dp/B0FK39MY5C/) - Vault 기초와 실습
- [Road to Kubernetes](https://www.manning.com/books/road-to-kubernetes) - Kubernetes 기본 개념

## 🛠️ 사전 요구사항

### 시스템 요구사항
- **운영체제**: macOS, Linux, or Windows with WSL2
- **CPU**: 4 cores 이상 권장
- **메모리**: 8GB 이상 권장
- **디스크**: 20GB 이상 여유 공간

### 필수 도구

#### macOS
```bash
# Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Docker Desktop
brew install --cask docker

# Kind
brew install kind

# kubectl
brew install kubectl

# Helm
brew install helm

# Git
brew install git
```

#### Linux (Ubuntu/Debian)
```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## 📁 Repository 구조

```
gitops-demo/
├── docs/                          # 모든 학습 문서
│   ├── 01-gitops-cookbook/        # GitOps 이론
│   ├── 02-kubernetes/             # Kubernetes 실습
│   ├── 03-argocd/                 # ArgoCD 학습
│   ├── 04-jenkins/                # Jenkins 학습
│   ├── 05-vault/                  # Vault 학습
│   └── 99-references/             # 참고 자료
│
├── examples/                      # 실습 예제 (선택)
│   ├── kubernetes/
│   ├── argocd/
│   ├── jenkins/
│   └── vault/
│
└── README.md                      # 이 파일
```

## 💻 이 Repository 사용 방법

### 1. Clone
```bash
git clone <repository-url>
cd gitops-demo
```

### 2. 순차적 학습
각 주제별 디렉토리에는 `README.md`가 있어 전체 목차와 학습 가이드를 제공합니다.
문서는 순서대로 번호가 매겨져 있어 단계적으로 학습할 수 있습니다.

### 3. 실습
- 각 문서의 명령어를 따라 실습
- `examples/` 디렉토리의 예제 파일 활용
- 필요에 따라 설정 커스터마이징

## 🌐 GitHub Pages

이 repository는 GitHub Pages와 연동되어 있습니다.

**웹에서 보기**: `https://<username>.github.io/<repository-name>/`

모든 문서가 웹에서도 보기 좋게 렌더링됩니다.

## 🤝 기여

이 학습 자료에 기여하고 싶으시다면:

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 라이선스

This repository is for educational purposes.

## 🙋 질문 및 피드백

- **Issues**: GitHub Issues를 통해 질문하거나 버그 리포트
- **Discussions**: 학습 관련 토론 및 질문

## 🔗 유용한 링크

### 공식 문서
- [Kubernetes](https://kubernetes.io/docs/)
- [ArgoCD](https://argo-cd.readthedocs.io/)
- [Jenkins](https://www.jenkins.io/doc/)
- [HashiCorp Vault](https://developer.hashicorp.com/vault/docs)
- [Helm](https://helm.sh/docs/)
- [Kustomize](https://kustomize.io/)

### 커뮤니티
- [CNCF](https://www.cncf.io/)
- [Kubernetes Slack](https://slack.k8s.io/)
- [ArgoCD Slack](https://argoproj.github.io/community/join-slack/)

---

**Happy Learning! 🚀**

GitOps를 통해 현대적인 클라우드 네이티브 애플리케이션 배포를 마스터하세요!
