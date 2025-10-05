
#!/usr/bin/env bash
set -euo pipefail

REGION=${1:-us-east-1}
STAGE=${2:-dev}

echo "==> Verificando dependencias"
command -v npm >/dev/null || { echo "Instala npm"; exit 1; }
command -v aws >/dev/null || { echo "Instala AWS CLI"; exit 1; }

echo "==> Instalando Serverless si hace falta"
if ! command -v sls >/dev/null; then
  npm i -g serverless
fi

echo "==> Desplegando con Serverless (region=$REGION stage=$STAGE)"
sls deploy --region "$REGION" --stage "$STAGE" --verbose

echo "==> Mostrando endpoints"
sls info --region "$REGION" --stage "$STAGE"

echo "==> Descubriendo API ID y listando rutas (requiere jq)"
if command -v jq >/dev/null; then
  API_NAME="api-transacciones"
  REST_API_ID=$(aws apigateway get-rest-apis --region "$REGION" --query "items[?name==\\`$API_NAME\\`].id | [0]" --output text)
  BASE="https://${REST_API_ID}.execute-api.${REGION}.amazonaws.com/${STAGE}"
  echo "BASE=$BASE"
  aws apigateway get-resources --rest-api-id "$REST_API_ID" --region "$REGION"     --query "items[?methods].{p:path,m:keys(methods)}" --output json   | jq -r --arg base "$BASE" '.[] | .m[] as $method | "\($method) \($base)\(.p)"'
else
  echo "Instala jq para listar rutas bonitas: sudo apt-get install -y jq"
fi
