from flask import Flask, request, jsonify, make_response
import os

app = Flask(__name__)

# Simulare valori senzor
sensor_values = {
    "1": 23.5,
    "2": 45.2,
    "3": 67.8
}

CONFIG_DIR = 'sensor_configs'
os.makedirs(CONFIG_DIR, exist_ok=True)

####
# Tests using curl:
# GET: curl.http://127.0.0.1:5000/sensor/1
# POST: curl -X POST http://127.0.0.1:5000/sensor/1
# PUT: -X PUT -H "Content-Type: text/plain" -d "version=2.5" http://127.0.0.1:5000/sensor/1/1_config.txt
####

@app.route('/sensor/<sensor_id>', methods=['GET'])
def read_sensor(sensor_id):
    value = sensor_values.get(sensor_id)
    if value is None:
        return make_response(jsonify({"error": "sensor id does not exist"}), 404)
    
    return jsonify({"sensor_id": sensor_id, "value": value})

@app.route('/sensor/<sensor_id>', methods=['POST'])
def create_config(sensor_id):
    config_path = os.path.join(CONFIG_DIR, f"{sensor_id}_config.txt")
    if os.path.exists(config_path):
        return make_response(jsonify({
            "error": "config file already exists"
        }), 409)
    
    default_content = "version=1.0\n"
    with open(config_path, 'w') as f:
        f.write(default_content)

    return jsonify({"message": f"created config file: {config_path}"}), 201

@app.route('/sensor/<sensor_id>/<config_file>', methods=['PUT'])
def update_config(sensor_id, config_file):
    config_path = os.path.join(CONFIG_DIR, config_file)
    if not os.path.exists(config_path):
        return make_response(jsonify({
            "error": "config file does not exist"
        }), 409)
    
    content = request.data.decode('utf-8')
    if not content:
        return make_response(jsonify({
            "error": "file content can not be empty"
        }), 400)
    
    with open(config_path, 'w') as f:
        f.write(content)
    
    return jsonify({"message": f"config file {config_file} updated successfully"})

if __name__ == '__main__':
    app.run(debug=True)