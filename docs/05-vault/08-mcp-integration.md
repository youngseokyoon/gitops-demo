# Vault MCP (Model Context Protocol) 연동

이 문서는 AI Agent가 Model Context Protocol (MCP)을 통해 HashiCorp Vault와 안전하게 상호작용하는 방법을 설명합니다.

## MCP 개요

**Model Context Protocol (MCP)**은 AI 모델이 외부 시스템(데이터베이스, 도구 등)과 표준화된 방식으로 통신할 수 있게 해주는 프로토콜입니다. Vault와 MCP를 연동하면, AI Agent는 Vault의 강력한 보안 기능을 활용하면서 필요한 Secret을 안전하게 조회할 수 있습니다.

### 아키텍처

```mermaid
graph LR
    Agent[AI Agent (Claude etc.)] -- MCP Protocol --> MCPServer[Vault MCP Server]
    MCPServer -- HTTP/TLS --> Vault[HashiCorp Vault]
    Vault -- Audit Log --> Logging[Monitoring]
```

1. **AI Agent**: MCP 클라이언트 역할
2. **MCP Server**: Vault API를 래핑하여 MCP Tool로 노출
3. **Vault**: 실제 Secret 저장소

## MCP 서버 구현 (Python)

Vault MCP 서버는 Python의 `mcp` SDK와 `hvac`(HashiCorp Vault API Client)를 사용하여 구현할 수 있습니다.

### 주요 기능 (Tools)

- `read_secret(path)`: 지정된 경로의 Secret 읽기
- `list_secrets(path)`: 지정된 경로의 Secret 목록 조회

### 사전 요구사항

- Python 3.10+
- `mcp` 패키지
- `hvac` 패키지
- Vault 접근 권한 (Token 또는 AppRole)

## 구현 예제

`examples/mcp-server/` 디렉토리에 포함된 예제를 사용하여 Kind 클러스터에 배포할 수 있습니다.

### 1. MCP 서버 코드 (`server.py`)

ConfigMap을 통해 코드를 주입합니다.

```python
# 상세 코드는 examples/mcp-server/server.py 참조
```

### 2. Kubernetes 배포 (`deployment.yaml`)

MCP 서버를 Pod로 실행하고, AI Agent(예: 로컬의 Claude Desktop 또는 별도 파드)가 접근할 수 있도록 설정합니다. 여기서는 데모를 위해 Stdout/Stdin 방식(로컬 실행) 또는 SSE(Server-Sent Events) 방식을 고려할 수 있지만, 가장 쉬운 **Stdio 방식**(로컬 실행)을 기준으로 설명합니다.

하지만 Kubernetes 내부에서 동작하는 Agent를 가정한다면, SSE 방식의 서버가 적합합니다. 이 예제에서는 Kubernetes 내에 배포된 **SSE 기반 MCP 서버**를 구축합니다.

## 배포 및 테스트

### 1. 설정 및 배포

```bash
# MCP 서버 배포
kubectl apply -f examples/mcp-server/deployment.yaml
```

### 2. 동작 확인

배포된 MCP 서버 로그를 확인하여 정상적으로 시작되었는지 확인합니다.

```bash
kubectl logs -l app=vault-mcp-server
```

## 보안 고려사항

- **최소 권한 원칙**: MCP 서버가 사용하는 Vault Token은 필요한 Secret 경로(`secret/data/myapp/*` 등)에만 접근 권한이 있어야 합니다.
- **Audit Logging**: Vault의 Audit Log를 활성화하여 AI Agent의 접근 기록을 모니터링해야 합니다.
- **Rate Limiting**: AI의 과도한 요청을 방지하기 위해 속도 제한을 설정하는 것이 좋습니다.
