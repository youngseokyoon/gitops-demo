helm upgrade argocd argo/argo-cd -n argocd -f argocd-keycloak-vaules.yaml
kubectl rollout restart deployment argocd-server -n argocd