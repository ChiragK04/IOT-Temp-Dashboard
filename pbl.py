from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import threading
import time
import random
import requests
import csv
import os
import io
import base64
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt



# Flask  setup
app = Flask(__name__)
socketio = SocketIO(app)

# Path for logs
CSV_FILE = "logs.csv"
logs = []

#  CSV file 
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "IP", "Device ID", "Temperature"])

# Flask route to log device data
@app.route('/device', methods=['POST'])
def log_device():
    ip = request.remote_addr
    data = request.get_json()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        'timestamp': timestamp,
        'ip': ip,
        'device_id': data.get("device_id"),
        'temperature': data.get("temperature")
    }
    logs.append(entry)

    # Save to CSV 
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, entry['device_id'], entry['temperature']])

    # Emit the new temperature data over WebSocket
    socketio.emit('temperature_update', {'device_id': entry['device_id'], 'temperature': entry['temperature'], 'timestamp': entry['timestamp']})
    socketio.emit('log_update', {'device_id': entry['device_id'], 'timestamp': entry['timestamp'], 'temperature': entry['temperature'], 'ip': ip})

    print(f"[SERVER] {timestamp} | {ip} | {entry['device_id']} | {entry['temperature']}°C")
    return jsonify({"status": "success"}), 200

# Generate live temperature chart
def generate_chart():
    data_by_device = {}

    # Read latest 100 entries from CSV
    with open(CSV_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)[-100:]

    for row in rows:
        timestamp, ip, device_id, temp = row
        if device_id not in data_by_device:
            data_by_device[device_id] = {'timestamps': [], 'temps': []}
        data_by_device[device_id]['timestamps'].append(timestamp[-8:])  # time only
        data_by_device[device_id]['temps'].append(float(temp))

    # Plot the data
    fig, ax = plt.subplots()
    for device_id, data in data_by_device.items():
        ax.plot(data['timestamps'], data['temps'], label=device_id, marker='o')

    ax.set_title("Temperature Chart")
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Flask route to display the dashboard
@app.route('/')
def dashboard():
    chart = generate_chart()

    html = """
    <html><head><title>IoT Dashboard</title>
    <meta http-equiv="refresh" content="2">
    <style>
    body { font-family: sans-serif; padding: 20px; }
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid #ccc; padding: 6px; text-align: center; }
    th { background: #f0f0f0; }
    </style></head><body>
    <h2>Live IoT Temperature Dashboard</h2>
    <img src="data:image/png;base64,{{chart}}" style="max-width: 90%; height: auto; margin: 20px auto; display: block;"><br><br>
    <h3>Last 10 Logs</h3>
    <table>
    <tr><th>Timestamp</th><th>Device ID</th><th>Temperature</th><th>IP</th></tr>
    {% for log in logs %}
    <tr>
      <td>{{log.timestamp}}</td>
      <td>{{log.device_id}}</td>
      <td>{{log.temperature}}</td>
      <td>{{log.ip}}</td>
    </tr>
    {% endfor %}
    </table>

    <h3>Real-time Temperature Updates</h3>
    <ul id="temp-updates">
    </ul>

    <script src="https://cdn.socket.io/4.1.3/socket.io.min.js"></script>
    <script type="text/javascript">
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    
    socket.on('temperature_update', function(data) {
        var newUpdate = document.createElement('li');
        newUpdate.innerHTML = "Device: " + data.device_id + " | Temp: " + data.temperature + "°C | Timestamp: " + data.timestamp;
        document.getElementById("temp-updates").appendChild(newUpdate);
    });

    socket.on('log_update', function(data) {
        var logTable = document.querySelector("table");
        var newRow = logTable.insertRow(1);  // Insert at the top
        newRow.insertCell(0).innerText = data.timestamp;
        newRow.insertCell(1).innerText = data.device_id;
        newRow.insertCell(2).innerText = data.temperature;
        newRow.insertCell(3).innerText = data.ip;

        // Keep only the last 10 logs
        if (logTable.rows.length > 11) {  // 1 header row + 10 log rows
            logTable.deleteRow(11);  // Delete last row
        }
    });
    </script>
    </body></html>
    """

    recent_logs = logs[-10:]
    return render_template_string(html, logs=recent_logs, chart=chart)

# Flask server runner function
def run_flask_app():
    socketio.run(app, host='127.0.0.1', port=5000, debug=True, use_reloader=False)

# Simulate device temperature data for testing
def simulate_devices():
    time.sleep(3)
    device_ids = ["sensor_A", "sensor_B", "sensor_C"]
    for _ in range(30):
        device = random.choice(device_ids)
        temp = round(random.uniform(20, 35), 2)
        data = {
            "device_id": device,
            "temperature": temp
        }
        try:
            requests.post('http://127.0.0.1:5000/device', json=data)
        except Exception as e:
            print(f"[{device}] Failed: {e}")
        time.sleep(2)




   
   
    # Start Flask app in a separate thread
    threading.Thread(target=run_flask_app, daemon=True).start()

    root.mainloop()

# Starting Flask and simulate devices
if __name__ == '__main__':
    # Starting Flask server in background thread
    threading.Thread(target=run_flask_app, daemon=True).start()
    
    # Simulate devices generating data
    simulate_devices()

    