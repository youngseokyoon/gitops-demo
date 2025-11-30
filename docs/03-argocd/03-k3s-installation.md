Ubuntu 24.04 환경에서 k3s k8s 클러스터에 ArgoCD 를 helm 사용하여 설치하기

kind 환경에 설정한 문서 확인 필요함.
- [Configure argocd to kind](./argocd-configure-kind.md)


Multipass 환경에서 K3s 및 ArgoCD를 이용한 도메인 접속이 가능하도록 구성한 문서
따라서 기존 NodePort 로 배포한 ArgoCD 를 ClusterIP 로 배포 후 Traefik Ingress 설정이 포함되어 있음. 

https://argocd.cicd.com


## Traefik?
컨테이너나 Kubernetes 환경에서 동작하는 Reverse Proxy, 인그레스 컨트롤러(Ingress Controller) 임.

Traefik is a modern HTTP reverse proxy and load balancer


## argocd 재배포 하기
[argocd-k3s.yaml](../../helmcharts/argocd/argocd-k3s.yaml)

NodePort, Ingress 를 사용하지 않도록 수정. 

기본적으로 생성하는 argocd-server ingress 사용은 중단
```bash
server:
  ingress:
    enabled: false
```

http 사용을 위한 옵션 추가해야함.
이 옵션은 ConfigMap 존재 하고, 아래 처럼 설정을 해줘야함
> kubectl -n argocd get cm argocd-cm -o yaml

```bash
configs:
  cm:
    server.insecure: true

  params:
    server.insecure: true
```

```bash
helm install argocd argo/argo-cd -n argocd -f argocd-k3s.yaml

helm upgrade argocd argo/argo-cd -n argocd -f argocd-k3s.yaml
```

## argocd-ingress 등록하기
[argocd-ingress.yaml](../../helmcharts/argocd/argocd-ingress.yaml)

argocd-server 에 동작하도록 설정을 해야 하기에 아래 처럼 backend 등록이 필요함.

```bash
spec:
  ingressClassName: traefik
  tls:
    - hosts:
        - argocd.cicd.com
      secretName: argocd-tls
  rules:
    - host: argocd.cicd.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: argocd-server
                port:
                  number: 80
```

```bash
kubectl apply -f argocd-ingress.yaml
```


# 참고 링크
- https://docs.k3s.io/networking/networking-services
- https://github.com/traefik/traefik
- https://doc.traefik.io/
