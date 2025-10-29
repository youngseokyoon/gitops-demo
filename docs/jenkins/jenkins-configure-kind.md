macOS 환경에서 kind k8s 클러스터에 Jenkins 를 helm 사용하여 설치하기

# Prerequisites
* kubectl
* [kind 클러스터 설정](../kubernetes-configure-kind.md)
* CICD Storage Class 설정 (optional: PV 생성 시 default storageclass 로 설정 해도 됨)
[cicd-storageclass.yaml](./cicd-storageclass.yaml)

# Namespace 생성
```bash
kubectl create namespace cicd-jenkins
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

2025.10.29 기준 최신 버전 5.8.104
- https://github.com/jenkinsci/helm-charts/releases/tag/jenkins-5.8.104

```bash
# 사전에 만들어 놓은 jenkins 5.8.104 버전
git clone git@github.com:youngseokyoon/jenkinsci-helm-charts.git -b 5.8.104
```

```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update

helm pull jenkins/jenkins --version 5.8.104 --untar
```

# values.yaml 설정 파일 작성 (5.8.104 기준)

[jenkins-5.8.104.yaml](https://github.com/youngseokyoon/jenkinsci-helm-charts/blob/5.8.104/charts/jenkins/jenkins-5.8.104.yaml)


# Jenkins Helm 차트 설치
```bash
helm install cicd-jenkins -n cicd-jenkins -f jenkins-5.8.104.yaml charts/jenkins
```

# 참고 링크
- https://github.com/jenkinsci/helm-charts
- https://artifacthub.io/packages/helm/jenkinsci/jenkins
