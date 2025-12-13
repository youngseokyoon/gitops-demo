# HashiCorp Vault 문서

이 디렉토리에는 HashiCorp Vault에 대한 포괄적인 가이드와 실습 자료가 포함되어 있습니다.

## 📚 목차

1. [Vault 개요](./01-vault-overview.md)
   - HashiCorp Vault란 무엇인가?
   - 핵심 기능 및 아키텍처
   - Use Cases

2. [사전 지식](./02-prerequisites.md)
   - Vault 사용을 위한 필수 개념
   - 암호화 및 보안 기본
   - Kubernetes 기본 개념

3. [Kind 클러스터에서 Vault 배포](./03-kind-deployment.md)
   - macOS 환경 설정
   - Helm을 사용한 Vault 설치
   - 초기화 및 unsealing
   - Kubernetes 인증 설정

4. [Vault Secrets Operator (VSO)](./04-vault-secrets-operator.md)
   - VSO란 무엇인가?
   - 아키텍처 및 동작 원리
   - 설치 및 구성
   - 실습 예제

5. [Dynamic Secrets](./05-dynamic-secrets.md)
   - Dynamic Secrets 개념
   - Static vs Dynamic Secrets
   - 지원되는 시크릿 엔진
   - 실습 예제

6. [Jenkins를 활용한 Dynamic Secrets](./06-jenkins-integration.md)
   - Jenkins 통합 방법
   - Pipeline 예제
   - Best Practices

7. [High Availability (HA)](./07-high-availability.md)
   - Raft Storage 구성
   - Leader Election 및 Failover
   - 백업 및 복구

8. [MCP Integration](./08-mcp-integration.md)
   - Model Context Protocol 개요
   - Vault MCP Server 구현 (Python)
   - Kubernetes 배포 및 활용

## 🛠️ 실습 환경

이 문서의 모든 실습은 다음 환경을 기준으로 작성되었습니다:

- **운영체제**: macOS
- **Kubernetes**: Kind (Kubernetes in Docker)
- **패키지 관리자**: Homebrew
- **Helm**: v3.x 이상

## 📁 예제 파일

[examples](./examples/) 디렉토리에는 실습에 필요한 모든 YAML 파일과 스크립트가 포함되어 있습니다.
- `ha-values.yaml`: HA 구성용 Helm Values
- `mcp-server/`: Vault MCP 서버 예제 코드 및 배포 설정

## 📝 변경 이력

- **[CHANGELOG.md](./CHANGELOG.md)**: 작업 중 발생한 이슈 및 해결 과정 기록

## 🚀 시작하기

1. [Vault 개요](./01-vault-overview.md) 문서를 읽고 Vault에 대한 기본 이해를 습득하세요.
2. [사전 지식](./02-prerequisites.md) 문서로 필요한 배경 지식을 확인하세요.
3. [Kind 클러스터에서 Vault 배포](./03-kind-deployment.md) 가이드를 따라 실습 환경을 구축하세요.
4. 이후 문서들을 순서대로 진행하며 Vault의 다양한 기능을 학습하세요.

## 📖 참고 자료

- [HashiCorp Vault 공식 문서](https://developer.hashicorp.com/vault/docs)
- [Vault Secrets Operator](https://developer.hashicorp.com/vault/docs/platform/k8s/vso)
- [Vault on Kubernetes](https://developer.hashicorp.com/vault/tutorials/kubernetes)
