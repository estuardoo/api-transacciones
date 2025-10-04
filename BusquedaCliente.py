import os, json, boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
INDEX = "GSI_Cliente_Fecha"
dynamodb = boto3.resource("dynamodb")

def _resp(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(data)
    }

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    cid = params.get("ClienteID")
    if not cid:
        return _resp(400, {"ok": False, "msg": "Falta ClienteID"})
    table = dynamodb.Table(TABLE_NAME)
    try:
        resp = table.query(IndexName=INDEX, KeyConditionExpression=Key("ClienteID").eq(int(cid)))
        return _resp(200, {"ok": True, "data": resp.get("Items", [])})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
