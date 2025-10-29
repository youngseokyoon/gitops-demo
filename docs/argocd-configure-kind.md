macOS 환경에서 kind k8s 클러스터에 ArgoCD 를 helm 사용하여 설치하기

# Prerequisite
* kubectl
* kind 클러스터 설정 [kind-cluster.yaml](../../assets/kind-cluster.yaml)
* CICD Storage Class 설정 (optional: PV 생성 시 default storageclass 로 설정 해도 됨)
  [cicd-storageclass.yaml](./cicd-storageclass.yaml)

# Namespace 생성
```bash
kubectl create ns argocd
```

# PersistentVolume 생성 (optional)
- [jenkins-persistence.yaml](./jenkins-persistence.yaml)

kind 로 구성할 때 2개의 워커 노드를 설정을 하였고, 각각 jenkins, argocd 를 위한 hostPath 지정함.

PV 사용을 원지 않으면, 이 과정은 생략 가능함.
```bash
kubectl apply -f jenkins-persistence.yaml
```

# Helm 차트 다운로드
- 필요한 버전을 확인 후 다운로드

2025.10.29 기준 최신 버전 9.0.5
- https://artifacthub.io/packages/helm/argo/argo-cd

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

helm pull argo/argo-cd  --version 9.0.5 --untar
```

# values.yaml 파일 생성 (9.0.5 기준)

[argocd-values.yaml](../argocd-values.yaml)

# ArgoCD Helm 차트 설치
```bash
helm install argocd argo/argo-cd -n argocd -f argocd-values.yaml

helm upgrade argocd argo/argo-cd -n argocd -f argocd-values.yaml
```

# 동작 검증 
```bash
# 모든 리소스 확인
kubectl get pod,svc,ep,secret,cm -n argocd
kubectl get crd | grep argo
applications.argoproj.io                     2024-04-14T08:12:16Z
applicationsets.argoproj.io                  2024-04-14T08:12:17Z
appprojects.argoproj.io                      2024-04-14T08:12:16Z

kubectl get appproject -n argocd -o yaml

# configmap
kubectl get cm -n argocd argocd-cm -o yaml
kubectl get cm -n argocd argocd-rbac-cm -o yaml
...
data:
policy.csv: ""
policy.default: ""
policy.matchMode: glob
scopes: '[groups]'
```

## 초기 admin 비밀번호 얻기
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d ;echo
jm7nLuQqTg1U3T3L
```

## 비밀번호 변경
위에서 얻은 초기 admin 비밀번호를 사용하여 비밀번호 변경.
e.g) admin:argopass

localhost:30002 접속 후 User Info -> UPDATE PASSWORD 클릭 후 암호 변경.

# Repository 추가
github 에서 원하는 repository 를 생성 후, ArgoCD 에서 해당 repository 를 추가.

Settings -> Repositories -> CONNECT REPO

연결 방법: ssh, https/http, github app, google cloud 지원.

e.g) ssh 연결을 통해 연결한 경우
* type: git
* url: https://github.com/youngseokyoon/jenkinsci-helm-charts

![Add Repository](./assets/argocd-add-repository.png)

# Application 생성
jenkinsci-helm-charts 저장소에 있는 jenkins helm 차트를 배포하기 위한 Application 생성.

- git@github.com:youngseokyoon/jenkinsci-helm-charts.git

Applications -> NEW APP 클릭
* Application Name: cicd-jenkins
* Project: default
* Sync Policy: Automatic
* Repository URL: git@github.com:youngseokyoon/jenkinsci-helm-charts.git

Sync 후 결과
![jenkins.png](../../assets/argocd-jenkins-ok.png)

