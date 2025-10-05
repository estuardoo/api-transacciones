
# api-transacciones (completo)

API Serverless (AWS Lambda + API Gateway + DynamoDB) para gestionar y consultar transacciones y comercios.

## Endpoints

### GET
- **Por ID de Transacción**  
  `GET /transacciones/buscar-por-id?TransaccionID=...`

- **Por ID de Cliente** (ordenado por fecha desc)  
  `GET /transacciones/buscar-por-cliente?ClienteID=...`

- **Por ID de Cliente + Rango de Fechas** (ordenado por fecha desc)  
  `GET /transacciones/buscar-por-cliente-fechas?ClienteID=...&desde=YYYY-MM-DDTHH:MM:SSZ&hasta=YYYY-MM-DDTHH:MM:SSZ`  

- **Por ID de Comercio** (ordenado por fecha desc)  
  `GET /transacciones/buscar-por-comercio?ComercioID=...`

### POST (importación masiva)
- **Cargar Comercios** (JSON array)  
  `POST /import/comercios`

- **Cargar Transacciones** (JSON array)  
  `POST /import/transacciones`

> Todos los endpoints devuelven `{"ok": true/false, ...}` y habilitan CORS.

---

## Tablas DynamoDB

- **TablaComercio**  
  - PK: `ComercioID` (Number)  
  - Billing: **PAY_PER_REQUEST** (on-demand)

- **TablaTransaccion**  
  - PK: `TransaccionID` (String)  
  - GSI: `GSI_Cliente_Fecha` → HASH `ClienteID` (Number), RANGE `FechaHoraISO` (String)  
  - GSI: `GSI_Comercio_Fecha` → HASH `ComercioID` (Number), RANGE `FechaHoraISO` (String)  
  - Billing: **PAY_PER_REQUEST** (on-demand)

---

## Despliegue

### Opción A: con scripts incluidos
```bash
# Setup en EC2 (una sola vez)
./setup_all.sh

# Deploy (imprime endpoints al final)
./deploy.sh us-east-1 dev
```

### Opción B: manual con Serverless
```bash
npm i -g serverless
sls deploy --region us-east-1 --stage dev --verbose
sls info --region us-east-1 --stage dev
```

La URL base tendrá la forma:
```
https://<restApiId>.execute-api.us-east-1.amazonaws.com/dev
```

---

## Pruebas rápidas (curl)

```bash
BASE="https://<restApiId>.execute-api.us-east-1.amazonaws.com/dev"

curl -s -X POST "$BASE/import/comercios" -H "Content-Type: application/json" -d '[{"ComercioID":10,"Nombre":"Tienda Sol","Estado":"Activo"}]' | jq

curl -s -X POST "$BASE/import/transacciones" -H "Content-Type: application/json" -d '[{"TransaccionID":"T-0001","ClienteID":100,"FechaHoraISO":"2025-10-04T20:00:00Z","ComercioID":10,"Monto":120.5}]' | jq

curl -s "$BASE/transacciones/buscar-por-id?TransaccionID=T-0001" | jq

curl -s "$BASE/transacciones/buscar-por-cliente?ClienteID=100" | jq

curl -s "$BASE/transacciones/buscar-por-cliente-fechas?ClienteID=100&desde=2025-10-01T00:00:00Z&hasta=2025-10-05T23:59:59Z" | jq

curl -s "$BASE/transacciones/buscar-por-comercio?ComercioID=10" | jq
```

---

## Carga de datos (alternativa desde archivos)

```bash
pip3 install --user boto3 pandas openpyxl

python3 subir_comercios.py --input comercios.xlsx --sheet TablaComercio --region us-east-1
python3 subir_transacciones.py --input transacciones.xlsx --sheet TablaTransaccion --region us-east-1
```

> El script convierte `FechaHora` al campo ISO `FechaHoraISO` para que los GSIs funcionen.

---

## Troubleshooting

- **No veo endpoints después del deploy**  
  - Verifica región/stage: `sls info --region us-east-1 --stage dev`
  - Lista APIs y rutas: `./deploy.sh` (usa jq si está instalado)

- **Query por fechas no devuelve datos**  
  - Asegúrate que `FechaHoraISO` esté en **ISO 8601** (`2025-10-01T00:00:00Z`).

- **Permisos IAM**  
  - `LabRole` debe permitir DynamoDB (`DescribeTable`, `GetItem`, `Query`, `BatchWriteItem`, `PutItem`).

---

## Notas

- DynamoDB en modo **on-demand** (PAY_PER_REQUEST).  
- CORS habilitado.  
- Incluye `deploy.sh` y `setup_all.sh` para despliegue automatizado.
