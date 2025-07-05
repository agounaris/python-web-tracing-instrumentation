OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
OTEL_SERVICE_NAME="web2" \
UPSTREAM="http://localhost:8003/process" \
PYTHONPATH=src \
opentelemetry-instrument uvicorn web-service:app --host 0.0.0.0 --port 8002
