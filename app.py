from flask import Flask, jsonify
import script  # importa seu script.py

app = Flask(__name__)

@app.route("/run", methods=["GET"])
def run():
    try:
        log = script.registrar_ponto()
        return jsonify({"status": "success", "log": log}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
