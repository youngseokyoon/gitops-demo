## 1.1 GitOps란 무엇인가
GitOps는 **Git을 단일 진실 원본(Single Source of Truth)** 으로 사용하는 인프라 및 애플리케이션 운영 방식이다.  
DevOps 철학을 기반으로 하며, **모든 것을 코드로 관리(Everything as Code)** 한다.

**주요 원칙**
1. **선언적(Declarative)** — 원하는 시스템 상태를 코드로 정의
2. **버전 관리 및 불변성(Versioned & Immutable)** — Git 이력으로 모든 변경 추적
3. **자동 Pull(Pulled Automatically)** — 에이전트가 Git에서 상태를 자동 반영
4. **지속적 동기화(Continuously Reconciled)** — 실제 상태와 선언적 상태를 지속 비교 및 조정

---

## 1.2 왜 GitOps인가
기존의 **Git 중심 개발 워크플로우**를 배포 및 인프라 관리로 확장한다.  
모든 변경 사항은 Git에 기록되어 **추적, 검토, 롤백**이 가능하다.

**주요 장점**
- **표준화된 워크플로우**: 개발자가 익숙한 Git 기반 프로세스 사용
- **보안 강화**: 변경 검토 및 Drift(비의도적 변경) 감지
- **가시성 확보**: Git 이력을 통해 모든 변경 추적
- **멀티클러스터 일관성**: 여러 환경 및 클러스터의 동기화 유지

---

## 1.3 Kubernetes와 CI/CD
GitOps는 CI/CD 파이프라인의 **CD(Continuous Delivery)** 영역을 자동화한다.  
CI 단계에서 애플리케이션 이미지를 빌드하여 레지스트리에 저장하고, 
CD 단계에서 Git 변경을 감지하여 쿠버네티스에 자동 배포한다.

결과적으로 **버전 관리된 선언적 배포**를 구현할 수 있다.

---

## 1.4 Kubernetes에서의 GitOps 배포
GitOps는 **in-cluster** 또는 **external** 방식으로 구현할 수 있다.

**GitOps 루프(GitOps Loop)** 의 4단계:
1. **Deploy** — Git에서 매니페스트를 읽어 배포
2. **Monitor** — Git 및 클러스터 상태를 지속 감시
3. **Detect Drift** — 선언적 상태와 실제 상태의 불일치 감지
4. **Take Action** — Git을 기준으로 자동 복구 또는 동기화 수행

일반적으로 두 개의 Git 저장소를 사용한다.
- **App Repository**: 애플리케이션 소스 코드
- **Manifest Repository**: Kubernetes 매니페스트 및 설정

---

## 1.5 DevOps와 Agility
GitOps는 DevOps의 확장 개념으로, **개발자가 Git을 통해 운영을 자동화**한다.  
목표는 **리드타임(요구사항 → 배포)** 단축이며, 빠른 피드백 루프를 형성한다.

조직은 모든 운영 절차를 Git 기반으로 전환해야 하며,  
이는 단순한 기술 변화가 아니라 **문화적 변화(Cultural Shift)** 를 의미한다.

---

## ✅ 핵심 요약
GitOps는 **Git 중심의 자동화된 운영 방식**이다.  
Kubernetes 환경에서 **CI/CD, IaC, 선언적 관리**를 결합해  
안정성과 일관성을 높이고 운영 효율성을 극대화한다.  
결국 GitOps는 기술뿐 아니라 **조직 문화의 진화**를 요구하는 접근 방식이다.
