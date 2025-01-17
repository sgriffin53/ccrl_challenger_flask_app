from flask import Flask, Response, request
import subprocess
import os
import time
import json
import psutil
import threading
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
ENGINES_DIR = "c:\\engines\\"

# Global variables
global current_ips
global current_clients
last_connection_time = {}

# Global variables
current_ips = {}
current_clients = 0
last_connection_time = {}


def timeout_remove_client(ip, time_limit):
    """ Helper function to remove client from global count and IP count after 6 seconds """
    global current_ips
    global current_clients

    # Sleep for 6 seconds and then remove the client
    time.sleep(time_limit * 1.2)

    # Decrease global client count
    current_clients -= 1
    if current_clients < 0: current_clients = 0
    if current_ips.get(ip, 0) > 0:
        current_ips[ip] -= 1

    # Log the removal
    print(
        f"Client {ip} removed after 6-second timeout. Current clients: {current_clients}, IP count: {current_ips[ip]}")

    # Remove IP entry if no more connections
    if current_ips[ip] <= 0:
        del current_ips[ip]


def stream_engine_output(fen, engine_name, time_limit, ip):
    global current_ips
    global current_clients
    start_time = time.time()

    # Track time of last connection for each IP for reset after 15 seconds
    if ip in last_connection_time:
        time_diff = time.time() - last_connection_time[ip]
        if time_diff > 15:
            current_ips[ip] = 0  # Reset count if over 15 seconds

    # Update current client count
    current_clients += 1

    # If the IP has exceeded 3 concurrent connections, reject
    if ip not in current_ips:
        current_ips[ip] = 0
    if current_ips[ip] > 3:
        current_clients -= 1  # Decrease global client count if rejected
        yield f"data: {json.dumps({'error': 'Too many concurrent connections from your IP.<br><br>Try again soon.' + str(current_ips[ip])})}\n\n"
        return

    current_ips[ip] += 1  # Increment the concurrent connections for this IP

    # If there are too many clients globally, reject
    if current_clients > 75:
        current_clients -= 1  # Decrease global client count if rejected
        current_ips[ip] -= 1  # Decrease this IP's count if rejected
        yield f"data: {json.dumps({'error': 'Server over capacity. <br><br>Try again soon.'})}\n\n"
        return

    # Start the timeout thread to automatically remove client after 6 seconds
    threading.Thread(target=timeout_remove_client, args=(ip,time_limit,), daemon=True).start()

    # Example engine path and setup
    engine_name = 'raven1.30.exe'
    engine_path = os.path.join(ENGINES_DIR, engine_name)

    if not os.path.exists(engine_path):
        yield f"data: {json.dumps({'error': 'Engine not found'})}\n\n"
        return

    try:
        process = subprocess.Popen(
            [engine_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line-buffered
        )

        # Sending UCI commands to the engine
        process.stdin.write("uci\n")
        process.stdin.write("isready\n")
        process.stdin.write("setoption name Hash value 32")
        process.stdin.flush()
        process.stdin.write(f"position fen {fen}\n")
        process.stdin.flush()
        process.stdin.write(f"go movetime {time_limit * 1000}\n")
        process.stdin.flush()

        # Stream engine output and update server load in real-time
        while True:
            line = process.stdout.readline().strip()
            if "bestmove" in line:
                best_move = line.split()[1]
                yield f"data: {json.dumps({'best_move': best_move, 'current_clients': current_clients})}\n\n"
                break

            if "info" in line:
                parts = line.split()
                try:
                    best_move = parts[parts.index("pv") + 1] if "pv" in parts else None
                    nodes = parts[parts.index("nodes") + 1] if "nodes" in parts else None
                    depth = parts[parts.index("depth") + 1] if "depth" in parts else None
                    nps = parts[parts.index("nps") + 1] if "nps" in parts else None
                    score = parts[parts.index("cp") + 1] if "cp" in parts else None
                    yield f"data: {json.dumps({'current_best': best_move, 'nodes': nodes, 'depth': depth, 'nps': nps, 'score': score, 'current_clients': current_clients})}\n\n"
                except ValueError:
                    continue

        process.stdin.write("quit\n")
        process.stdin.flush()
        process.terminate()

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e), 'current_clients': current_clients})}\n\n"

    # Update last connection time
    last_connection_time[ip] = time.time()

@app.route("/stream_engine", methods=["GET"])
def stream_engine():
    fen = request.args.get("fen")
    engine_name = request.args.get("engine_name")
    time_limit = int(request.args.get("time_limit", 30))
    ip = request.remote_addr
    if not fen or not engine_name:
        return Response("data: {'error': 'FEN and engine_name are required'}\n\n", mimetype="text/event-stream")

    return Response(stream_engine_output(fen, engine_name, time_limit, ip), mimetype="text/event-stream")

if __name__ == "__main__":
    #global current_ips
    #global current_clients
    current_ips = {}
    current_clients = 0
    p = psutil.Process()  # Get current process

    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    app.run(host='0.0.0.0', port=8080, debug=True)