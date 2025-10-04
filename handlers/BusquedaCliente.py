import os
import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
INDEX_NAME = "GSI_Cliente_Fecha"

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
    cliente_id = params.get("ClienteID") if isinstance(params, dict) else None
    if not cliente_id:
        return _resp(400, {"ok": False, "msg": "Falta parámetro ClienteID"})

    try:
        cliente_id_n = int(cliente_id)
    except Exception:
        return _resp(400, {"ok": False, "msg": "ClienteID debe ser numérico"})

    desde = (params.get("Desde") or "").strip() if isinstance(params, dict) else ""
    hasta = (params.get("Hasta") or "").strip() if isinstance(params, dict) else ""

    table = dynamodb.Table(TABLE_NAME)

    key_cond = Key("ClienteID").eq(cliente_id_n)
    if desde and hasta:
        key_cond = key_cond & Key("FechaHoraISO").between(desde, hasta)
    elif desde:
        key_cond = key_cond & Key("FechaHoraISO").gte(desde)
    elif hasta:
        key_cond = key_cond & Key("FechaHoraISO").lte(hasta)

    try:
        resp = table.query(
            IndexName=INDEX_NAME,
            KeyConditionExpression=key_cond
        )
        items = resp.get("Items", [])
        while "LastEvaluatedKey" in resp:
            resp = table.query(
                IndexName=INDEX_NAME,
                KeyConditionExpression=key_cond,
                ExclusiveStartKey=resp["LastEvaluatedKey"]
            )
            items.extend(resp.get("Items", []))

        return _resp(200, {"ok": True, "count": len(items), "data": items})

    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response.get('Error', {}).get('Message', str(e))})
    except Exception as e:
        return _resp(500, {"ok": False, "msg": str(e)})
