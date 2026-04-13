import paho.mqtt.client as mqtt
import json
import datetime

# MQTT Broker settings
BROKER = "localhost"
PORT = 1883

# Topics to subscribe
TEMP_TOPIC = "iot/sensors/temperature"
MOTION_TOPIC = "iot/sensors/motion"

# Thresholds for alert system
TEMP_HIGH_THRESHOLD = 40.0   # Alert if temperature exceeds this
TEMP_LOW_THRESHOLD = 18.0    # Alert if temperature drops below this

# Shared data store (used by Flask dashboard)
sensor_data = {
    "temperature": {
        "device": "Sensor-A",
        "value": 0,
        "unit": "Celsius",
        "timestamp": "-",
        "alert": False,
        "alert_message": ""
    },
    "motion": {
        "device": "Sensor-C",
        "detected": False,
        "timestamp": "-",
        "alert": False
    },
    "alerts_log": []
}

def check_temperature_alert(value, timestamp):
    if value > TEMP_HIGH_THRESHOLD:
        msg = f"HIGH TEMP ALERT: {value}°C exceeds {TEMP_HIGH_THRESHOLD}°C at {timestamp}"
        sensor_data["alerts_log"].append({"type": "danger", "message": msg, "time": timestamp})
        print(f"[ALERT] {msg}")
        return True, msg
    elif value < TEMP_LOW_THRESHOLD:
        msg = f"LOW TEMP ALERT: {value}°C below {TEMP_LOW_THRESHOLD}°C at {timestamp}"
        sensor_data["alerts_log"].append({"type": "warning", "message": msg, "time": timestamp})
        print(f"[ALERT] {msg}")
        return True, msg
    return False, ""

def check_motion_alert(detected, timestamp):
    if detected:
        msg = f"MOTION DETECTED at {timestamp}"
        sensor_data["alerts_log"].append({"type": "warning", "message": msg, "time": timestamp})
        print(f"[ALERT] {msg}")
        return True
    return False

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[PROCESSOR] Connected to MQTT broker")
        client.subscribe(TEMP_TOPIC)
        client.subscribe(MOTION_TOPIC)
        print(f"[PROCESSOR] Subscribed to: {TEMP_TOPIC}")
        print(f"[PROCESSOR] Subscribed to: {MOTION_TOPIC}")
    else:
        print(f"[PROCESSOR] Connection failed: {reason_code}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode())

    if topic == TEMP_TOPIC:
        value = payload["value"]
        timestamp = payload["timestamp"]
        alert, alert_msg = check_temperature_alert(value, timestamp)

        sensor_data["temperature"].update({
            "device": payload["device"],
            "value": value,
            "unit": payload["unit"],
            "timestamp": timestamp,
            "alert": alert,
            "alert_message": alert_msg
        })
        print(f"[DATA] Temperature: {value}°C from {payload['device']}")

    elif topic == MOTION_TOPIC:
        detected = payload["detected"]
        timestamp = payload["timestamp"]
        alert = check_motion_alert(detected, timestamp)

        sensor_data["motion"].update({
            "device": payload["device"],
            "detected": detected,
            "timestamp": timestamp,
            "alert": alert
        })
        print(f"[DATA] Motion: {'DETECTED' if detected else 'None'} from {payload['device']}")

# Create MQTT client
processor_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
processor_client.on_connect = on_connect
processor_client.on_message = on_message

def start_processor():
    print("[PROCESSOR] Starting MQTT Data Processor...")
    processor_client.connect(BROKER, PORT, 60)
    processor_client.loop_start()

if __name__ == "__main__":
    start_processor()
    print("[PROCESSOR] Listening for sensor data. Press Ctrl+C to stop.\n")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n[PROCESSOR] Stopped.")
        processor_client.loop_stop()
        processor_client.disconnect()