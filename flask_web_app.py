import ast
from datetime import datetime
from flask import Flask, Response, request, redirect
import subprocess
import os
import time
import urllib
import json
import requests
import random
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

def get_footer():
    return ''

@app.route('/img/<path:filename>')
def redirect_to_external_img(filename):
    # Redirect to the external URL, preserving the filename
    return redirect(f'https://www.jimmyrustles.com/img/{filename}', code=302)

@app.route('/ccrlchallenger/img/<path:filename>')
def redirect_to_external_img_ccrl(filename):
    # Redirect to the external URL, preserving the filename
    return redirect(f'https://www.jimmyrustles.com/img/{filename}', code=302)

@app.route("/ccrlchallenger/playing_now", methods=["GET"])
def playing_now_page():
    outtext = '<html><body><div id="maindiv"></div>'
    outtext += '''
   <!-- Ensure CSS for the chessboard is linked -->
<link rel="stylesheet" href="https://www.jimmyrustles.com/css/chessboard-1.0.0.min.css">
<!-- jQuery (required for Chessboard.js) -->
<script src="https://code.jquery.com/jquery-3.5.1.min.js"
    integrity="sha384-ZvpUoO/+PpLXR1lu4jmpXWu80pZlYUAfxl5NsBMWOEPSjUn/6Z/hRTt8+pR6L4N2"
    crossorigin="anonymous"></script>
<!-- Chessboard.js script -->
<script src="https://www.jimmyrustles.com/js/chessboard-1.0.0.min.js"></script>

<style>
    /* Styling for the boards container */
    .boards-container {
        display: flex;
        flex-wrap: wrap; /* Allow wrapping for smaller screens */
        gap: 20px; /* Space between boards */
    }

    .board-wrapper {
        text-align: center; /* Centre-align the match titles */
    }

    .match-title {
        font-weight: bold;
        margin-bottom: 10px;
        font-size: 16px;
    }
</style>
    <style>
        /* Style for the container */
        .board-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px; /* Add spacing between the boards */
            padding: 20px;
        }

        /* Each game board wrapper */
        .board-wrapper {
            text-align: center;
            width: 500px; /* Set consistent width for each wrapper */
        }

        .board-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .board-div {
            margin: 0 auto; /* Centre the chessboard within the wrapper */
            width: 600px;
            height: 600px;
        }
    </style>
<center>
<h1>CCRL Challenger</h1>
<h2>Games in Progress</h2>
<script>
    // Function to handle the event stream and create/update chess boards
    function handleEventStream(eventSourceUrl) {
        const eventSource = new EventSource(eventSourceUrl);
        const container = document.getElementById('boardContainer');
        var keep_going = true;
        eventSource.onmessage = function (event) {
            const data = JSON.parse(event.data); // Parse incoming data
            console.log('Received event:', event.data);  // Log raw event data
                data.forEach(item => {
                    if (item.delete_user) {
                        // Handle board deletion
                        const boardWrapper = document.getElementById(item.delete_user);
                        console.log(`Received request to delete user_id: ${item.delete_user}`);
                        keep_going = false
                        if (boardWrapper) {
                            console.log('Board found:', boardWrapper); // Log if board is found
                            boardWrapper.remove(); // Remove the board wrapper from the DOM
                            console.log(`Board with user_id ${item.delete_user} deleted.`);
                        } else {
                            console.log(`No board found with user_id ${item.delete_user}`);
                        }
                    }
                });
            keep_going = true;
            if (keep_going) {
                // Handle board creation or updates
                data.forEach(item => {
                    const { fen, user_id, match_title, player_colour } = item;
                    if (match_title != undefined) {
                        // Check if a board with this user_id already exists
                        let boardWrapper = document.getElementById(user_id);
                
                        if (boardWrapper) {
                            // Update the existing board
                            const board = Chessboard(boardWrapper.querySelector('.board-div'));
                            board.position(fen); // Update the board with the new FEN
                            board.orientation(player_colour);
                            // Update the match title
                            const title = boardWrapper.querySelector('.match-title');
                            if (title) {
                                title.innerText = match_title; // Update the title text
                            }
                        } else {
                            // Create a new wrapper for the board if it doesn't exist
                            boardWrapper = document.createElement('div');
                            boardWrapper.id = user_id; // Assign the user_id as the id
                            boardWrapper.className = 'board-wrapper';
                
                            // Create and add the match title
                            const title = document.createElement('div');
                            title.className = 'match-title';
                            title.innerText = match_title;
                
                            // Create the chess board div
                            const boardDiv = document.createElement('div');
                            boardDiv.className = 'board-div';
                            boardDiv.style.width = '500px';
                
                            // Append title and board to the wrapper
                            boardWrapper.appendChild(title);
                            boardWrapper.appendChild(boardDiv);
                
                            // Add the wrapper to the container
                            document.querySelector('.boards-container').appendChild(boardWrapper);
                
                            // Initialise the chess board
                            const config = {
                                draggable: false,          // Allow piece dragging
                                position: fen,            // Start position for pieces
                                orientation: player_colour, // Use player_colour dynamically
                                onDrop: onDrop            // Define the onDrop callback function if needed
                            };
                
                            Chessboard(boardDiv, config); // Create the chessboard
                        }
                    }
                });
                
                // Delete boards for user_ids not in the data
                const currentBoards = document.querySelectorAll('.board-wrapper');
                const receivedUserIds = data.map(item => item.user_id);
                
                currentBoards.forEach(board => {
                    const boardUserId = board.id; // Get the user_id from the board's id
                    if (!receivedUserIds.includes(boardUserId)) {
                        board.remove(); // Remove the board if its user_id is not in the received data
                    }
                });
            }
        };
    }

    // Replace with your actual EventStream endpoint
    const eventStreamUrl = 'http://ccrl_tunnel.blindfoldchess.app/playing_now_sse';
    handleEventStream(eventStreamUrl);

    // Optional: Define the onDrop function (you can customise this as needed)
    function onDrop(source, target, piece, newPos, oldPos, orientation) {
        console.log(`Piece ${piece} moved from ${source} to ${target}`);
        // Add logic for when a piece is dropped, if required
    }
</script>

<body>
    <!-- Container to hold all the boards -->
    <div class="boards-container"></div>
    '''
    outtext += '<a href="/ccrlchallenger">Back to Engine List</a>'
    outtext += get_footer()
    return outtext

@app.route("/ccrlchallenger", methods=["GET"])
def main_page():
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    #fen = '1k6/8/8/8/8/4N2r/PPP5/1K6 b - - 0 1'
    #fen = 'rnbqkb1r/ppp3Pp/5n2/3pp3/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1'
    colour = request.args.get('colour')
    move_time = request.args.get('move_time')
    book_moves = request.args.get("book_moves")
    engine_name = request.args.get("engine")
    if colour == 'random':
        colour = random.choice(['white', 'black'])
    to_move = fen.split(" ")[1].replace("b","black").replace("w","white")
   # fen = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'
   # to_move = 'White'
    if request.args.get('newgame') is None and request.args.get('game_settings') is None:
        outtext = '<html>'
        outtext += '''<head><style>
                    /* General table styling */
                    table {
                      width: 600px; /* Fixed width for the table */
                      margin: 20px auto; /* Centers the table horizontally */
                      border-collapse: collapse;
                      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    }

                    /* Header styling */
                    th {
                      background-color: #4CAF50;
                      color: white;
                      padding: 12px 15px;
                      text-align: left;
                      font-weight: bold;
                      border-bottom: 2px solid #ddd;
                    }

                    /* Cell styling */
                    td {
                      padding: 12px 15px;
                      border-bottom: 1px solid #ddd;
                      text-align: left;
                    }

                    /* Zebra striping for rows */
                    tr:nth-child(even) {
                      background-color: #f9f9f9;
                    }

                    /* Hover effect for rows */
                    tr:hover {
                      background-color: #f1f1f1;
                    }

                    /* Borders and padding for a clean look */
                    td, th {
                      border: 1px solid #ddd;
                    }

                    /* Add rounded corners to the table */
                    table {
                      border-radius: 8px;
                      overflow: hidden;
                    }
            </style></head>
        '''
        try:
            page = requests.get("https://ccrl_tunnel.blindfoldchess.app/engine_list")
        except:
            return "<html><center>Unable to connect to server. Try again in a few minutes.</center>" + get_footer()
        data = page.text
        if "8CPU" not in page.text:
            return "<html><center>Unable to connect to server (invalid response). Tunnel is most likely temporarily unavailable. Try again in a few minutes.</center>" + get_footer()
        outtext += '<body>'
        outtext += '''<center>
                    <h1>CCRL Challenger</h1>
                    This site allows you to play against 118 different chess engines in your browser.<br>
                    All engines are open-source engines taken from the <a href="https://computerchess.org.uk/ccrl/404/">CCRL (Computer Chess Rating List)</a><br><br>
                    Limitations:<br>
                    <li> Engines have been tested but reliability cannot be guaranteed.
                    <li> A maximum of 5 seconds computer move time is allowed
                    <li> Engines are set to use a 32MB hash table
                    <li> Pawns will auto-promote to queens
                    <li> Threefold draws are not detected
                    '''
        page = requests.get("https://ccrl_tunnel.blindfoldchess.app/current_games")
        active_users = int(page.text)
        outtext += f'<br><br> {active_users} game(s) in progress.'
        outtext += '- <a href="/ccrlchallenger/playing_now">View Active Games</a><BR><br>'
        outtext += '<a href="/ccrlchallenger">Sort by rating</a><br><br>'
        outtext += '<a href="/ccrlchallenger?sort_by_date=True">Sort by release date</a>'
        outtext += '''
                    <h2>Select opponent</h2>
                    '''
        #return data
        lines = data.split("\n")
        # get random engine
        engine_list = []
        for line in lines:
            line = ast.literal_eval(f"[{line}]")
            if len(line) < 2: continue
            engine_list.append(line[0])
        random_engine = random.choice(engine_list)
        outtext += f"<a href=\"/ccrlchallenger?game_settings=True&engine={random_engine}\">Play Against Random Engine</a><br>"

        # Print sorted list
        #for line in sorted_lines:
         #   outtext += print(line) + "<BR>"
        outtext += "<table border=0><tr><td>Rank</td><td>Name</td><td>Rating</td><td>Release Date</td></tr>"
        all_engines = []
        for line in lines:
            #outtext += "<tr><td>" + str(split_data) + "</td></tr>"
            line = ast.literal_eval(f"[{line}]")
            if len(line) == 0: continue
            #print(type(line))
            #print(len(line))
            rank = line[3].split(" ")[0]
            rating = line[3].split(" ")[1].replace("(","").replace(")","")
            release_date = line[4]
            all_engines.append((line[0], line[3], release_date))
            #outtext += "<tr><td>" + rank + "</td><td><a href=\"/ccrlchallenger?game_settings=True&engine=" + line[0] + "\">" + line[0] + "</a></td><td>" + rating + "</td><td>" + release_date + "</td></tr>"
        if request.args.get("sort_by_date"):
            all_engines = sorted(all_engines, key=lambda x: datetime.strptime(x[2], '%Y-%m-%d'), reverse=True)
        for line in all_engines:
            rank = line[1].split(" ")[0]
            rating = line[1].split(" ")[1].replace("(", "").replace(")", "")
            release_date = line[2]
            outtext += "<tr><td>" + rank + "</td><td><a href=\"/ccrlchallenger?game_settings=True&engine=" + line[0] + "\">" + line[0] + "</a></td><td>" + rating + "</td><td>" + release_date + "</td></tr>"

        outtext += "</table>"
        outtext += get_footer()
        return outtext
    elif request.args.get('game_settings') is not None:
        outtext = '<html>'
        outtext += '''<head><style>
                        /* Optional: Style for greyed-out input */
                        input:disabled {
                            background-color: #e9e9e9;
                            color: #7d7d7d;
                            cursor: not-allowed;
                        }
                    </style>'''
        outtext += f'''<body><center>
                    <h1>CCRL Challenger</h1>
                    <h2>New Game</h2>
                    <form method="get">
                    <input type="hidden" name="newgame" value="True">
                    <input type="hidden" name="engine" value="{request.args.get('engine')}">
                    '''
        page = requests.get("https://ccrl_tunnel.blindfoldchess.app/engine_info?engine_name=" + engine_name)
        data = page.text
        data = ast.literal_eval(f'[{data}]')
        if data != 'None':
            if data[5] and data[5] != 'None':
                outtext += f'<img src="{data[5]}"><br><br>'
        outtext += f'''
                    Playing against: {request.args.get('engine')}
                    <br><br>
                    Play as: <input type="radio" name="colour" value="white" id="white">
                    <label for="white">White</label>
                    <input type="radio" name="colour" value="black" id="black">
                    <label for="black">Black</label>
                    <input type="radio" name="colour" value="random" id="random" checked>
                    <label for="random">Random</label>
                    <br><br>
                    Computer move time (seconds, 0.001 to 5): <input type="input" name="move_time" value="3" style="width:50px">
                    <br><br>
                    <input type="checkbox" name="use_book" id="use_book" checked onClick=bookCheckClick()><label for="use_book">Use opening book</label>
                    <br>
                    Max book moves: <input type="input" name="book_moves" id="book_moves" style="width:50px" value="5">
                    <br><br>
                    <input type="submit" action="startgame" value="Start Game" onClick=onSubmit()></form>
                    <br>
                    '''
        outtext += '<a href="/ccrlchallenger">Choose a new opponent</a><br><br>'
        outtext += '''
                    <script>
                    function bookCheckClick() {
                        if (document.getElementById('use_book').checked) {
                            document.getElementById('book_moves').disabled = false
                        }
                        else {
                            document.getElementById('book_moves').disabled = true
                        }
                    }
                    function onSubmit() {
                        if (!document.getElementById('use_book').checked) {
                            document.getElementById('book_moves') = 0
                        }
                    }
                    </script>
                    '''
        outtext += get_footer()
        return outtext
    else:
        outtext ='''<html><body>
                <link rel="canonical" href="https://www.jimmyrustles.com/ccrlchallenger" />
                <style>
                    /* General page styling */
                    @media screen and (max-width:767px) {
                       html, body {
                          	overflow: hidden;
                       }
                    }

                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                    }

                    /* Page content styling */
                    .content {
                        padding: 20px;
                    }

                    .section {
                        margin: 20px 0;
                    }

                    .section h2 {
                        margin-top: 0;
                    }
                    .container {
                        display: flex;
                        justify-content: center;
                        align-items: center; /* Align items vertically in the centre */
                        gap: 20px; /* Add space between the elements */
                    }

                    .info-text {
                        align-self: flex-start;
                        font-size: 16px;
                        padding: 10px;
                        text-align: left;
                    };

                </style>
                <!-- Ensure CSS for the chessboard is linked -->
                <link rel="stylesheet" href="https://www.jimmyrustles.com/css/chessboard-1.0.0.min.css">
                <!-- jQuery (required for Chessboard.js) -->
                <script src="https://code.jquery.com/jquery-3.5.1.min.js"
                    integrity="sha384-ZvpUoO/+PpLXR1lu4jmpXWu80pZlYUAfxl5NsBMWOEPSjUn/6Z/hRTt8+pR6L4N2"
                    crossorigin="anonymous"></script>
                <!-- Chessboard.js script -->
                <script src="https://www.jimmyrustles.com/js/chessboard-1.0.0.min.js"></script>
                <!-- Custom Chess logic (optional, make sure it's working) -->
                <script src="https://www.jimmyrustles.com/js/chess.ts"></script>
            '''
        outtext += f'''
                <center>
                    <h1>CCRL Challenger</h1>
                    <br>
                    '''
        #print(data)
        #engine_info = ast.literal_eval(f"[{data}]")
        #author = data[2]
        #outtext += "Author:" + author + "<br>"
        outtext += f'''
                    <!-- Chessboard container -->
                    <div class="container">
                        <div class="board-div" id="myBoard" style="width: 500px;"></div>
                        <div class="info-text" id="info-text" style="width: 200px"></div>
                    </div>
                    <br>

                '''
        page = requests.get("https://ccrl_tunnel.blindfoldchess.app/engine_info?engine_name=" + engine_name)
        data = page.text
        data = ast.literal_eval(f'[{data}]')
        if data != 'None':
            if data[5] and data[5] != 'None':
                outtext += f'<img src="{data[5]}"><br><br>'
            outtext += 'Engine: ' + data[0] + '<br>'
            outtext += 'Rank: ' + data[3] + '<br>'
            outtext += 'Release date: ' + data[7] + '<br>'
            outtext += 'Github: <a href="' + data[1] + '">' + data[1] + '</a><br>'
            outtext += 'Author: ' + data[2] + '<br>'
            outtext += 'Executable file: ' + data[4].split("/")[-1] + '<br>'
            outtext += 'Language: ' + data[6] + '<br><br>'

        outtext += '<a href="/ccrlchallenger?game_settings=True&engine=' + engine_name + '">Play again against ' + engine_name + '</a><br><br>'
        outtext += '<a href="/ccrlchallenger">Choose a new opponent</a><br><br>'
        outtext += '''
                </center>
                <!-- Initialize Chessboard after ensuring scripts are loaded -->
                <script>
                    var computer_turn = false
                    $(document).ready(function() {
                        // Ensure Chessboard is initialized after the DOM is ready
                        var config = {
                        '''
        outtext += f'''
                            draggable: true,        // Allow piece dragging
                            position: '{fen}',      // Start position for pieces
                            orientation: '{colour}',    // Show correct orientation
                            onDrop: onDrop
    }};

                        board = Chessboard('myBoard', config); // Initialize the chessboard


                    '''
        outtext += f'''
                    const to_move = "{to_move}";
                    const player_colour = "{colour}";
                    if (player_colour != to_move) {{
                        computer_turn = true
                        // engine has the first move

                        getEngineMove()
                    }}
                    else {{
                        handleMove('None')
                    }}
                    }})
                    '''
        outtext += f'''
                    var legal_moves;
                    var board;
                    var whiteSquareGrey = '#a9a9a9'
                    var blackSquareGrey = '#696969'
                    var whiteSquareGreen = '#00d900'
                    var blackSquareGreen = '#009900'
                    var SquareRed = '#ff0000'
                    fen = "{fen}";
                    book_moves = "{book_moves}"
                    const engineName = "{engine_name}"; // Replace with your engine name
                    const timeLimit = {move_time}; // 5 seconds
                    '''
        outtext += '''
                    function getEngineMove() {
                        computer_turn = true
                        document.getElementById('info-text').innerHTML = "Getting engine move."
                        const eventSource = new EventSource(`https://ccrl_tunnel.blindfoldchess.app/stream_engine?fen=${encodeURIComponent(fen)}&engine_name=${engineName}&move_time=${timeLimit}&book_moves=${book_moves}`);

                        eventSource.onmessage = (event) => {
                            const data = JSON.parse(event.data);
                            if (data && data.current_best && (!data.best_move || data.best_move === "")) {
                                document.getElementById('info-text').innerHTML = "";
                            }
                            if (data.depth && !document.getElementById('info-text').innerHTML.includes("Depth:")) {
                                document.getElementById('info-text').innerHTML += "Depth: " + data.depth + "<br>";
                            }
                            if (data.nodes) {
                                document.getElementById('info-text').innerHTML += "Nodes: " + data.nodes.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",") + "<br>";
                            }
                            if (data.nps) {
                                document.getElementById('info-text').innerHTML += "NPS: " + data.nps.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",") + "<br>";
                            }
                            if (data.score) {
                                score = data.score
                                if (!data.score.includes("Mate")) {
                                    score = (data.score / 100).toString()
                                    if (data.score >= 0) score = "+" + score
                                }
                                document.getElementById('info-text').innerHTML += "Score: " + score + "<br>";
                            }
                            if (data.current_best) {
                                //console.log(`Current Best Move: ${data.current_best}`);
                                document.getElementById('info-text').innerHTML += "Current best: " + data.current_best + "<br>";
                                removeGreySquares()
                                greySquare(data.current_best[0] + data.current_best[1])
                                greenSquare(data.current_best[2] + data.current_best[3])
                                // Optionally highlight the current best move on the board
                            }
                            if (data.current_clients >= 0 && data.current_best) {
                                //document.getElementById('info-text').innerHTML += "Current clients: " + data.current_clients
                                server_load = Math.round(data.current_clients * (100 / 100))
                                if (server_load < 0) server_load = 0
                                //document.getElementById('info-text').innerHTML += "Server load: " + server_load + "%"

                            }
                            if (data.error) {
                                document.getElementById('info-text').innerHTML = "Error: " + data.error
                                buttonString = '<input type="button" onClick=getEngineMove() value="Try again">'
                                document.getElementById('info-text').innerHTML += "<br><br>" + buttonString
                            }
                            if (data.book_move) {
                                document.getElementById('info-text').innerHTML = "Received move from book."
                            }
                            if (data.best_move) {
                                //console.log(`Final Best Move: ${data.best_move}`);
                                // Update the board with the final move
                                // board.move(data.best_move);
                                document.getElementById('info-text').innerHTML += "<br>Best move: " + data.best_move + "<br>";
                                eventSource.close();
                                computer_turn = false;
                                removeGreySquares()
                                //board.position('rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 0 1')
                                get_fen_and_legal_moves(data.best_move)
                                return
                            }
                        };
                        eventSource.onerror = (err) => {
                            console.error("Error receiving events", err);
                            eventSource.close();
                        };

                    }
                    function get_fen_and_legal_moves(move) {
                        return new Promise((resolve, reject) => {

                            const eventSource = new EventSource(`https://ccrl_tunnel.blindfoldchess.app/new_fen_and_legal_moves?fen=${encodeURIComponent(fen)}&move=${move}`);

                            eventSource.onmessage = (event) => {
                                try {
                                    const data = JSON.parse(event.data);
                                    if (data.new_fen) {
                                        board.position(data.new_fen);
                                        fen = data.new_fen
                                        legal_moves = data.legal_moves;
                                        if (data.game_over && data.game_over != 'False') {
                                            document.getElementById('info-text').innerHTML += "<br>" + data.game_over
                                        }
                                        if (data.king_pos) {
                                            redSquare(data.king_pos)
                                        }
                                    }
                                    resolve();
                                    eventSource.close();
                                } catch (error) {
                                    console.error("Error processing message from EventSource:", error);
                                    reject(error);  // Reject the promise in case of JSON parsing or processing error
                                    eventSource.close();
                                }
                            };

                            eventSource.onerror = (error) => {
                                console.error("EventSource encountered an error:", error);
                                eventSource.close();
                                reject(error); // Reject the promise on error
                            };
                        });
                    }

                    async function handleMove(move) {
                        try {
                            await get_fen_and_legal_moves(move); // Wait for this to complete
                            infotext = document.getElementById('info-text').innerHTML
                            if (move != 'None' && !infotext.includes('wins by') && !infotext.includes('draw')) getEngineMove(); // Trigger the next function after the promise resolves
                        } catch (error) {
                            console.error("Error handling move:", error);  // Catch and log any error that occurs in get_fen_and_legal_moves
                        }
                    }
                    function onDrop (source, target, piece, newPos, oldPos, orientation) {
                        if (computer_turn) {
                            return 'snapback';
                        }
                        let move = source + target; // Declare 'move' here
                        if (!legal_moves.includes(move)) {
                            const queenmove = move + "q";
                            if (!legal_moves.includes(queenmove)) {
                                return 'snapback';
                            } else {
                                move = queenmove; // Update 'move' with queenmove if valid
                            }
                        }
                        // legal move
                        handleMove(move); // Pass 'move' as an argument
                    }
                    function removeGreySquares () {
                        //alert("test")
                        $('#myBoard .square-55d63').css('background', '')
                    }

                    function greySquare (square) {
                        var $square = $('#myBoard .square-' + square);
                        var background = whiteSquareGrey;
                        if ($square.hasClass('black-3c85d')) {;
                            background = blackSquareGrey;
                        };

                        $square.css('background', background);
                    }
                    function greenSquare (square) {
                        var $square = $('#myBoard .square-' + square);
                        var background = whiteSquareGreen;
                        if ($square.hasClass('black-3c85d')) {;
                            background = blackSquareGreen;
                        };
                        $square.css('background', background);
                    }
                    function redSquare (square) {
                        var $square = $('#myBoard .square-' + square);
                        var background = SquareRed;
                        if ($square.hasClass('black-3c85d')) {;
                            background = SquareRed;
                        };
                        $square.css('background', background);
                    }
                </script>
                '''
        outtext += get_footer()

        return outtext

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)