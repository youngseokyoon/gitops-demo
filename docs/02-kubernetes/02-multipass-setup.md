# Multipass

해당 문서는 Ubuntu 24.04 PC 기준으로 작성 됨.

Multipass is a lightweight VM manager for Linux, Windows and macOS. 
It's designed for developers who want to spin up a fresh Ubuntu environment with a single command. 
It uses KVM on Linux, Hyper-V on Windows and QEMU on macOS to run virtual machines with minimal overhead. 
It can also use VirtualBox on Windows and macOS. 
Multipass will fetch Ubuntu images for you and keep them up to date.

Since it supports metadata for cloud-init, you can simulate a small cloud deployment on your laptop or workstation.

https://canonical.com/multipass

- **cloud-init 를 지원함.**
- canonical 에서 공식적으로 제공하는 Ubuntu VM 생성 툴.

## Install
https://canonical.com/multipass/install

- Linux, Windows, MacOS 모두 지원함.

```bash
# Ubuntu 24.04 에서는 snap 을 사용하여 설치 가능.
sudo snap install multipass
[sudo] $USER 암호: 
multipass 1.16.1 from Canonical✓ installed
```

### Multipass 네트워크 설정 변경하기

설정 으로 이동 후 Virtualization 에서 내용 확인
Driver: QEMU
Bridged network: mpqemubr0

## Node 설정
jenkins-0, argocd-0 생성 예정.

| name      | cpu | memory | disk   | volume                                                           | note                       |
|-----------|-----|--------|--------|------------------------------------------------------------------|----------------------------|
| jenkins-0 | 4   | 8 GiB  | 20 Gib | /home/ryoon/volumes/jenkins-persist:/private/var/persist/jenkins | jenkins-pv 사용을 위해 설정이 필요함  |
| argocd-0  | 4   | 8 GiB  | 20 Gib |                                                                  |                            |


### Node 생성하기
Multipass 는 GUI 도 지원함.

```bash
# argocd-0 생성
multipass launch --name argocd-0 --cpus 4 --memory 8G --disk 20G --network mpqemubr0

# jenkins-0 생성
multipass launch --name jenkins-0 --cpus 4 --memory 8G --disk 20G --network mpqemubr0 \
  --mount /home/ryoon/volumes/jenkins-persist:/private/var/persist/jenkins
```

### k3s cluster 에 Node join 시키기
k3s cluster 에서 join 을 시키기 위해선 k3s control plain 의 IP와 TOKEN 이 필요함

- mpqemubr0 사용예정

```bash
 nmcli d show mpqemubr0 | grep ADDRESS
IP4.ADDRESS[1]:                         10.21.166.1/24
```

e.g)
```bash
sudo cat /var/lib/rancher/k3s/server/node-token
K10ac47517ef2939eec0b384dba37cb387d754c7caa54427cb3accab1d0a1d1e5eb::server:00ce5daf9ab813ca7fa1bf5b3d99ec63

hostname -I
172.30.1.60 10.0.0.95 192.168.122.1 10.21.166.1
```

IP: 192.168.122.1
TOKEN: K10ac47517ef2939eec0b384dba37cb387d754c7caa54427cb3accab1d0a1d1e5eb::server:00ce5daf9ab813ca7fa1bf5b3d99ec63

각 node 에 접속 후 join 명령어 입력, multipass exec 도 사용가능

```bash
# argocd-0 node 접속
$ multipass shell argocd-0 

# k3s cluster 에 join
ubuntu@argocd-0:~$ curl -sfL https://get.k3s.io | \
K3S_URL="https://10.21.166.1:6443" \
K3S_TOKEN="K10ac47517ef2939eec0b384dba37cb387d754c7caa54427cb3accab1d0a1d1e5eb::server:00ce5daf9ab813ca7fa1bf5b3d99ec63" \
sh -
[INFO]  Finding release for channel stable
[INFO]  Using v1.33.5+k3s1 as release
[INFO]  Downloading hash https://github.com/k3s-io/k3s/releases/download/v1.33.5+k3s1/sha256sum-amd64.txt

<snip>

[INFO]  systemd: Enabling k3s-agent unit
Created symlink /etc/systemd/system/multi-user.target.wants/k3s-agent.service → /etc/systemd/system/k3s-agent.service.
[INFO]  systemd: Starting k3s-agent
```

### Node label 설정 - optional

각 node 에 label 설정 
jenkins-0: app=jenkins
argocd-0: app=argocd

```bash
kubectl get no
NAME        STATUS   ROLES                  AGE   VERSION
argocd-0    Ready    <none>                 45m   v1.33.5+k3s1
jenkins-0   Ready    <none>                 43m   v1.33.5+k3s1
ryoon-l1    Ready    control-plane,master   37d   v1.33.4+k3s1

kubectl label nodes jenkins-0 app=jenkins
node/jenkins-0 labeled

kubectl label nodes argocd-0 app=argocd
node/argocd-0 labeled
```

## troubleshooting
### mpqemubr0 연결이 간혹 끊어지는 현상이 발생함.
tap 연결 향상을 위해 stp 설정을 on 으로 변경함.

```bash
sudo brctl stp mpqemubr0 on
```

### WiFi 절전모드 해제
```bash
sudo vi /etc/NetworkManager/conf.d/default-wifi-powersave-on.conf
[connection]
wifi.powersave = 2
```

# 참고 링크
- https://documentation.ubuntu.com/multipass/latest/
- https://github.com/canonical/multipass
- https://docs.k3s.io/quick-start
