
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, argparse
import boto3
import pandas as pd

def to_int(x):
    if x is None or str(x).strip() == "":
        return None
    return int(str(x).strip())

def cleanse_none(d):
    return {k:v for k,v in d.items() if v is not None and v != ""}

def main():
    ap = argparse.ArgumentParser(description="Sube comercios a DynamoDB (TablaComercio) desde CSV o Excel.")
    ap.add_argument("--input", required=True, help="Archivo .csv o .xlsx (hoja con columnas: ComercioID, ...)")
    ap.add_argument("--sheet", default=None, help="Nombre/índice de la hoja si es Excel")
    ap.add_argument("--table", default=os.environ.get("TABLA_COMERCIO", "TablaComercio"), help="Tabla DynamoDB destino")
    ap.add_argument("--region", default=os.environ.get("AWS_REGION", "us-east-1"), help="Región AWS")
    args = ap.parse_args()

    ext = os.path.splitext(args.input)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(args.input, dtype=str, keep_default_na=False, na_filter=False)
    else:
        df = pd.read_excel(args.input, sheet_name=args.sheet or 0, dtype=str)

    if "ComercioID" not in df.columns:
        raise SystemExit("Falta columna obligatoria: ComercioID")

    ddb = boto3.resource("dynamodb", region_name=args.region)
    table = ddb.Table(args.table)
    table.load()

    count = 0
    with table.batch_writer(overwrite_by_pkeys=["ComercioID"]) as bw:
        for _, r in df.iterrows():
            item = {
                "ComercioID": to_int(r.get("ComercioID")),
                "Nombre": r.get("Nombre", ""),
                "RUC": r.get("RUC", ""),
                "ActividadEconomica": r.get("ActividadEconomica", ""),
                "Sector": r.get("Sector", ""),
                "Direccion": r.get("Direccion", ""),
                "Telefono": r.get("Telefono", ""),
                "Email": r.get("Email", ""),
                "Estado": r.get("Estado") if r.get("Estado") else "Activo",
            }
            item = cleanse_none(item)
            if item.get("ComercioID") is None:
                print(f"[WARN] Comercio sin ID, se omite: {item}")
                continue
            bw.put_item(Item=item)
            count += 1

    print(f"[OK] Cargados {count} comercios a {args.table} (región {args.region})")

if __name__ == "__main__":
    main()
