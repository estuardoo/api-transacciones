
#!/usr/bin/env bash
set -euo pipefail

echo "==> Actualizando paquetes"
sudo apt-get update -y

echo "==> Instalando jq y Python deps opcionales"
sudo apt-get install -y jq python3-pip

echo "==> Instalando Serverless (si no está)"
if ! command -v sls >/dev/null; then
  sudo npm i -g serverless
fi

echo "==> Instalando librerías Python para scripts de carga"
pip3 install --user boto3 pandas openpyxl

echo "==> Completado. Usa ./deploy.sh para desplegar."
