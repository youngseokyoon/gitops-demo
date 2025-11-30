# ArgoCD 개요

GitOps를 위한 선언적 Kubernetes CD(Continuous Delivery) 도구인 ArgoCD에 대해 알아봅니다.

## 📖 ArgoCD란?

ArgoCD는 **Kubernetes를 위한 선언적 GitOps CD 도구**입니다. Git Repository를 단일 진실 원천(Single Source of Truth)으로 사용하여 애플리케이션을 Kubernetes 클러스터에 배포하고 관리합니다.

### 핵심 개념

> **GitOps = Git + Operations**
> 
> Git Repository의 선언적 설정을 기반으로 인프라와 애플리케이션을 자동으로 관리하는 운영 방식

## 🎯 주요 특징

### 1. 선언적 배포
- Kubernetes 매니페스트를 Git에서 관리
- Helm, Kustomize, Plain YAML 지원
- 버전 관리 및 이력 추적

### 2. Git을 Single Source of Truth로 사용
- 모든 변경사항은 Git을 통해 발생
- Git 이력이 곧 배포 이력
- 감사(Audit) 및 규정 준수 용이

### 3. 자동 동기화
- Git Repository 모니터링
- 클러스터 상태와 Git 상태 비교
- Drift(불일치) 자동 감지 및 복구

### 4. 멀티 클러스터 / 멀티 테넌트
- 하나의 ArgoCD로 여러 클러스터 관리
- 프로젝트별 권한 분리
- RBAC를 통한 세밀한 접근 제어

## 🏗️ ArgoCD 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                      Git Repository                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐   │
│  │ Helm Chart │  │ Kustomize  │  │  Plain YAML    │   │
│  └────────────┘  └────────────┘  └────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ Poll / Webhook
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    ArgoCD Server                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  API Server / Web UI / gRPC                     │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Application Controller                         │   │
│  │  - Monitor Git Repository                       │   │
│  │  - Compare desired vs actual state              │   │
│  │  - Sync if needed                               │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Repo Server                                    │   │
│  │  - Fetch manifests from Git                     │   │
│  │  - Render templates (Helm/Kustomize)            │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ Apply / Watch
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Kubernetes Cluster(s)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │   Pod    │  │ Service  │  │  Deployment      │     │
│  └──────────┘  └──────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 구성 요소

#### API Server
- RESTful API 및 gRPC 제공
- Web UI 호스팅
- Git Repository, 클러스터, 애플리케이션 관리

#### Application Controller
- Git에서 원하는 상태(Desired State) 가져오기
- Kubernetes에서 실제 상태(Actual State) 확인
- 두 상태 비교 및 동기화 수행
- Health 상태 모니터링

#### Repo Server
- Git Repository에서 매니페스트 가져오기
- Helm Chart 렌더링
- Kustomize 빌드
- 캐싱을 통한 성능 최적화

#### Redis
- 애플리케이션 상태 캐싱
- 메시징 큐

#### Dex (선택사항)
- SSO 통합을 위한 OIDC Provider
- LDAP, SAML, OAuth2 등 지원

## 🔄 GitOps 루프

ArgoCD는 다음과 같은 GitOps 루프를 구현합니다:

```
1. Deploy
   └─> Git Repository의 매니페스트를 읽어 배포

2. Monitor
   └─> Git Repository와 Kubernetes 클러스터 지속 감시

3. Detect Drift
   └─> 선언적 상태(Git)와 실제 상태(Cluster) 불일치 감지

4. Take Action
   └─> 자동 또는 수동으로 동기화하여 복구
```

## ✨ 주요 기능

### Auto-Sync (자동 동기화)
- Git 변경 시 자동으로 클러스터에 반영
- Self-Healing: 수동 변경 감지 및 자동 복구

### Sync Strategies
- **Replace**: 리소스를 교체 (기본값)
- **Apply**: Kubernetes apply 사용
- **Prune**: 더 이상 필요 없는 리소스 자동 삭제

### Health Assessment
- 리소스 상태 자동 평가
- Healthy, Progressing, Degraded, Suspended, Missing, Unknown

### Rollback
- Git 히스토리를 이용한 쉬운 롤백
- 특정 커밋으로 빠르게 복원

### Sync Waves & Hooks
- 리소스 배포 순서 제어
- Pre-sync, Sync, Post-sync Hooks
- 복잡한 배포 시나리오 구현

## 🆚 ArgoCD vs 전통적 CD 도구

| 특징 | 전통적 CD (Push 방식) | ArgoCD (Pull 방식) |
|------|----------------------|-------------------|
| 배포 방식 | CI 도구가 직접 Push | ArgoCD가 Git에서 Pull |
| 클러스터 접근 | CI에서 클러스터 접근 필요 | 클러스터 내부에서 동작 |
| 보안 | 외부에 credential 노출 | Credential 외부 노출 없음 |
| Drift 감지 | 어려움 | 자동 감지 및 복구 |
| 멀티 클러스터 | 복잡 | 쉬움 |
| 상태 가시성 | 제한적 | 실시간 UI 제공 |

## 🔧 사용 사례

### 1. 마이크로서비스 배포
- 여러 서비스를 독립적으로 관리
- 각 서비스별 Git Repository 또는 디렉토리
- 자동 동기화로 빠른 배포

### 2. 멀티 환경 관리
- Dev, Staging, Production 환경
- Kustomize Overlay로 환경별 설정
- 환경별 Git 브랜치 또는 디렉토리

### 3. 인프라 as Code
- Kubernetes 리소스를 코드로 관리
- 변경 사항 추적 및 리뷰
- 일관된 인프라 상태 유지

### 4. Disaster Recovery
- Git에 모든 상태 저장
- 클러스터 장애 시 빠른 복구
- 새 클러스터에 동일한 상태 재현

## 📈 장점

✅ **투명성**: 모든 변경사항이 Git 커밋으로 기록  
✅ **안정성**: Drift 자동 감지 및 복구  
✅ **확장성**: 멀티 클러스터 쉽게 관리  
✅ **보안**: Kubernetes credential을 외부 노출 불필요  
✅ **협업**: Git 워크플로우 활용 (PR, Review)  
✅ **감사**: 배포 이력 완벽 추적  

## ⚠️ 고려사항

- **Git이 필수**: Git Repository가 다운되면 배포 불가
- **학습 곡선**: GitOps 개념 및 ArgoCD 사용법 학습 필요
- **네트워크**: ArgoCD와 Git, Registry 간 네트워크 필요
- **초기 설정**: 기존 시스템에서 마이그레이션 시 초기 작업 필요

## 🚀 다음 단계

ArgoCD 개요를 이해했다면:

1. [Kind에 ArgoCD 설치](./02-kind-installation.md)
2. 첫 번째 Application 배포
3. Auto-Sync 및 Self-Healing 실습
4. [Keycloak SSO 연동](./04-keycloak-sso.md)

## 📖 참고 자료

- [ArgoCD 공식 문서](https://argo-cd.readthedocs.io/)
- [GitOps 원칙](https://www.gitops.tech/)
- [CNCF ArgoCD](https://www.cncf.io/projects/argo/)
- [ArgoCD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
