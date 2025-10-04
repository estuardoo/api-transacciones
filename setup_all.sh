#!/usr/bin/env bash
set -euo pipefail

AWS_ACCOUNT_ID="102362304326"
AWS_REGION="us-east-1"
REPO_OWNER="estuardoo"
REPO_NAME="api-transacciones"
LAB_ROLE_NAME="LabRole"
DEPLOY_ROLE_NAME="GitHubActionsDeployRole"

echo "==> Verificando aws, git, gh, node, npm"
for cmd in aws git gh node npm; do
  command -v $cmd >/dev/null || { echo "Falta $cmd"; exit 1; }
done

echo "==> Creando/actualizando rol OIDC para GitHub Actions: ${DEPLOY_ROLE_NAME}"
TRUST_DOC='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Federated": "arn:aws:iam::'"${AWS_ACCOUNT_ID}"':oidc-provider/token.actions.githubusercontent.com" },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
        "StringLike": { "token.actions.githubusercontent.com:sub": "repo:'"${REPO_OWNER}/${REPO_NAME}"':*" }
      }
    }
  ]
}'
if ! aws iam get-role --role-name "${DEPLOY_ROLE_NAME}" >/dev/null 2>&1; then
  aws iam create-role --role-name "${DEPLOY_ROLE_NAME}" --assume-role-policy-document "${TRUST_DOC}" >/dev/null
else
  aws iam update-assume-role-policy --role-name "${DEPLOY_ROLE_NAME}" --policy-document "${TRUST_DOC}" >/dev/null
fi

echo "==> Adjuntando política ServerlessDeployPolicy"
POLICY_DOC='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["cloudformation:*","lambda:*","apigateway:*","logs:*","dynamodb:*","iam:PassRole"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::'"${AWS_ACCOUNT_ID}"':role/'"${LAB_ROLE_NAME}"'"
    }
  ]
}'
aws iam put-role-policy --role-name "${DEPLOY_ROLE_NAME}" --policy-name ServerlessDeployPolicy --policy-document "${POLICY_DOC}" >/dev/null

echo "==> Asegurando permisos mínimos de DynamoDB para ${LAB_ROLE_NAME}"
READ_DOC='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem","dynamodb:Query","dynamodb:DescribeTable"],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/TablaTransaccion",
        "arn:aws:dynamodb:*:*:table/TablaTransaccion/index/*",
        "arn:aws:dynamodb:*:*:table/TablaComercio",
        "arn:aws:dynamodb:*:*:table/TablaComercio/index/*"
      ]
    }
  ]
}'
aws iam put-role-policy --role-name "${LAB_ROLE_NAME}" --policy-name DynamoDBReadAccess --policy-document "${READ_DOC}" >/dev/null

echo "==> Inicializando repo Git y subiendo a GitHub"
git init -b main
git add .
git commit -m "init api-transacciones serverless + dynamodb + lambdas"
if gh repo view "${REPO_OWNER}/${REPO_NAME}" >/dev/null 2>&1; then
  echo "Repo existe, configurando remote origin"
  git remote remove origin >/dev/null 2>&1 || true
  git remote add origin "https://github.com/${REPO_OWNER}/${REPO_NAME}.git"
else
  gh repo create "${REPO_OWNER}/${REPO_NAME}" --public --source=. --remote=origin --push
fi
git push -u origin main

echo "==> Todo listo. Revisa el workflow en:"
echo "https://github.com/${REPO_OWNER}/${REPO_NAME}/actions"
