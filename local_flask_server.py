from flask import Flask, Response, request, jsonify
import subprocess
import os
import time
import json
import psutil
import threading
import chess, chess.engine
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
    """ Helper function to remove client from global count and IP count after it times out """
    global current_ips
    global current_clients

    # Sleep for 6 seconds and then remove the client
    time.sleep(time_limit * 1)

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
        yield f"data: {json.dumps({'error': 'Too many concurrent connections from your IP.<br><br>Try again soon.'})}\n\n"
        return

    current_ips[ip] += 1  # Increment the concurrent connections for this IP
    # Update last connection time
    last_connection_time[ip] = time.time()
    # If there are too many clients globally, reject
    if current_clients > 100:
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
        # Initialize the chess board from the FEN
        board = chess.Board(fen)

        # Set up the chess engine
        try:
            with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
                # Set the engine options
                engine.configure({"Hash": 32})  # Example engine option (adjust as needed)

                # Make the engine ready
                #engine.is_ready()

                # Get the best move for the current position within the specified time limit
                #result = engine.play(board, chess.engine.Limit(time=time_limit))

                # Get additional engine information (e.g., depth, nodes, score, etc.)
                pv = ''
                # Stream analysis as the engine processes the position
                with engine.analysis(board, chess.engine.Limit(time=time_limit)) as analysis:
                    for info in analysis:
                      #  print(info)
                        nodes = str(info.get("nodes", None))
                        if nodes == 'None': continue
                        depth = str(info.get("depth", None))
                        nps = str(info.get("nps", None))
                        score = info.get("score", None)
                        score = str(score.relative.cp)
                        bestmove = info.get("bestmove", None)
                      #  print(bestmove)
                        if info.get("pv", None) is not None: pv = str(info.get("pv", None)[0])
                        yield f"data: {json.dumps({'current_best': pv, 'nodes': nodes, 'depth': depth, 'nps': nps, 'score': score, 'current_clients': current_clients})}\n\n"
                      #  if bestmove:
                      #      yield f"data: {json.dumps({'best_move': str(bestmove), 'current_clients': current_clients})}\n\n"
                best_move = pv
                # Stream engine output and update server load
                yield f"data: {json.dumps({'best_move': best_move, 'current_clients': current_clients})}\n\n"
                engine.quit()
        except:
            with chess.engine.SimpleEngine.popen_xboard(engine_path) as engine:
                # Set the engine options
                engine.configure({"Hash": 32})  # Example engine option (adjust as needed)

                # Make the engine ready
                # engine.is_ready()

                # Get the best move for the current position within the specified time limit
                # result = engine.play(board, chess.engine.Limit(time=time_limit))

                # Get additional engine information (e.g., depth, nodes, score, etc.)
                pv = ''
                # Stream analysis as the engine processes the position
                with engine.analysis(board, chess.engine.Limit(time=time_limit)) as analysis:
                    for info in analysis:
                        #  print(info)
                        nodes = str(info.get("nodes", None))
                        if nodes == 'None': continue
                        depth = str(info.get("depth", None))
                        nps = str(info.get("nps", None))
                        score = info.get("score", None)
                        score = str(score.relative.cp)
                        bestmove = info.get("bestmove", None)
                        #  print(bestmove)
                        if info.get("pv", None) is not None: pv = str(info.get("pv", None)[0])
                        yield f"data: {json.dumps({'current_best': pv, 'nodes': nodes, 'depth': depth, 'nps': nps, 'score': score, 'current_clients': current_clients})}\n\n"
                    #  if bestmove:
                    #      yield f"data: {json.dumps({'best_move': str(bestmove), 'current_clients': current_clients})}\n\n"
                best_move = pv
                # Stream engine output and update server load
                yield f"data: {json.dumps({'best_move': best_move, 'current_clients': current_clients})}\n\n"
                engine.quit()

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e), 'current_clients': current_clients})}\n\n"


@app.route("/stream_engine", methods=["GET"])
def stream_engine():
    fen = request.args.get("fen")
    engine_name = request.args.get("engine_name")
    time_limit = float(request.args.get("move_time", 5))
    ip = request.remote_addr
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if not fen or not engine_name:
        return Response("data: {'error': 'FEN and engine_name are required'}\n\n", mimetype="text/event-stream")

    return Response(stream_engine_output(fen, engine_name, time_limit, ip), mimetype="text/event-stream")

@app.route("/new_fen_and_legal_moves", methods=["GET"])
def new_fen_and_legal_moves():
    fen = request.args.get("fen")
    move = request.args.get("move")
    board = chess.Board(fen)
    if move != 'None': board.push_uci(move)
    legal_moves = board.legal_moves
    new_legal_moves = []
    for legal_move in legal_moves:
        new_legal_moves.append(str(legal_move))
    new_fen = board.fen()
    game_over = 'False'
    if board.can_claim_draw():
        game_over = 'Game is drawn.'
    if board.is_checkmate():
        if board.turn:
            game_over = 'Black wins by checkmate.'
        else:
            game_over = 'White wins by checkmate.'
    sse_data = f"data: {json.dumps({'new_fen': new_fen, 'legal_moves': new_legal_moves, 'game_over': game_over})}\n\n"
    return Response(sse_data, mimetype="text/event-stream")

    #    return Response(f"data: {{'new_fen': '{new_fen}', 'legal_moves': {new_legal_moves}}}")
    return

if __name__ == "__main__":
    #global current_ips
    #global current_clients
    current_ips = {}
    current_clients = 0
    p = psutil.Process()  # Get current process

    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    app.run(host='0.0.0.0', port=8080, debug=True)