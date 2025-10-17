# Requirements (실습 중심)

## 1. 컨테이너 레지스트리 등록
**Docker Hub** 또는 **Quay.io** 계정이 필요하다.  
두 서비스는 모두 무료 공개 저장소를 제공하지만, 정책과 기능에 차이가 있다.

| 항목    | Docker Hub | Quay.io |
|--------|-------------|---------|
| 공개 저장소 | 무제한 | 무제한 |
| 비공개 저장소 | 무료 계정은 제한 (보통 1개) | 무료 계정은 불가 (유료 필요) |
| Pull 제한 | 무료 사용자 시간당 제한 있음 | 일반적으로 제한 없음 (과도 시 제약 가능) |
| 빌드 자동화 | GitHub, Bitbucket 연동 가능 | GitHub, GitLab 연동 가능 |
| 보안 스캔 | 일부 요금제 제공 | 무료로 이미지 취약점 스캔 제공 |
| 권한 제어 | 유료 계정 중심 | 팀, 조직, 로봇 계정 지원 |
| 정책 안정성 | 정책 변경 가능 | 오픈소스 기반, 정책 안정적 |

---

## 2. Git 저장소 등록
스터디용 Git 저장소를 포크 후 로컬로 복제한다.

token 설정은 아래 링크 참고

https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens


```bash
# GitHub 접속 후 포크
https://github.com/gitops-cookbook/gitops-cookbook-sc

# 로컬 복제
git clone https://github.com/gitops-cookbook/chapters.git
cd chapters
```

## 3. 로컬 Kubernetes 클러스터 생성 ([kind](https://kind.sigs.k8s.io/) 를 사용하여 구성)
kind k8s - v1.32.8

kind는 Docker 컨테이너 안에서 Kubernetes 클러스터를 생성하는 도구이다.
주로 테스트 및 GitOps 실습 환경으로 사용한다.

kind 설치 (https://kind.sigs.k8s.io/docs/user/quick-start/)
```bash
# macOS
# Install Kind
brew install kind
kind --version

# Install kubectl
brew install kubernetes-cli
kubectl version --client=true

## kubectl -> k 단축키 설정
echo "alias kubectl=kubecolor" >> ~/.zshrc

# Install Helm
brew install helm
helm version

# Install tools
brew install krew
brew install kube-ps1
brew install kubectx
brew install k9s

# kubectl 출력 시 하이라이트 처리
brew install kubecolor
echo "alias k=kubectl" >> ~/.zshrc
echo "alias kubectl=kubecolor" >> ~/.zshrc
echo "compdef kubecolor=kubectl" >> ~/.zshrc

# k8s krew path : ~/.zshrc 아래 추가
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
```

기 사용 중인 kubeconfig 는 알아서 백업 or KUBECONFIG 설정하는 것을 추천함.
```bash
export KUBECONFIG=/Users/<Username>/Downloads/kind/config
```

클러스터 생성하기
```bash
# 클러스터 배포 전 확인
docker info
docker ps

# Create a cluster with kind
kind create cluster --name myk8s --image kindest/node:v1.32.8 --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30000
    hostPort: 30000
  - containerPort: 30001
    hostPort: 30001
- role: worker
EOF


# 확인
docker images
kind get nodes --name myk8s
kubens default

# kind 는 별도 도커 네트워크 생성 후 사용 : 예) docker 기본값 172.18.0.0/16 , orbstack 192.168.97.0/24
docker network ls
docker inspect kind | jq

# k8s api 주소 확인 : 어떻게 로컬에서 접속이 되는 걸까?
kubectl cluster-info
docker ps

# 노드 정보 확인 : CRI 는 containerd 사용
kubectl get node -o wide

# 파드 정보 확인 : CNI 는 kindnet 사용
kubectl get pod -A -o wide

# 네임스페이스 확인 >> 도커 컨테이너에서 배운 네임스페이스와 다릅니다!
kubectl get namespaces

# 컨트롤플레인/워커 노드(컨테이너) 확인 : 도커 컨테이너 이름은 myk8s-control-plane , myk8s-worker 임을 확인
docker ps
docker images
docker exec -it myk8s-control-plane ss -tnlp

# 디버그용 내용 출력에 ~/.kube/config 권한 인증 로드
kubectl get pod -v6

# kube config 파일 확인
cat ~/.kube/config
혹은
cat $KUBECONFIG
```


