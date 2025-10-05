
import os, json, boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
ddb = boto3.resource("dynamodb")
table = ddb.Table(TABLE_NAME)

def _resp(code, data):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(data)
    }

def lambda_handler(event, context):
    try:
        body = event.get("body") or "[]"
        items = json.loads(body)
        if not isinstance(items, list):
            return _resp(400, {"ok": False, "msg": "El body debe ser un JSON array de objetos"})
        count = 0
        with table.batch_writer(overwrite_by_pkeys=["TransaccionID"]) as bw:
            for it in items:
                required = ("TransaccionID", "ClienteID", "FechaHoraISO", "ComercioID")
                if not all(k in it for k in required):
                    continue
                clean = {k: v for k, v in it.items() if v is not None}
                try:
                    clean["ClienteID"] = int(clean["ClienteID"])
                    clean["ComercioID"] = int(clean["ComercioID"])
                except Exception:
                    return _resp(400, {"ok": False, "msg": "ClienteID y ComercioID deben ser numéricos"})
                bw.put_item(Item=clean)
                count += 1
        return _resp(200, {"ok": True, "insertados": count})
    except ClientError as e:
        return _resp(500, {"ok": False, "msg": e.response["Error"]["Message"]})
    except Exception as ex:
        return _resp(500, {"ok": False, "msg": str(ex)})
