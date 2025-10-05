#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, argparse
from decimal import Decimal
from datetime import datetime, timezone
import boto3
import pandas as pd

def to_decimal(x):
    if x is None:
        return None
    s = str(x).strip()
    if s == "" or s.lower() == "none":
        return None
    return Decimal(s)

def to_bool(x):
    if x is None:
        return None
    s = str(x).strip().lower()
    return s in ("1", "true", "t", "yes", "y", "si", "sí")

def to_int(x):
    if x is None or str(x).strip() == "":
        return None
    return int(str(x).strip())

def to_iso(dt):
    if isinstance(dt, datetime):
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if dt is None:
        return None
    s = str(dt).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            d = datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
            return d.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            pass
    try:
        d = datetime.fromisoformat(s.replace("Z", "").replace(" ", "T"))
        return d.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return s

def cleanse_none(d):
    return {k:v for k,v in d.items() if v is not None and v != ""}

def main():
    ap = argparse.ArgumentParser(description="Sube transacciones a DynamoDB (TablaTransaccion) desde CSV o Excel.")
    ap.add_argument("--input", required=True, help="Archivo .csv o .xlsx (hoja con columnas mínimas)")
    ap.add_argument("--sheet", default=None, help="Nombre/índice de la hoja si es Excel")
    ap.add_argument("--table", default=os.environ.get("TABLA_TRANSACCION", "TablaTransaccion"), help="Tabla DynamoDB destino")
    ap.add_argument("--region", default=os.environ.get("AWS_REGION", "us-east-1"), help="Región AWS")
    args = ap.parse_args()

    ext = os.path.splitext(args.input)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(args.input, dtype=str, keep_default_na=False, na_filter=False)
    else:
        df = pd.read_excel(args.input, sheet_name=args.sheet or 0, dtype=str)

    required = ["TransaccionID", "ClienteID", "FechaHora", "ComercioID"]
    for col in required:
        if col not in df.columns:
            raise SystemExit(f"Falta columna obligatoria: {col}")

    ddb = boto3.resource("dynamodb", region_name=args.region)
    table = ddb.Table(args.table)
    table.load()

    count = 0
    with table.batch_writer(overwrite_by_pkeys=["TransaccionID"]) as bw:
        for _, r in df.iterrows():
            item = {
                "TransaccionID": str(r.get("TransaccionID")).strip(),
                "ClienteID": to_int(r.get("ClienteID")),
                "FechaHoraISO": to_iso(r.get("FechaHora")),
                "ComercioID": to_int(r.get("ComercioID")),
                "IdTransaccionOrigen": str(r.get("IdTransaccionOrigen")).strip() if "IdTransaccionOrigen" in df.columns else None,
                "CodigoAutorizacion": str(r.get("CodigoAutorizacion")).strip() if "CodigoAutorizacion" in df.columns else None,
                "EstadoOperacion": str(r.get("EstadoOperacion")).strip() if "EstadoOperacion" in df.columns else None,
                "Canal": str(r.get("Canal")).strip() if "Canal" in df.columns else None,
                "CodigoMoneda": str(r.get("CodigoMoneda")).strip() if "CodigoMoneda" in df.columns else None,
                "MontoBruto": to_decimal(r.get("MontoBruto")) if "MontoBruto" in df.columns else None,
                "TasaCambio": to_decimal(r.get("TasaCambio")) if "TasaCambio" in df.columns else None,
                "Monto": to_decimal(r.get("Monto")) if "Monto" in df.columns else None,
                "IndicadorAprobada": to_bool(r.get("IndicadorAprobada")) if "IndicadorAprobada" in df.columns else None,
                "LatenciaAutorizacionMs": to_int(r.get("LatenciaAutorizacionMs")) if "LatenciaAutorizacionMs" in df.columns else None,
                "Fraude": to_bool(r.get("Fraude")) if "Fraude" in df.columns else None,
            }
            item = cleanse_none(item)
            if not item.get("TransaccionID") or item.get("ClienteID") is None or not item.get("FechaHoraISO") or item.get("ComercioID") is None:
                print(f"[WARN] Registro inválido, se omite: {item}")
                continue
            bw.put_item(Item=item)
            count += 1

    print(f"[OK] Cargadas {count} transacciones a {args.table} (región {args.region})")

if __name__ == "__main__":
    main()
