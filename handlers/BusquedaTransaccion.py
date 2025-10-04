import os
import json
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
dynamodb = boto3.resource("dynamodb")

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, ensure_ascii=False)
    }

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    transaccion_id = params.get("TransaccionID") if isinstance(params, dict) else None

    if not transaccion_id:
        return _resp(400, {"ok": False, "msg": "Falta parámetro TransaccionID"})

    table = dynamodb.Table(TABLE_NAME)
    try:
        res = table.get_item(Key={"TransaccionID": transaccion_id})
        item = res.get("Item")
        if not item:
            return _resp(404, {"ok": False, "msg": "Transacción no encontrada"})
        return _resp(200, {"ok": True, "data": item})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response.get('Error', {}).get('Message', str(e))})
    except Exception as e:
        return _resp(500, {"ok": False, "msg": str(e)})
