# IOT-Temp-Dashboard
IoT Temperature Monitoring Dashboard is a real-time web application that tracks and visualizes temperature data from IoT devices. The system allows users to monitor live temperature updates, view historical temperature trends, and control devices. Data is logged in CSV files, and email alerts are sent when thresholds are exceeded.


---



## Features

- **Real-time updates**: Temperature data is displayed in real-time using WebSocket connections.
- **Temperature trends**: View temperature data trends for the last 30 days.
- **Device control**: Option to control devices (turn on/off, set temperature thresholds).
- **Email alerts**: Send email notifications when the temperature exceeds a specified threshold.
- **CSV logging**: All temperature data is logged to a CSV file for future analysis.

## Technologies Used

- **Flask**: Python web framework for building the application.
- **Flask-SocketIO**: For real-time communication and updates between the server and clients.
- **Matplotlib**: For generating temperature trend charts.
- **HTML/CSS**: For the frontend user interface.
- **Python**: Backend logic, data handling, and device control.
- **JavaScript**: Real-time WebSocket integration in the frontend.

## Setup Instructions

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/iot-temperature-dashboard.git
   cd iot-temperature-dashboard
