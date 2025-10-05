#!/usr/bin/env bash
set -euo pipefail
npm i -g serverless
aws sts get-caller-identity || { echo 'Configura AWS CLI con credenciales válidas.'; exit 1; }
echo 'Ejecuta: ./deploy.sh'
