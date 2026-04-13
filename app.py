from flask import Flask, render_template, jsonify
from mqtt_processor import sensor_data, start_processor
import threading

app = Flask(__name__)

# Start MQTT processor in background thread
def run_processor():
    start_processor()

processor_thread = threading.Thread(target=run_processor, daemon=True)
processor_thread.start()

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/data")
def get_data():
    # Returns latest sensor data as JSON
    return jsonify({
        "temperature": sensor_data["temperature"],
        "motion": sensor_data["motion"],
        "alerts_count": len(sensor_data["alerts_log"]),
        "alerts_log": sensor_data["alerts_log"][-5:]  # Last 5 alerts
    })

if __name__ == "__main__":
    print("[FLASK] Starting IoT Dashboard at http://localhost:5000")
    app.run(debug=False, port=5000)