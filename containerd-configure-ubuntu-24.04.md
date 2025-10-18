
# Getting started with containerd
https://github.com/containerd/containerd/blob/main/docs/getting-started.md

이곳에 containerd 설정하는 방법이 총 3가지가 있음.
1. 공식 바이너리 이미지를 사용하는 방법.
2. 패키지 매니저를 사용하는 방법.
3. 소스코드를 빌드하는 방법.

해당 문서에서는 2번 패키지 매니저를 사용하는 방법을 설명함.
## Install containerd from package manager

```bash
sudo apt update
sudo apt install -y containerd
```
## Configure containerd
```bash
# 기본 설정 생성
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml

# systemd cgroup 드라이버 활성화 (Kubernetes 호환성 확보)
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

# 서비스 적용
sudo systemctl restart containerd
sudo systemctl enable containerd
```

## install CNI plugins
```bash
sudo mkdir -p /opt/cni/bin

CNI_VERSION=$(curl -s https://api.github.com/repos/containernetworking/plugins/releases/latest \
| grep tag_name | cut -d '"' -f4)

wget https://github.com/containernetworking/plugins/releases/download/${CNI_VERSION}/cni-plugins-linux-amd64-${CNI_VERSION}.tgz

sudo tar -C /opt/cni/bin -xzf cni-plugins-linux-amd64-${CNI_VERSION}.tgz
```



## [Optional] install nerdctl
https://github.com/containerd/nerdctl

### nerdctl 최신 릴리스 확인
https://github.com/containerd/nerdctl/releases

```bash
VERSION=$(curl -s https://api.github.com/repos/containerd/nerdctl/releases/latest \
| grep tag_name | cut -d '"' -f4)

e.g) v2.1.4
```

### 다운로드 및 설치
```bash
wget https://github.com/containerd/nerdctl/releases/download/${VERSION}/nerdctl-${VERSION#v}-linux-amd64.tar.gz
sudo tar -C /usr/local/bin -xzf nerdctl-${VERSION#v}-linux-amd64.tar.gz

```
e.g)
wget https://github.com/containerd/nerdctl/releases/download/v2.1.4/nerdctl-2.1.4-linux-amd64.tar.gz
sudo tar -C /usr/local/bin -xzf nerdctl-v2.1.4-linux-amd64.tar.gz

## [Optional] sudo 없이 nerdctl 사용 설정

```bash
# containerd 전용 그룹 생성 (이름 자유, 여기서는 'containerd')
sudo groupadd containerd

# 현재 사용자를 그룹에 추가
sudo usermod -aG containerd $USER

# 소켓 권한 변경
sudo chown root:containerd /run/containerd/containerd.sock
sudo chmod 660 /run/containerd/containerd.sock

# systemd drop-in으로 영구 적용
sudo mkdir -p /etc/systemd/system/containerd.service.d
sudo tee /etc/systemd/system/containerd.service.d/override.conf <<EOF
[Service]
ExecStartPost=/bin/sh -c 'chown root:containerd /run/containerd/containerd.sock && chmod 660 /run/containerd/containerd.sock'
EOF

# 서비스 재시작
sudo systemctl daemon-reexec
sudo systemctl restart containerd

# 세션 재로그인 필요

```