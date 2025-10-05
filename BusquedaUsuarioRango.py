import os, json, boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
INDEX = "GSI_Usuario_Fecha"
dynamodb = boto3.resource("dynamodb")

def _resp(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(data, ensure_ascii=False)
    }

def _to_iso_floor(s):
    s = (s or "").strip()
    if not s: return None
    try:
        if len(s) == 10:
            return f"{s}T00:00:00Z"
        dt = datetime.fromisoformat(s.replace("Z","").replace(" ","T"))
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return s

def _to_iso_ceil(s):
    s = (s or "").strip()
    if not s: return None
    try:
        if len(s) == 10:
            return f"{s}T23:59:59Z"
        dt = datetime.fromisoformat(s.replace("Z","").replace(" ","T"))
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return s

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    usuario = (params.get("Usuario") or "").strip()
    fecha1 = _to_iso_floor(params.get("fecha1"))
    fecha2 = _to_iso_ceil(params.get("fecha2"))
    if not usuario or not fecha1 or not fecha2:
        return _resp(400, {"ok": False, "msg": "Faltan parámetros: Usuario, fecha1, fecha2"})
    table = dynamodb.Table(TABLE_NAME)
    resp = table.query(
        IndexName=INDEX,
        KeyConditionExpression=Key("Usuario").eq(usuario) & Key("FechaHoraISO").between(fecha1, fecha2)
    )
    return _resp(200, {"ok": True, "count": resp.get("Count", 0), "data": resp.get("Items", [])})
