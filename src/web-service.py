import os
import random
import time

import requests
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.trace.status import StatusCode

app = FastAPI()
tracer = trace.get_tracer(__name__)

dependency_url = os.getenv("UPSTREAM", None) 
service_name = os.getenv("OTEL_SERVICE_NAME", None) 

@app.get("/")
async def root():
    with tracer.start_as_current_span(f"root-request-{service_name}"):
        return {"message": "Hello, FastAPI with OpenTelemetry!"}

@app.get("/process")
async def custom_route():
    with tracer.start_as_current_span(f"custom-proccessing-{service_name}") as span:
        if dependency_url:
            try:
                if random.random() <= 0.02:  # 2% chance
                    raise requests.RequestException()
                response = requests.get(dependency_url)
                if response.status_code == 200:
                    span.add_event("ok-upstream-request")
                    span.set_status(StatusCode.OK, str(e))
                    return response.json()
                else:
                    print(f"Request failed with status code: {response.status_code}")
                    raise requests.RequestException()
            except requests.RequestException as e:
                span.record_exception(e)  # Attach exception event to the span
                span.set_attribute("upstream-url", dependency_url)
                span.add_event("failed-upstream-request")
                span.set_status(StatusCode.ERROR, str(e))  # Mark span as failed
                print(f"An error occurred: {e}")
        else:
            # Generate a random delay between 0.1 and 2.0 seconds
            delay = random.uniform(0.1, 2.0)
            time.sleep(delay)
            return {"message": f"Processed for {delay:.3f} seconds"}
