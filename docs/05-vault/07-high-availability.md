# Vault 고가용성 (HA) 구성

이 문서는 Kubernetes 환경에서 Raft Integrated Storage를 사용하여 Vault를 고가용성(HA) 모드로 구성하는 방법을 설명합니다.

## HA 아키텍처 (Raft)

Vault는 데이터 저장을 위해 여러 백엔드를 지원하지만, 최신 배포에서는 별도의 외부 스토리지(Consul, Etcd 등) 없이 Vault 자체에 내장된 **Raft Integrated Storage**를 사용하는 것이 권장됩니다.

### 주요 특징
- **단일 바이너리**: 외부 스토리지 의존성 제거
- **운영 단순화**: Vault 클러스터만 관리하면 됨
- **성능**: 네트워크 홉 감소로 인한 성능 향상

```mermaid
graph TD
    subgraph "Kubernetes Cluster"
        subgraph "Vault StatefulSet"
            Vault0[Vault-0 (Leader)]
            Vault1[Vault-1 (Follower)]
            Vault2[Vault-2 (Follower)]
            
            Vault0 <-->|Raft Protocol| Vault1
            Vault0 <-->|Raft Protocol| Vault2
            Vault1 <-->|Raft Protocol| Vault2
        end
        
        LoadBalancer[Service / Ingress] --> Vault0
        LoadBalancer -.-> Vault1
        LoadBalancer -.-> Vault2
    end
```

## 설치 및 구성

### 1. Helm Values 파일 작성

HA 구성을 위해 `examples/vault-ha-values.yaml` 파일을 사용합니다. Standalone 모드와 달리 `server.ha` 섹션이 활성화됩니다.

```yaml
# examples/vault-ha-values.yaml 확인
server:
  ha:
    enabled: true
    replicas: 3
    raft:
      enabled: true
      setNodeId: true
      config: |
        ui = true

        listener "tcp" {
          tls_disable = 1
          address = "[::]:8200"
          cluster_address = "[::]:8201"
        }

        storage "raft" {
          path = "/vault/data"
        }

        service_registration "kubernetes" {}
```

### 2. 기존 Vault 삭제 (필요한 경우)

이미 Standalone으로 설치된 Vault가 있다면 삭제해야 합니다. (데이터는 PVC에 남지만, HA 구성으로 변경하므로 완전히 초기화하는 것이 깔끔합니다)

```bash
helm uninstall vault -n vault
kubectl delete pvc -l app.kubernetes.io/name=vault -n vault
```

### 3. Vault HA 설치

```bash
helm install vault hashicorp/vault \
  --namespace vault \
  --create-namespace \
  --values examples/vault-ha-values.yaml
```

### 4. 초기화 및 Unseal (Raft Join)

HA 모드에서는 첫 번째 노드를 초기화하고, 나머지 노드들은 클러스터에 Join 합니다. (Helm Chart는 자동으로 Join 처리를 도와줍니다)

1. **Vault-0 초기화**
   ```bash
   kubectl exec -ti vault-0 -n vault -- vault operator init
   # Unseal Key 5개와 Root Token 저장
   ```

2. **Unseal (모든 노드)**
   모든 노드(`vault-0`, `vault-1`, `vault-2`)는 Sealed 상태로 시작합니다. 3개 노드 모두 Unseal 해야 합니다.

   ```bash
   # vault-0 unseal
   kubectl exec -ti vault-0 -n vault -- vault operator unseal <Unseal-Key-1>
   kubectl exec -ti vault-0 -n vault -- vault operator unseal <Unseal-Key-2>
   kubectl exec -ti vault-0 -n vault -- vault operator unseal <Unseal-Key-3>
   
   # vault-1 unseal
   kubectl exec -ti vault-1 -n vault -- vault operator unseal <Unseal-Key-1>
   ...
   
   # vault-2 unseal
   kubectl exec -ti vault-2 -n vault -- vault operator unseal <Unseal-Key-1>
   ...
   ```

### 5. HA 상태 확인

```bash
# 리더 및 팔로워 상태 확인
kubectl exec -ti vault-0 -n vault -- vault operator raft list-peers
```

**출력 예시:**
```
Node       Address                        State       Voter
----       -------                        -----       -----
vault-0    vault-0.vault-internal:8201    leader      true
vault-1    vault-1.vault-internal:8201    follower    true
vault-2    vault-2.vault-internal:8201    follower    true
```

## 운영 고려사항

### 리더 선출 (Leader Election)
- 리더 노드(`vault-0` 등)가 다운되면, 나머지 노드들이 투표를 통해 새로운 리더를 선출합니다.
- 잠시 동안의 **Down Time**이 발생할 수 있지만, 자동으로 복구됩니다.
- 클라이언트는 Service를 통해 접근하므로, 리더 변경을 인지하지 못해도 되지만 재시도 로직이 필요할 수 있습니다.

### 백업 및 복구
Raft 스냅샷을 통해 데이터를 백업할 수 있습니다.

```bash
# 스냅샷 생성
kubectl exec -ti vault-0 -n vault -- vault operator raft snapshot save /tmp/backup.snap

# 로컬로 가져오기
kubectl cp vault/vault-0:/tmp/backup.snap ./backup.snap
```

## 트러블슈팅

**Q: 노드가 클러스터에 Join 하지 못합니다.**
A: `vault-internal` 서비스 통신에 문제가 없는지 확인하고, `vault operator raft list-peers` 명령어로 현재 멤버를 확인하세요. 필요시 `vault operator raft join` 명령어로 수동 조인할 수 있습니다.
