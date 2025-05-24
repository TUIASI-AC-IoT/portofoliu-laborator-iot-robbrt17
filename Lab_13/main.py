from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, unset_jwt_cookies, get_jwt
from datetime import timedelta

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret" 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

users = {
    "user1": {"passwd": "parola1", "role": "admin"},
    "user2": {"passwd": "parola2", "role": "owner"},
    "user3": {"passwd": "parolaX", "role": "owner"},
    "user4": {"passwd": "guest", "role": "guest"}
}

# curl -X POST -H "Content-Type: application/json" -d '{"username": "user1", "password": "parola1"}' http://localhost:5000/auth
# {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODA4NzUzMywianRpIjoiZjYyMmRkZjAtOGM0Ni00ZTczLTg4NjctNTg2OTY3MTZhNTlkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXIxIiwibmJmIjoxNzQ4MDg3NTMzLCJjc3JmIjoiZmNkZGI0MTUtYjNjMC00MGY3LTkxM2YtN2Q2M2E3MTdhZDM3IiwiZXhwIjoxNzQ4MDkxMTMzLCJyb2xlIjoiYWRtaW4ifQ.WYkVajqowVd0D9djTjsQ8ou-ff-ZENf3FGcBp4l3OlA"}

@app.route("/auth", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = users.get(username)

    if not user or user["passwd"] != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username, additional_claims={"role": user["role"]})
    return jsonify(access_token=access_token), 200

# curl -X GET -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODA4NzkxNywianRpIjoiMTQ0ZGY5YzAtN2QzNC00NGYwLWFhYTctZTA5ZmNiOTA0MmUxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXIyIiwibmJmIjoxNzQ4MDg3OTE3LCJjc3JmIjoiNDlkZGZjZDEtMjMyYi00ZDk3LWFiOGEtODYzYmZlYjMwY2JjIiwiZXhwIjoxNzQ4MDkxNTE3LCJyb2xlIjoib3duZXIifQ.2c5nEG0d0hITIS0v7hVFlLvhXjBRKYXwjzNjMO8g0CE" http://localhost:5000/auth/jwtStore
# {"role":"owner"}
@app.route("/auth/jwtStore", methods=["GET"])
@jwt_required()
def verify_token():
    claims = get_jwt()
    user_role = claims.get("role")
    if user_role:
        return jsonify({"role": user_role}), 200
    return jsonify({"msg": "Token not found or invalid"}), 404

# curl -X DELETE -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODA4NzkxNywianRpIjoiMTQ0ZGY5YzAtN2QzNC00NGYwLWFhYTctZTA5ZmNiOTA0MmUxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXIyIiwibmJmIjoxNzQ4MDg3OTE3LCJjc3JmIjoiNDlkZGZjZDEtMjMyYi00ZDk3LWFiOGEtODYzYmZlYjMwY2JjIiwiZXhwIjoxNzQ4MDkxNTE3LCJyb2xlIjoib3duZXIifQ.2c5nEG0d0hITIS0v7hVFlLvhXjBRKYXwjzNjMO8g0CE" http://localhost:5000/auth/jwtStore
# {"msg":"Logout successful"}
@app.route("/auth/jwtStore", methods=["DELETE"])
def logout():
    response = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(response)
    return response

# curl -X GET -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODA4NzUzMywianRpIjoiZjYyMmRkZjAtOGM0Ni00ZTczLTg4NjctNTg2OTY3MTZhNTlkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXIxIiwibmJmIjoxNzQ4MDg3NTMzLCJjc3JmIjoiZmNkZGI0MTUtYjNjMC00MGY3LTkxM2YtN2Q2M2E3MTdhZDM3IiwiZXhwIjoxNzQ4MDkxMTMzLCJyb2xlIjoiYWRtaW4ifQ.WYkVajqowVd0D9djTjsQ8ou-ff-ZENf3FGcBp4l3OlA" http://localhost:5000/sensor/data
# {"data":"some_sensor_data","msg":"Sensor data retrieved successfully"}
@app.route("/sensor/data", methods=["GET"])
@jwt_required()
def get_sensor_data():
    claims = get_jwt()
    user_role = claims.get("role")

    if user_role in ["owner", "admin"]:
        return jsonify({"msg": "Sensor data retrieved successfully", "data": "some_sensor_data"}), 200
    else:
        return jsonify({"msg": "Unauthorized: Insufficient role to read sensor data"}), 403

# curl -X POST -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODA4NzUzMywianRpIjoiZjYyMmRkZjAtOGM0Ni00ZTczLTg4NjctNTg2OTY3MTZhNTlkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXIxIiwibmJmIjoxNzQ4MDg3NTMzLCJjc3JmIjoiZmNkZGI0MTUtYjNjMC00MGY3LTkxM2YtN2Q2M2E3MTdhZDM3IiwiZXhwIjoxNzQ4MDkxMTMzLCJyb2xlIjoiYWRtaW4ifQ.WYkVajqowVd0D9djTjsQ8ou-ff-ZENf3FGcBp4l3OlA" http://localhost:5000/sensor/config
# {"msg":"Sensor configuration updated successfully"}
#
# In cazul in care incearca altcineva in afara de admin sa faca udate la sensor config 
# curl -X POST -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODA4NzkxNywianRpIjoiMTQ0ZGY5YzAtN2QzNC00NGYwLWFhYTctZTA5ZmNiOTA0MmUxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXIyIiwibmJmIjoxNzQ4MDg3OTE3LCJjc3JmIjoiNDlkZGZjZDEtMjMyYi00ZDk3LWFiOGEtODYzYmZlYjMwY2JjIiwiZXhwIjoxNzQ4MDkxNTE3LCJyb2xlIjoib3duZXIifQ.2c5nEG0d0hITIS0v7hVFlLvhXjBRKYXwjzNjMO8g0CE" http://localhost:5000/sensor/config
# {"msg":"Unauthorized: Insufficient role to update sensor configuration"}
@app.route("/sensor/config", methods=["POST", "PUT"])
@jwt_required()
def update_sensor_config():
    claims = get_jwt()
    user_role = claims.get("role")

    if user_role == "admin":
        return jsonify({"msg": "Sensor configuration updated successfully"}), 200
    else:
        return jsonify({"msg": "Unauthorized: Insufficient role to update sensor configuration"}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)