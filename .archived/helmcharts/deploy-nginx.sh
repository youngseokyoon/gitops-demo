CONFIG_HASH=$(kubectl get configmap k3s-nginx-config -o json | sha256sum | awk '{print $1}')
echo "Configuration hash: $CONFIG_HASH"
# CONFIG_HASH 는 추후 ArgoCD hook 에서 처리 예정.

helm upgrade --install k3s-nginx bitnami/nginx \
  -f k3s-nginx.yaml \
  --set deploymentAnnotations.configmap-reload=$CONFIG_HASH
