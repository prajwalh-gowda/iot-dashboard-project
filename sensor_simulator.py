import paho.mqtt.client as mqtt
import json
import time
import random
import datetime

# MQTT Broker settings
BROKER = "localhost"
PORT = 1883

# MQTT Topics
TEMP_TOPIC = "iot/sensors/temperature"
MOTION_TOPIC = "iot/sensors/motion"

# Fix deprecation warning
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def generate_temperature():
    # Simulates temperature between 18 and 50 degrees Celsius
    return round(random.uniform(18.0, 50.0), 2)

def generate_motion():
    # Simulates motion detection (True = motion detected)
    return random.choice([True, False, False])  # 33% chance of motion

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[MQTT] Connected to broker successfully")
    else:
        print(f"[MQTT] Connection failed with code {reason_code}")

client.on_connect = on_connect

print("[SIM] Starting Virtual IoT Sensor Simulator...")
print("[SIM] Connecting to MQTT broker at localhost:1883")
client.connect(BROKER, PORT, 60)
client.loop_start()

time.sleep(1)  # Wait for connection

print("[SIM] Publishing sensor data every 2 seconds. Press Ctrl+C to stop.\n")

try:
    while True:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Temperature sensor payload
        temp_value = generate_temperature()
        temp_payload = json.dumps({
            "device": "Sensor-A",
            "type": "temperature",
            "value": temp_value,
            "unit": "Celsius",
            "timestamp": timestamp
        })

        # Motion sensor payload
        motion_value = generate_motion()
        motion_payload = json.dumps({
            "device": "Sensor-C",
            "type": "motion",
            "detected": motion_value,
            "timestamp": timestamp
        })

        # Publish to MQTT topics
        client.publish(TEMP_TOPIC, temp_payload)
        client.publish(MOTION_TOPIC, motion_payload)

        print(f"[{timestamp}] Temp: {temp_value}°C | Motion: {'DETECTED' if motion_value else 'None'}")

        time.sleep(2)

except KeyboardInterrupt:
    print("\n[SIM] Simulator stopped.")
    client.loop_stop()
    client.disconnect()