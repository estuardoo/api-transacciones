import os, json, boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
dynamodb = boto3.resource("dynamodb")

def _resp(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(data, ensure_ascii=False)
    }

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    tid = (params.get("TransaccionID") or "").strip()
    if not tid:
        return _resp(400, {"ok": False, "msg": "Falta TransaccionID"})
    try:
        table = dynamodb.Table(TABLE_NAME)
        r = table.get_item(Key={"TransaccionID": tid})
        if "Item" not in r:
            return _resp(404, {"ok": False, "msg": "Transacción no encontrada"})
        return _resp(200, {"ok": True, "data": r["Item"]})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
    except Exception as e:
        return _resp(500, {"ok": False, "msg": str(e)})
