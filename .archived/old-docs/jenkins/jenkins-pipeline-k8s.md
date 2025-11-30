
# Declarative 타입 Pipeline 으로 검증
* Nginx pod 실행하기

## Pipeline 코드
```bash
pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
metadata:
  name: nginx-test
spec:
  terminationGracePeriodSeconds: 5
  containers:
  - name: nginx
    image: nginx:latest
    command:
    - cat
    tty: true
"""
            defaultContainer 'nginx'
            idleMinutes 0          // Pipeline 종료 후 바로 삭제
        }
    }

    stages {
        stage('Run nginx') {
            steps {
                container('nginx') {
                    sh 'echo "Hello from nginx"'
                }
            }
        }
    }
}
```

## Pipeline console 출력
```console
<snip>

Agent k8s-2-rs0x4-121kz-5b8hw is provisioned from template k8s_2-rs0x4-121kz
---
apiVersion: "v1"
kind: "Pod"
metadata:
  annotations:
    kubernetes.jenkins.io/last-refresh: "1761760421264"
    buildUrl: "http://cicd-jenkins.cicd-jenkins.svc.cluster.local:8080/job/k8s/2/"
    runUrl: "job/k8s/2/"
  labels:
    jenkins/label-digest: "5fadd9d940e20ea7299b232c053f9f250323ddfd"
    jenkins/cicd-jenkins-jenkins-agent: "true"
    jenkins/label: "k8s_2-rs0x4"
    kubernetes.jenkins.io/controller: "http___cicd-jenkins_cicd-jenkins_svc_cluster_local_8080x"
  name: "k8s-2-rs0x4-121kz-5b8hw"
  namespace: "cicd-jenkins"
spec:
  containers:
  - command:

<snip>

Running on k8s-2-rs0x4-121kz-5b8hw in /home/jenkins/agent/workspace/k8s
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Run nginx)
[Pipeline] container
[Pipeline] {
[Pipeline] sh
+ echo Hello from nginx container
Hello from nginx container
[Pipeline] }
[Pipeline] // container
[Pipeline] }
[Pipeline] // stage
[Pipeline] }
[Pipeline] // node
[Pipeline] }
[Pipeline] // podTemplate
[Pipeline] End of Pipeline
Finished: SUCCESS
```
