# Vault HA & MCP 작업 트러블슈팅 로그

이 문서는 Vault HA 구성 및 MCP 연동 작업을 진행하면서 발생한 주요 이슈와 해결 과정을 기록합니다.

## 1. Vault HA 배포 시 Pod Scheduling 실패

### 🔴 증상
Kind 클러스터에 HA 모드(replicas: 3)로 배포 시 `vault-1`, `vault-2` 파드가 `Pending` 상태에서 멈춤.

```bash
$ kubectl describe pod vault-1
Warning  FailedScheduling  ...  0/2 nodes are available: 1 node(s) didn't match pod anti-affinity rules
```

### 🟡 원인
Vault Helm Chart의 기본 설정에는 **Pod Anti-Affinity**가 포함되어 있어, 파드들이 서로 다른 노드에 배포되도록 강제함. Kind는 단일 노드(Single Node)로 동작하므로 하나의 노드에 여러 Vault 파드를 띄울 수 없어 스케줄링 실패.

### 🟢 해결
Helm Values 파일(`vault-ha-values.yaml`)에서 Affinity 설정을 비활성화(초기화)함.

**수정된 코드 (`examples/vault-ha-values.yaml`):**
```yaml
server:
  # ... 기존 설정 ...
  
  # Affinity 설정 완화 (Kind 등 단일 노드 환경 지원)
  affinity: ""
```

---

## 2. Helm Upgrade 시 Webhook 충돌

### 🔴 증상
설정 변경 후 `helm upgrade` 실행 시 에러 발생.

```
Error: UPGRADE FAILED: conflict occurred while applying object ... Kind=MutatingWebhookConfiguration ... conflict with "vault-k8s"
```

### 🟡 원인
Helm 차트 업그레이드 과정에서 기존에 등록된 `MutatingWebhookConfiguration` 리소스와 충돌 발생 (Helm의 알려진 이슈 중 하나).

### 🟢 해결
기존 설치를 완전히 제거하고 재설치 진행.

**실행 명령어:**
```bash
# 1. 기존 설치 제거
helm uninstall vault -n vault

# 2. PVC 제거 (데이터 초기화)
kubectl delete pvc -l app.kubernetes.io/name=vault -n vault

# 3. 재설치
helm install vault hashicorp/vault --namespace vault --values examples/vault-ha-values.yaml
```

---

## 3. MCP 서버 Pod 생성 실패 (ServiceAccount 누락)

### 🔴 증상
`vault-mcp-server` Deployment 배포 후 Pod가 생성되지 않음. ReplicaSet 상태 확인 시 `FailedCreate` 에러 발생.

```
Error creating: pods ... is forbidden: error looking up service account default/myapp-sa: serviceaccount "myapp-sa" not found
```

### 🟡 원인
HA 테스트를 위해 Vault Environments를 재구성하면서, 이전 단계에서 생성했던 `default` 네임스페이스의 `myapp-sa` ServiceAccount가 누락됨 (또는 이전 테스트 과정에서 정리됨).

### 🟢 해결
ServiceAccount 재생성 및 Vault 권한 설정 복구.

**실행 명령어:**
```bash
# ServiceAccount 생성
kubectl create sa myapp-sa -n default
```

이후 `setup-vault.sh` 스크립트를 통해 Vault의 Auth, Policy, Role 설정을 다시 적용함.

---

## 4. Vault 설정 스크립트 실행 오류 (Invalid Token)

### 🔴 증상
Vault 설정을 복구하기 위해 스크립트 실행 시 `permission denied` 및 `invalid token` 에러 다수 발생.

### 🟡 원인
1. 스크립트 실행 시 `VAULT_TOKEN` 환경 변수가 `kubectl exec` 세션 내부로 제대로 전달되지 않음.
2. 초기화 시 사용했던 토큰 값이 스크립트에 잘못 기입됨 (이전 테스트 토큰 사용 등).

### 🟢 해결
1. 유효한 Root Token 확인 (`ha-keys.json`).
2. `kubectl exec` 내부에서 `vault login` 명령어를 명시적으로 실행하도록 스크립트 수정.

**수정된 코드 (`setup-vault.sh`):**
```bash
# 수정 전 (Token 전달 실패 가능성)
export VAULT_TOKEN=...
kubectl exec ... -- sh -c "export VAULT_TOKEN=$VAULT_TOKEN; vault auth enable..."

# 수정 후 (명시적 로그인)
kubectl exec ... -- sh -c "
vault login $VAULT_TOKEN
vault auth enable...
"
```

---

## 5. GitHub Push 차단 (Secret Protection)

### 🔴 증상
`git push` 실행 시 GitHub의 Push Protection 기능에 의해 차단됨.

```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - GITHUB PUSH PROTECTION
remote:   —— HashiCorp Vault Root Service Token ————————————————
remote:     path: docs/05-vault/ha-keys.json
remote:     path: setup-vault.sh
```

### 🟡 원인
실습 과정에서 생성된 실제 Vault Root Token과 Unseal Key가 포함된 파일(`*-keys.json`)과 스크립트(`setup-vault.sh`)가 커밋에 포함됨.

### 🟢 해결
커밋을 취소하고(Reset), 민감한 파일을 삭제한 후, 스크립트를 수정하여 재커밋.

**조치 내용:**
1. **커밋 취소**: `git reset --soft HEAD~1`
2. **파일 삭제**: `rm docs/05-vault/*-keys.json`
3. **스크립트 수정**: `setup-vault.sh`에서 하드코딩된 토큰 제거 및 환경변수 사용으로 변경.
4. **Git 무시 설정**: `.gitignore`에 `*keys.json` 추가.
5. **재커밋 및 푸시**: `git push origin main` 성공.
