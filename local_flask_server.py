from flask import Flask, Response, request, jsonify
import subprocess
import os
import time
import json
import psutil
import threading
import ast
import sys
import threading
import re
import chess, chess.engine, chess.polyglot
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
ENGINES_DIR = "c:\\engines\\"

# Global variables
global current_ips
global current_clients
global last_stream
global recent_fens

last_connection_time = {}

# Global variables
current_ips = {}
current_clients = 0
last_connection_time = {}
last_stream = time.time()
recent_fens = []

book_file = 'c:\\python\\ccrlchallenger\\Perfect2017.bin'
book_file = "c:\\python\\ccrlchallenger\\codekiddy.bin"
#book_file = "c:\\python\\ccrlchallenger\\lichess-201301-202405-caissa-wins.bin"


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

def conditional_delete_line(input_string):
    """
    Deletes the last printed line if the input string contains 'delete_this'.
    """
    if "true" in input_string:
        sys.stdout.write("\033[F")  # Move the cursor up one line
        sys.stdout.write("\033[K")  # Clear the line
        sys.stdout.write("\033[F")  # Move the cursor up one line
        sys.stdout.write("\033[K")  # Clear the line
        sys.stdout.flush()

def stream_engine_output(fen, engine_name, time_limit, ip, book_moves):
    global current_ips
    global current_clients
    global last_stream
    last_stream = time.time()
    start_time = time.time()
    f = open('engine_list_complete.txt', 'r', encoding='utf-8')
    lines = f.readlines()
    f.close()
    response = ''
    exe_file = ''
    for line in lines:
        info = ast.literal_eval(f"{line}")
        name = info[0]
        if name != engine_name: continue
        exe_file = info[4].replace("\\","/" )
        break

    if time_limit > 5:
        time_limit = 5
    if time_limit < 0:
        time_limit = 0

    # Handle book moves
    full_move_count = int(fen.split(" ")[5])
    if book_moves > 0 and book_moves >= full_move_count:
        board = chess.Board(fen)
        opening_moves = []
        with chess.polyglot.open_reader(book_file) as reader:
            for entry in reader.find_all(board):
                if entry.weight >= 20 or len(opening_moves) < 3: opening_moves.append(entry.move)
        if len(opening_moves) == 0:
            move = None
        else:
            move = str(random.choice(opening_moves))
            yield f"data: {json.dumps({'best_move': move, 'book_move': True})}\n\n"
            return

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
    #engine_name = 'stockfish.exe'
    #engine_path = os.path.join(ENGINES_DIR, engine_name)
    exe_file = exe_file.replace("/","\\")
    engine_path = exe_file
    if not os.path.exists(engine_path):
        yield f"data: {json.dumps({'error': 'Engine not found ' + exe_file})}\n\n"
        return

    try:
        # Initialize the chess board from the FEN
        board = chess.Board(fen)

        # Set up the chess engine
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
                    new_score = 0
                    if score is not None:
                        if hasattr(score.relative, 'mate'):
                            new_score = "Mate in " + str(score.relative.mate())
                        if hasattr(score.relative, 'cp'):
                            new_score = str(score.relative.cp)
                    score = new_score
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

global last_streamed_engine
last_streamed_engine = {}
global colour
colour = {}
@app.route("/stream_engine", methods=["GET"])
def stream_engine():
    global last_streamed_engine
    fen = request.args.get("fen")
    engine_name = request.args.get("engine_name")
    time_limit = float(request.args.get("move_time", 5))
    book_moves = request.args.get("book_moves", 0)
    print("Streaming engine:", engine_name)
    if book_moves == 'None': book_moves = 0
    if book_moves:
        book_moves = int(book_moves)
    ip = request.remote_addr
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    last_streamed_engine[ip] = engine_name
    colour[ip] = fen.split(" ")[1].replace("w", "white").replace("b", "black")
    if not fen or not engine_name:
        return Response("data: {'error': 'FEN and engine_name are required'}\n\n", mimetype="text/event-stream")

    return Response(stream_engine_output(fen, engine_name, time_limit, ip, book_moves), mimetype="text/event-stream")


@app.route("/users", methods=["GET"])
def user_count():
    global current_clients
    global last_stream
    duration = time.time() - last_stream
    return Response(str(current_clients) + "," + str(int(duration)))

@app.route("/engine_list", methods=["GET"])
def engine_list():
    f = open('engine_list_complete.txt', 'r', encoding='utf-8')
    lines = f.readlines()
    f.close()
    response = ''
    for line in lines:
        info = ast.literal_eval(f"{line}")
        name = info[0]
        github_link = info[1]
        author = info[2]
        rating = info[3]
        exe_file = info[4]
        language = info[5]
        release_date = info[6]
        response += f'\'{name}\', \'{github_link}\', \'{author}\', \'{rating}\', \'{release_date}\'\n'
    return response

@app.route("/engine_info", methods=["GET"])
def engine_info():
    global logo_urls
    engine_name = request.args.get('engine_name')
    f = open('engine_list_complete.txt', 'r', encoding='utf-8')
    lines = f.readlines()
    f.close()
    response = ''
    for line in lines:
        info = ast.literal_eval(f"{line}")
        name = info[0]
        if name != engine_name: continue
        github_link = info[1]
        author = info[2]
        rating = info[3]
        exe_file = info[4]
        exe_file = exe_file.replace("\\","/" )
        match = re.match(r'^([A-Za-z]+)', name)
        short_name =  match.group(1) if match else None
        engine_logo = 'None'
        if short_name in logo_urls:
            engine_logo = logo_urls[short_name]
            print(engine_logo)
        language = info[5]
        release_date = info[6]
        return f'\'{name}\', \'{github_link}\', \'{author}\', \'{rating}\', \'{exe_file}\', \'{engine_logo.strip()}\', \'{language}\', \'{release_date}\'\n'
    return 'None'
    pass

@app.route("/new_fen_and_legal_moves", methods=["GET"])
def new_fen_and_legal_moves():
    global recent_fens
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    fen = request.args.get("fen")
    move = request.args.get("move")
    board = chess.Board(fen)
    # Assume recent_fens is a list of tuples (fen, ip, timestamp)
    i = 0
    found = False
    new_recent_fens = []  # New list to store the valid fens
    current_ip = ip
    orig_fen = fen
    for fen in recent_fens:
        age = time.time() - fen[3]  # Calculate age of the current entry
        if ip not in last_streamed_engine: continue
        if ip not in colour: continue
        match_title = 'Human Player vs ' + last_streamed_engine[ip]
        if colour[ip] == "white":
            match_title = last_streamed_engine[ip] + " vs Human Player"
        if fen[1] == current_ip:  # Matching current fen and IP
            found = True
            new_fen = (orig_fen, fen[1], match_title, time.time())  # Update with the new timestamp
            new_recent_fens.append(new_fen)  # Append to new list
        else:
            # If the fen is too old, we don't add it back
            if age <= 120:  # Only keep the ones younger than 120 seconds
                new_recent_fens.append(fen)

        i += 1  # Increment the index for the next iteration
    recent_fens = list(new_recent_fens)
    if not found:
        if ip in last_streamed_engine: engine_name = last_streamed_engine[ip]
        if ip in last_streamed_engine and ip in colour:
            match_title = 'Human Player vs ' + engine_name
            if colour[ip] == "white":
                match_title = engine_name + " vs Human Player"
            recent_fens.append((orig_fen, ip, match_title, time.time()))
    print("Current games:", len(recent_fens))
    for entry in recent_fens:
        print(":::", entry)
    game_over = 'False'
    if board.can_claim_draw():
        game_over = 'Game is drawn.'
    if board.is_checkmate():
        if board.turn:
            game_over = 'Black wins by checkmate.'
        else:
            game_over = 'White wins by checkmate.'
    if game_over != 'False':
        sse_data = f"data: {json.dumps({'new_fen': fen, 'legal_moves': [], 'game_over': game_over})}\n\n"
        return Response(sse_data, mimetype="text/event-stream")
    if move != 'None': board.push_uci(move)
    legal_moves = board.legal_moves
    new_legal_moves = []
    new_legal_moves = []
    for legal_move in legal_moves:
        new_legal_moves.append(str(legal_move))
    new_fen = board.fen()
    game_over = 'False'
    king_pos = str(chess.square_name(board.king(board.turn)))
    if board.can_claim_draw():
        game_over = 'Game is drawn (claimable draw).'
    elif board.is_stalemate():
        game_over = 'Game is drawn by stalemate.'
    elif board.is_insufficient_material():
        game_over = 'Game is drawn due to insufficient material.'
    if board.is_checkmate():
        if board.turn:
            game_over = 'Black wins by checkmate.'
        else:
            game_over = 'White wins by checkmate.'
    if 'wins' not in game_over:
        king_pos = None
    sse_data = f"data: {json.dumps({'new_fen': new_fen, 'legal_moves': new_legal_moves, 'game_over': game_over, 'king_pos': king_pos})}\n\n"
    threading.Timer(0.01, conditional_delete_line, args=[str(request.args.get("delete_this"))]).start()
    return Response(sse_data, mimetype="text/event-stream")

    #    return Response(f"data: {{'new_fen': '{new_fen}', 'legal_moves': {new_legal_moves}}}")
    return

if __name__ == "__main__":
    global logo_urls
    logo_urls = {}
    f = open('logo_urls.txt','r',encoding='utf-8')
    lines = f.readlines()
    f.close()
    for line in lines:
        logo_urls[line.split("|")[0]] = line.split("|")[1]
    #global current_ips
    #global current_clients
    current_ips = {}
    current_clients = 0
    p = psutil.Process()  # Get current process

    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    app.run(host='0.0.0.0', port=8080, debug=True)