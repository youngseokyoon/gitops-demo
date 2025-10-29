macOS 에서 kind 를 사용하여 로컬 Kubernetes 클러스터를 생성하는 방법은 다음과 같다.

# 클러스터 생성하기
- [kind-cluster.yaml](../assets/kind-cluster.yaml)

* control-plane 1개와 worker 노드 2개로 구성된 클러스터
* 30000~30005 포트를 호스트와 매핑
* Jenkins 와 Argo CD 를 위한 Persistent Volume 마운트

## kind-cluster.yaml 내용
```kind-cluster.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: myk8s
networking:
  apiServerAddress: "0.0.0.0"
nodes:
  - role: control-plane
    image: kindest/node:v1.32.8
    extraPortMappings:
      - containerPort: 30000
        hostPort: 30000
      - containerPort: 30001
        hostPort: 30001
      - containerPort: 30002
        hostPort: 30002
      - containerPort: 30003
        hostPort: 30003
      - containerPort: 30004
        hostPort: 30004
      - containerPort: 30005
        hostPort: 30005
  - role: worker
    image: kindest/node:v1.32.8
    labels:
      app: jenkins
    extraMounts:
      - hostPath: /private/var/persist/jenkins
        containerPath: /private/var/persist/jenkins
  - role: worker
    image: kindest/node:v1.32.8
    labels:
      app: argocd
    extraMounts:
      - hostPath: /private/var/persist/argocd
        containerPath: /private/var/persist/argocd
```

## 클러스터 생성
```bash
kind create cluster --config kind-cluster.yaml
```

## 포트 매핑 정보

| Port  | Service       | Description  |
|-------|---------------|--------------|
| 30000 | TBD           | TBD          |
| 30001 | kube-ops-view |              |
| 30002 | ArgoCD        | ArgoCD HTTP  |
| 30003 | Jenkins       | Jenkins HTTP |
| 30004 | TBD           | TBD          |
| 30005 | TBD           | TBD          |

# 참고 링크
- https://kind.sigs.k8s.io/docs/user/configuration/#per-node-options
