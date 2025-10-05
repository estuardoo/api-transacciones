
import os, json, boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
INDEX = "GSI_Comercio_Fecha"
dynamodb = boto3.resource("dynamodb")

def _resp(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
        "body": json.dumps(data)
    }

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    comercio = params.get("ComercioID")
    if not comercio:
        return _resp(400, {"ok": False, "msg": "Falta ComercioID"})
    table = dynamodb.Table(TABLE_NAME)
    try:
        resp = table.query(
            IndexName=INDEX,
            KeyConditionExpression=Key("ComercioID").eq(int(comercio)),
            ScanIndexForward=False  # orden por fecha desc
        )
        return _resp(200, {"ok": True, "data": resp.get("Items", [])})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
