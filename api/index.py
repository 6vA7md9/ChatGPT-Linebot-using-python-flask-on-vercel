import time
from datetime import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from mcstatus import JavaServer
import threading
from flask import Flask, send_file

app = Flask(__name__)

def get_player_count(server_address):
    try:
        server = JavaServer.lookup(server_address)
        status = server.status()
        return status.players.online
    except Exception as e:
        print(f"Error: {e}")
        return None

def log_player_count(server_address, log_file):
    player_count = get_player_count(server_address)
    if player_count is not None:
        with open(log_file, 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp},{player_count}\n")
            print(f"Logged: {player_count} players online at {timestamp}")

def plot_graph(log_file):
    timestamps = []
    player_counts = []
    with open(log_file, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            timestamps.append(parts[0])
            player_counts.append(int(parts[1]))

    fig = make_subplots(rows=1, cols=1)

    fig.add_trace(
        go.Scatter(x=timestamps, y=player_counts, mode='lines+markers', name='Player Count'),
        row=1, col=1
    )

    fig.update_layout(
        title='Player Count Over Time',
        xaxis=dict(title='Timestamp'),
        yaxis=dict(title='Player Count'),
        showlegend=True,
        autosize=True
    )

    fig.write_html("templates/player_count_graph.html")  # Save the HTML file in the 'templates' directory

def run_script():
    server_address = "play.blocksmc.com:25565"  # Minecraft server address
    log_file = "player_count.log"  # File to log player counts
    interval_hours = 1  # Interval in hours to check the player count

    while True:
        log_player_count(server_address, log_file)
        plot_graph(log_file)
        time.sleep(interval_hours * 3600)  # Convert hours to seconds

@app.route('/')
def index():
    return send_file('templates/player_count_graph.html')

if __name__ == "__main__":
    threading.Thread(target=run_script).start()
    app.run(host='0.0.0.0', port=8080)
