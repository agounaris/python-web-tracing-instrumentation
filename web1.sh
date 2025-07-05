OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
OTEL_SERVICE_NAME="web1" \
UPSTREAM="http://localhost:8002/process" \
PYTHONPATH=src \
opentelemetry-instrument uvicorn web-service:app --host 0.0.0.0 --port 8001
