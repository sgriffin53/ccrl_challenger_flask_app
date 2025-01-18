from flask import Flask, Response, request, redirect
import subprocess
import os
import time
import random
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/img/<path:filename>')
def redirect_to_external_img(filename):
    # Redirect to the external URL, preserving the filename
    return redirect(f'https://www.jimmyrustles.com/img/{filename}', code=302)


@app.route("/ccrlchallenge", methods=["GET"])
def main_page():
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    colour = request.args.get('colour')
    move_time = request.args.get('move_time')
    if colour == 'random':
        colour = random.choice(['white', 'black'])
    to_move = colour
   # fen = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'
   # to_move = 'White'
    if request.args.get('newgame') is None and request.args.get('game_settings') is None:
        outtext = '<html><body>'
        outtext += '''<center>
                    <h2>CCRL Challenger</h2>
                    Select opponent
                    <br><br>
                    <a href="/ccrlchallenge?game_settings=True&engine=Default">Default (1500)</a>
                    </body></html>
                    '''
        return outtext
    elif request.args.get('game_settings') is not None:
        outtext = '<html><body>'
        outtext += f'''<center>
                    <h1>CCRL Challenger</h1>                    
                    <h2>New Game</h2>
                    <form method="get">
                    <input type="hidden" name="newgame" value="True">
                    <input type="hidden" name="engine" value="{request.args.get('engine')}">
                    Playing against: {request.args.get('engine')}
                    <br><br>
                    Play as: <input type="radio" name="colour" value="white" id="white">
                    <label for="white">White</label>
                    <input type="radio" name="colour" value="black" id="black">
                    <label for="black">Black</label>
                    <input type="radio" name="colour" value="random" id="random" checked>
                    <label for="random">Random</label>
                    <br><br>
                    Computer move time (seconds, 0.1 to 5): <input type="input" name="move_time" value="5" style="width:50px">
                    <br><br>
                    <input type="submit" action="startgame" value="Start Game"></form>
                    <br><br>
                    '''
        return outtext
    else:
        outtext ='''<html><body>
                <link rel="canonical" href="https://www.jimmyrustles.com/ccrlchallenger" />
                <style>
                    /* General page styling */
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
                
                    .board-div {
                        /* Add styles specific to the board if needed */
                    }
                
                    .info-text {
                        align-self: flex-start;
                        font-size: 16px;
                        padding: 10px;
                        text-align: left;
                    }
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
                    <!-- Chessboard container -->
                    <div class="container">
                        <div class="board-div" id="myBoard" style="width: 500px;"></div>
                        <div class="info-text" id="info-text" style="width: 200px"></div>
                    </div>
                    <br>
                </center>
                '''
        outtext += '''
    
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
                            orientation: '{to_move}',    // Show correct orientation
                            onDrop: onDrop
    }};
    
                        board = Chessboard('myBoard', config); // Initialize the chessboard
                    
                    
                    '''
        outtext += f'''
                    const player_colour = "{to_move}";
                    if (player_colour == 'black') {{
                        computer_turn = true
                        // engine is white and has the first move
                        
                        //board.draggable(false)
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
                    fen = "{fen}"; // Example FEN
                    const engineName = "stockfish"; // Replace with your engine name
                    const timeLimit = {move_time}; // 5 seconds
                    '''
        outtext += '''
                    function getEngineMove() {
                        computer_turn = true
                        document.getElementById('info-text').innerHTML = "Getting engine move."
                        const eventSource = new EventSource(`https://tapir-bold-personally.ngrok-free.app/stream_engine?fen=${encodeURIComponent(fen)}&engine_name=${engineName}&move_time=${timeLimit}`);
                
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
                                score = (data.score / 100).toString()
                                if (data.score >= 0) score = "+" + score
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
                                document.getElementById('info-text').innerHTML += "Server load: " + server_load + "%"
                                
                            }
                            if (data.error) {
                                document.getElementById('info-text').innerHTML = "Error: " + data.error
                                buttonString = '<input type="button" onClick=getEngineMove() value="Try again">'
                                document.getElementById('info-text').innerHTML += "<br><br>" + buttonString
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
                            
                            const eventSource = new EventSource(`https://tapir-bold-personally.ngrok-free.app/new_fen_and_legal_moves?fen=${encodeURIComponent(fen)}&move=${move}`);
                    
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
                            if (move != 'None') getEngineMove(); // Trigger the next function after the promise resolves
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
                </script>
            </body>
            </html>'''
        return outtext

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)