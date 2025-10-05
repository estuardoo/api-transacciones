import os, json, boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
INDEX = "GSI_Usuario_Fecha"
dynamodb = boto3.resource("dynamodb")

def _resp(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(data, ensure_ascii=False)
    }

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    usuario = (params.get("Usuario") or "").strip()
    if not usuario:
        return _resp(400, {"ok": False, "msg": "Falta Usuario"})
    table = dynamodb.Table(TABLE_NAME)
    resp = table.query(IndexName=INDEX, KeyConditionExpression=Key("Usuario").eq(usuario))
    return _resp(200, {"ok": True, "count": resp.get("Count", 0), "data": resp.get("Items", [])})
