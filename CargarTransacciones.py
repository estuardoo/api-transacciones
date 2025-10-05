import os, json, boto3
from decimal import Decimal
from datetime import datetime, timezone

TABLE_NAME = os.environ.get("TABLA_TRANSACCION", "TablaTransaccion")
dynamodb = boto3.resource("dynamodb")

def _resp(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(data, ensure_ascii=False)
    }

def _to_int(x):
    if x is None or str(x).strip()=="":
        return None
    return int(str(x).strip())

def _to_bool(x):
    if x is None: return None
    s = str(x).strip().lower()
    return s in ("1","true","t","yes","y","si","sí")

def _to_dec(x):
    if x is None: return None
    s = str(x).strip()
    if s=="" or s.lower()=="none": return None
    return Decimal(s)

def _to_iso(dt):
    if dt is None: return None
    if isinstance(dt, (int,float)):
        return datetime.fromtimestamp(dt, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    s = str(dt).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            d = datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
            return d.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            pass
    try:
        d = datetime.fromisoformat(s.replace("Z","").replace(" ","T"))
        return d.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return s

def lambda_handler(event, context):
    try:
        body = event.get("body") or "[]"
        items = json.loads(body)
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list):
            return _resp(400, {"ok": False, "msg": "El cuerpo debe ser JSON array u objeto"})

        table = dynamodb.Table(TABLE_NAME)
        count = 0
        with table.batch_writer(overwrite_by_pkeys=["TransaccionID"]) as bw:
            for r in items:
                item = {
                    "TransaccionID": (str(r.get("TransaccionID") or "").strip()),
                    "ClienteID": _to_int(r.get("ClienteID")),
                    "FechaHoraISO": _to_iso(r.get("FechaHora")),
                    "ComercioID": _to_int(r.get("ComercioID")),
                    "Usuario": (r.get("Usuario") or "").strip(),
                    "IdTransaccionOrigen": (r.get("IdTransaccionOrigen") or "").strip(),
                    "CodigoAutorizacion": (r.get("CodigoAutorizacion") or "").strip(),
                    "EstadoOperacion": (r.get("EstadoOperacion") or "").strip(),
                    "Canal": (r.get("Canal") or "").strip(),
                    "CodigoMoneda": (r.get("CodigoMoneda") or "").strip(),
                    "MontoBruto": _to_dec(r.get("MontoBruto")),
                    "TasaCambio": _to_dec(r.get("TasaCambio")),
                    "Monto": _to_dec(r.get("Monto")),
                    "IndicadorAprobada": _to_bool(r.get("IndicadorAprobada")),
                    "LatenciaAutorizacionMs": _to_int(r.get("LatenciaAutorizacionMs")),
                    "Fraude": _to_bool(r.get("Fraude")),
                }
                if not item["TransaccionID"] or item["ClienteID"] is None or not item["FechaHoraISO"] or item["ComercioID"] is None:
                    continue
                item = {k:v for k,v in item.items() if v not in ("", None)}
                bw.put_item(Item=item)
                count += 1
        return _resp(200, {"ok": True, "insertados": count})
    except Exception as e:
        return _resp(500, {"ok": False, "msg": str(e)})
