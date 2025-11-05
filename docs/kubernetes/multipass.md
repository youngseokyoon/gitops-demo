# Multipass

https://canonical.com/multipass

canonical 에서 공식적으로 제공하는 Ubuntu VM 생성 툴.
Kubernetes 검증 시 가상 Node 가 필요한 경우가 있는데, 이때 사용할 수 있는 툴로 생각됨.

# Install
https://canonical.com/multipass/install

Linux, Windows, MacOS 모두 지원함.

```bash
# Ubuntu 24.04 에서는 snap 을 사용하여 설치 가능.
sudo snap install multipass
[sudo] $USER 암호: 
multipass 1.16.1 from Canonical✓ installed
```


# Node 생성
multipass.gui 에서 생성을 해도 되고, 위의 문서를 참고해서 CLI 환경에서 생성을 해도 됨.

- jenkins-0 로 생성함.

```bash
multipass info jenkins-0 

Name:           jenkins-0
State:          Running
Snapshots:      0
IPv4:           10.21.166.79
                10.0.1.130
Release:        Ubuntu 24.04.3 LTS
Image hash:     85743244cc8f (Ubuntu 24.04 LTS)
CPU(s):         4
Load:           0.68 0.16 0.05
Disk usage:     3.4GiB out of 19.3GiB
Memory usage:   706.1MiB out of 7.7GiB
Mounts:         /home/ryoon/volumes/jenkins-persist => /private/var/persist/jenkins
                    UID map: 1000:default
                    GID map: 1000:default
```

# jenkins-0 Node join, k3s cluster
https://docs.k3s.io/quick-start

k3s 에서 join 을 시키려면 k3s control plain 의 IP와 TOKEN 이 필요함
아래의 명령어를 참고해서 각각 획득.

```bash
sudo cat /var/lib/rancher/k3s/server/node-token
K10ac47517ef2939eec0b384dba37cb387d754c7caa54427cb3accab1d0a1d1e5eb::server:00ce5daf9ab813ca7fa1bf5b3d99ec63

hostname -I
10.88.57.219 10.4.0.1 10.0.0.95 10.21.166.1 

hostname -l
127.0.1.1
```

join 을 하려면 실제 node(jenkins-0) 에 접속을 해서 join 명령어를 입력해야 함.
multipass 에서는 shell 명령어로 각각의 node 에 접속을 할 수 있음.

```bash
multipass shell jenkins-0 

ubuntu@jenkins-0:~$ 
ubuntu@jenkins-0:~$ curl -sfL https://get.k3s.io | \
K3S_URL="https://10.88.57.219:6443" \
K3S_TOKEN="K10ac47517ef2939eec0b384dba37cb387d754c7caa54427cb3accab1d0a1d1e5eb::server:00ce5daf9ab813ca7fa1bf5b3d99ec63" \
sh - 
```

## node 상태 확인
```bash
 k get no
NAME        STATUS   ROLES                  AGE   VERSION
jenkins-0   Ready    <none>                 54s   v1.33.5+k3s1
ryoon-l1    Ready    control-plane,master   36d   v1.33.4+k3s1
```

# 참고 링크
- https://documentation.ubuntu.com/multipass/latest/
