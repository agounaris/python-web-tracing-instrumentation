# Generating Metrics from Traces: Capabilities \& Benefits

### Overview

Modern observability platforms now enable extracting meaningful, actionable metrics directly from distributed trace data. This approach allows teams to leverage a single source of telemetry for both deep diagnostics and operational monitoring, significantly reducing operational complexity.

### How Metrics Are Generated from Traces

- **Automated Processing**: Trace data, composed of spans as requests flow through your system, is automatically analyzed by components like Grafana Tempo's metrics-generator or similar tools.
- **RED Metrics Extraction**: Key metrics—such as Rate (number of requests), Error (error counts), and Duration (latency figures)—are derived from trace spans by aggregating across service names, operations, and other dimensions.
- **Service Graphs**: Relationship and dependency information between services are mapped by tracking parent-child spans, enabling visualization of service-to-service communication and bottlenecks.
- **Real-time Integration with Metrics Systems**: Once extracted, these metrics can be sent to time-series databases like Prometheus, making them available for dashboards, alerting, and long-term analysis.


### Key Metrics Derived from Traces

| Metric Type | How It's Derived | Example Use-cases |
| :-- | :-- | :-- |
| Request Rate | Counting relevant spans | Traffic monitoring, scaling decisions |
| Error Rate | Status/error code in spans | Alerting on failures |
| Duration/Latency | Span timing and histograms | Detecting slow endpoints, SLO tracking |
| Service Graphs | Structure of span relationships | Dependency visualization, bottleneck ID |

### Benefits

- **Efficiency**: Eliminates the need for separate instrumentation. If your application emits complete trace data, you can generate all necessary operational metrics with no extra cost or complexity.
- **Lower Ingest and Storage Costs**: Extracted metrics are smaller and cheaper to store/query compared to raw traces.
- **Unified Observability**: Metric extraction enables sophisticated alerting and SLO tracking—powered by real end-to-end performance data—in addition to root-cause analysis using the underlying traces.
- **Out-of-the-Box Coverage**: Systems without dedicated metric instrumentation can gain immediate, useful visibility as soon as tracing is in place.


# Practical Example OpenTelemetry Traces: Getting Started Tutorial

## Prerequisites — Introduction to Grafana Alloy

**Grafana Alloy** is a robust open-source observability tool designed for collecting, processing, and forwarding telemetry signals—including traces, metrics, and logs. It's deeply **Kubernetes-native**, making it a natural fit for modern distributed applications that need unified observability across microservices.

Grafana Alloy helps you:

- **Integrate OpenTelemetry easily** for collecting and sending trace data.
- **Forward all signals** (logs, traces, metrics) to backends such as Grafana, Prometheus, or Loki.


### Kubernetes Install Example

```bash
# Step 1: Add Grafana charts
helm repo add grafana https://grafana.github.io/helm-charts

# Step 2: Update charts
helm repo update

# Step 3: Create an observability namespace
kubectl create namespace observability

# Step 4: Install Alloy with Helm (customize as needed)
helm install alloy grafana/alloy -n observability --set random.value=demo

# Step 5: Check Alloy pods
kubectl get pods -n observability

# Step 6: Apply sample Alloy configuration
kubectl apply -f alloy-config.yaml -n observability
```


## Get Started with Python and OpenTelemetry SDK

Traces in OpenTelemetry **do not replace transaction logs**—they provide a distributed context for a request, capturing how it propagates and where performance bottlenecks occur.

### Installation

```bash
pip install opentelemetry-api
pip install opentelemetry-sdk
pip install opentelemetry-exporter-otlp
pip install opentelemetry-distro
```


### Basic Example

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, OTLPSpanExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# This span shows a single operation, not every loop iteration
with tracer.start_as_current_span("sample-operation"):
    print("Tracing this operation!")
```

### Instrumenting Applications Automatically
OpenTelemetry provides an instrumentation tool that can instrument Python applications with little to no code changes.

Starting a Python Process with opentelemetry-instrument:

Use the opentelemetry-instrument command to automatically apply instrumentation to your Python application.

```bash
opentelemetry-instrument \
  --traces_exporter otlp \
  --service_name my-python-service \
  python my_script.py
```

* --traces_exporter otlp specifies that traces will be exported via the OTLP protocol.
* --service_name assigns a logical service name for trace grouping.
* Replace my_script.py with your entrypoint script.

Environment variables (such as collector endpoints) can also be set to control the destination and behavior.


## Best Practices

- **Traces vs. Logs:** Traces are not your transaction logs; they are tools for understanding the flow, dependencies, bottlenecks, and failure points of a request as it moves across services. Rely on structured logs for detailed audit trails.
- **Metric Extraction:** Use metrics derived from traces to monitor error rates, latency, and SLOs. This is much more efficient (and cost-effective) than extracting such insights directly from traces at scale. Tools like **Prometheus** are built for high-performance metric aggregation and are the industry standard for these use cases.

```python
# Example: Export error rates as Prometheus metrics, not from every trace
```

- **Failed Spans for Exceptions:** When an exception occurs, always **mark the span as failed**. This improves diagnosability by highlighting exactly where failures are happening.

```python
try:
    with tracer.start_as_current_span("app-action") as span:
        do_something()
except Exception as ex:
    span.record_exception(ex)
    **span.set_status(Status(StatusCode.ERROR, str(ex)))**
    raise
```

- **Avoid High Cardinality:** Never add user IDs, IP addresses, or other unique identifiers as attributes to your spans. This creates an explosion of unique time-series or labels, harming performance and queryability.
- **Spans in Loops:** Create one span for a batch or logical unit, not individual iterations of large loops.

```python
with tracer.start_as_current_span("batch-processing"):
    for item in items:
        process(item)  # Don't start a new span for each iteration
```

- **Environment Variables:** Configure exporters, endpoints, service names, and resource attributes using environment variables for easy reconfiguration and portability.

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="http://alloy:4317"
export OTEL_RESOURCE_ATTRIBUTES="service.name=my-service"
export OTEL_SERVICE_NAME="my-service"
```


## Visualizing and Interpreting Data

**Visualizing Trace Data** allows you to:

- **Diagnose Performance Bottlenecks:** Follow requests as they propagate through services, instantly identifying latency sources.
- **Error Analysis:** By highlighting failed spans, you can quickly pinpoint and troubleshoot failing operations.
- **Dependency Mapping:** Visualize service-to-service communication and detect which systems are most interdependent.


### Using Trace-Derived Metrics

- **Objective Tracking:** Use metrics from traces to feed dashboards or alerts monitoring SLOs (Service Level Objectives), error rates, and latency distributions.
- **Prometheus Integration:** Export summarized metrics (success, failures, durations) from traces to Prometheus for scalable analysis—it's far more efficient than aggregating directly from raw traces.
- **Practical Example:** Build Grafana panels using Prometheus metrics from your trace pipeline to monitor, alert, and drill down into outliers or failures, focusing on changes to error rates or latency for specific endpoints or services.

**Summary of Inferences:**

- Traces track causality; logs provide state. Always use the right tool for the job.
- Use failed spans systematically to enable instant filtering for failures in trace explorers.
- Let **metrics** power your real-time objectives dashboards and alerting, keeping tracing focused on root-cause analysis and deep dives.

This ensures **high observability, actionable performance insights, and maintainable infrastructure**