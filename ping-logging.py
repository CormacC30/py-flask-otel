import flask
from flask import Flask, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

@app.route('/ping', methods=['GET'])
def ping():
    app.logger.info('Ping Pong')
    return jsonify({"message": "pong"}), 200

if __name__ == '__main__':
    app.logger.info('Server is starting....')
    app.run(debug=True, host='0.0.0.0', port=5000)

