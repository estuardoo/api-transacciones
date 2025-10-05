# api-transacciones

API Serverless (Lambda + API Gateway + DynamoDB).

## Despliegue
npm i -g serverless
sls deploy --region us-east-1 --stage dev

## Carga de datos
pip3 install --user boto3 pandas openpyxl
python3 subir_comercios.py --input comercios.xlsx --sheet TablaComercio --region us-east-1
python3 subir_transacciones.py --input transacciones.xlsx --sheet TablaTransaccion --region us-east-1
