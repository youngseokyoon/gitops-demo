#!/bin/bash

# 사용법:
# export VAULT_TOKEN=<YOUR_ROOT_TOKEN>
# sh setup-vault.sh

if [ -z "$VAULT_TOKEN" ]; then
  echo "Error: VAULT_TOKEN environment variable is not set."
  echo "Usage: export VAULT_TOKEN=<YOUR_ROOT_TOKEN> && sh $0"
  exit 1
fi

export K8S_HOST="https://$KUBERNETES_PORT_443_TCP_ADDR:443"

# Vault 로그인 및 설정
kubectl exec -n vault vault-0 -- sh -c "
vault login $VAULT_TOKEN
vault auth enable kubernetes
vault write auth/kubernetes/config kubernetes_host=$K8S_HOST
vault secrets enable -version=2 -path=secret kv

vault policy write myapp-policy - <<EOF
path \"secret/data/myapp/*\" {
  capabilities = [\"read\", \"list\"]
}
EOF

vault write auth/kubernetes/role/myapp-role \
  bound_service_account_names=myapp-sa \
  bound_service_account_namespaces=default \
  policies=myapp-policy \
  ttl=24h

vault kv put secret/myapp/database username=dbuser password=dbpassword
"
