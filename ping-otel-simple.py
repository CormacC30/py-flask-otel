# same basic webserver as ping.py, but with OpenTelemetry instrumentation for tracing

import time
import atexit
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode

from flask import Flask, jsonify

resource = Resource.create(attributes={
    SERVICE_NAME: "py-flask-otel-service"
})

exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",  # Default OTLP gRPC endpoint
    insecure=True
)

tracerProvider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(exporter)
tracerProvider.add_span_processor(processor)

trace.set_tracer_provider(tracerProvider)

def shutdown_tracer():
    tracerProvider.shutdown()

atexit.register(shutdown_tracer)


app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    tracer = trace.get_tracer("http-server")
    
    with tracer.start_as_current_span("handleRequest") as span:
        time.sleep(1)
        span.set_status(Status(StatusCode.OK, "Status 200"))
        return jsonify({"message": "pong"}), 200
    
if __name__ == '__main__':
    print("Starting http-server...")  
    app.run(debug=True, host='0.0.0.0', port=8090)

