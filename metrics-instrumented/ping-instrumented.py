import flask
import prometheus_client
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

# Create Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Duration', ['method', 'endpoint'])

@app.route('/ping', methods=['GET'])
def ping():
    REQUEST_COUNT.labels(method='GET', endpoint='/ping').inc()
    return jsonify({"message": "pong"}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; version=0.0.4'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8090)