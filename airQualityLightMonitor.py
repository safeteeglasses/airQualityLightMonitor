from pms5003 import PMS5003
import paho.mqtt.client as mqtt
import json
import time

# MQTT Settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt/air_quality_light/set"  # Correct topic for your device

# Define the AQI conversion function
def pm25_to_aqi(pm25):
    breakpoints = [
        (0, 12, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500)
    ]
    
    for lower, upper, aqi_lower, aqi_upper in breakpoints:
        if lower <= pm25 <= upper:
            aqi = ((aqi_upper - aqi_lower) / (upper - lower)) * (pm25 - lower) + aqi_lower
            return round(aqi)
    
    return None

# Define the color mapping function
def aqi_to_color(aqi):
    if aqi <= 50:
        return (0, 255, 0)  # Green
    elif aqi <= 100:
        return (255, 255, 0)  # Yellow
    elif aqi <= 150:
        return (255, 165, 0)  # Orange
    elif aqi <= 200:
        return (255, 0, 0)  # Red
    elif aqi <= 300:
        return (128, 0, 128)  # Purple
    else:
        return (128, 0, 0)  # Maroon

# MQTT client setup
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def change_light_color(client, color):
    # Send RGB values as separate r, g, b keys
    message = {
        "state": "ON",
        "color": {
            "r": color[0],  # Red
            "g": color[1],  # Green
            "b": color[2]   # Blue
        }
    }
    
    # Print the message for debugging
    print(f"Sending message: {json.dumps(message)}")
    
    # Publish the message to the MQTT topic
    client.publish(MQTT_TOPIC, json.dumps(message))
    print(f"Light color changed to {color}")

# Read PM2.5 data from the EnviroPlus sensor
def read_pm25():
    sensor = PMS5003()
    data = sensor.read()
    
    pm25 = data.pm_ug_per_m3(2.5)  # Read PM2.5 value in µg/m³
    return pm25

# Main logic
def main():
    # Get PM2.5 data from EnviroPlus sensor
    pm25 = read_pm25()
    print(f"Current PM2.5 concentration: {pm25} µg/m³")
    
    # Calculate AQI based on PM2.5
    aqi = pm25_to_aqi(pm25)
    print(f"AQI for PM2.5 concentration {pm25} µg/m³: {aqi}")
    
    # Map AQI to color
    color = aqi_to_color(aqi)
    print(f"Color for AQI {aqi}: {color}")
    
    # MQTT client setup and connection
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    # Change light color based on AQI
    change_light_color(client, color)

    time.sleep(5)  # Let the light change color for 5 seconds
    client.loop_stop()

if __name__ == "__main__":
    main()
