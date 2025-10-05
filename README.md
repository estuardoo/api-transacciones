
# api-transacciones (completo)

Incluye:
- GET `/transacciones/buscar-por-id?TransaccionID=...`
- GET `/transacciones/buscar-por-cliente?ClienteID=...`
- POST `/import/comercios` (lote JSON)
- POST `/import/transacciones` (lote JSON)
- Scripts locales: `subir_comercios.py` y `subir_transacciones.py`

## Despliegue
npm i -g serverless
sls deploy --region us-east-1 --stage dev --verbose
sls info --region us-east-1 --stage dev

## Pruebas
BASE="https://<restApiId>.execute-api.us-east-1.amazonaws.com/dev"
curl -s -X POST "$BASE/import/comercios" -H "Content-Type: application/json" -d '[{"ComercioID":10,"Nombre":"Tienda Sol","Estado":"Activo"}]'
curl -s -X POST "$BASE/import/transacciones" -H "Content-Type: application/json" -d '[{"TransaccionID":"T-0001","ClienteID":100,"FechaHoraISO":"2025-10-04T20:00:00Z","ComercioID":10,"Monto":120.5}]'
curl -s "$BASE/transacciones/buscar-por-cliente?ClienteID=100"
curl -s "$BASE/transacciones/buscar-por-id?TransaccionID=T-0001"
