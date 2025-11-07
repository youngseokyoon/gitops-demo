# Kubernetes Ingress Example with ArgoCD and Jenkins
This example demonstrates how to set up Kubernetes Ingress resources to expose ArgoCD and Jenkins services using host-based routing. The setup assumes you have a Kubernetes cluster with ArgoCD and Jenkins deployed.

## Prerequisites
- A running Kubernetes cluster
- ArgoCD and Jenkins deployed in the cluster.
- traefik ingress controller installed in the cluster.

## Create ArgoCD Ingress
Create an Ingress resource for ArgoCD. Save the following YAML as argocd-ingress.yaml

[argocd-ingress.yaml](../../helmcharts/argocd/argocd-ingress.yaml)

## Create Jenkins Ingress
Create an Ingress resource for Jenkins. Save the following YAML as jenkins-ingress.yaml

[jenkins-ingress.yaml](../../helmcharts/jenkins/jenkins-ingress.yaml)

## Current Cluster Node and Hosts Information

```console
$ k get no -o wide

NAME        STATUS   ROLES                  AGE   VERSION        INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
argocd-0    Ready    <none>                 24h   v1.33.5+k3s1   10.21.166.194   <none>        Ubuntu 24.04.3 LTS   6.8.0-87-generic    containerd://2.1.4-k3s1
jenkins-0   Ready    <none>                 26h   v1.33.5+k3s1   10.21.166.244   <none>        Ubuntu 24.04.3 LTS   6.8.0-87-generic    containerd://2.1.4-k3s1
hostpc      Ready    control-plane,master   38d   v1.33.4+k3s1   172.30.1.60     <none>        Ubuntu 24.04.3 LTS   6.14.0-35-generic   containerd://2.0.5-k3s2
```

## Update /etc/hosts file
Add the following entries to your /etc/hosts file to map the hostnames to the internal IP addresses of the nodes.

```console
$ cat /etc/hosts

10.21.166.194  argocd.cicd.com
10.21.166.244  jenkins.cicd.com
```
