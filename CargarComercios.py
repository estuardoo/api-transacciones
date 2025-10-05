import os, json, boto3

TABLE_NAME = os.environ.get("TABLA_COMERCIO", "TablaComercio")
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
        with table.batch_writer(overwrite_by_pkeys=["ComercioID"]) as bw:
            for r in items:
                item = {
                    "ComercioID": _to_int(r.get("ComercioID")),
                    "Nombre": (r.get("Nombre") or "").strip(),
                    "RUC": (r.get("RUC") or "").strip(),
                    "ActividadEconomica": (r.get("ActividadEconomica") or "").strip(),
                    "Sector": (r.get("Sector") or "").strip(),
                    "Direccion": (r.get("Direccion") or "").strip(),
                    "Telefono": (r.get("Telefono") or "").strip(),
                    "Email": (r.get("Email") or "").strip(),
                    "Estado": (r.get("Estado") or "Activo").strip() or "Activo",
                }
                if item["ComercioID"] is None:
                    continue
                item = {k:v for k,v in item.items() if v not in ("", None)}
                bw.put_item(Item=item)
                count += 1
        return _resp(200, {"ok": True, "insertados": count})
    except Exception as e:
        return _resp(500, {"ok": False, "msg": str(e)})
