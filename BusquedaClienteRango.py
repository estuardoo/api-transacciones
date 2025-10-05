
import os, json, boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
INDEX = "GSI_Cliente_Fecha"
dynamodb = boto3.resource("dynamodb")

def _resp(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
        "body": json.dumps(data)
    }

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    cid = params.get("ClienteID")
    desde = params.get("desde")
    hasta = params.get("hasta")
    if not cid or not desde or not hasta:
        return _resp(400, {"ok": False, "msg": "Faltan parámetros: ClienteID, desde, hasta (ISO 8601)"})
    table = dynamodb.Table(TABLE_NAME)
    try:
        resp = table.query(
            IndexName=INDEX,
            KeyConditionExpression=Key("ClienteID").eq(int(cid)) & Key("FechaHoraISO").between(desde, hasta),
            ScanIndexForward=False
        )
        return _resp(200, {"ok": True, "data": resp.get("Items", [])})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
