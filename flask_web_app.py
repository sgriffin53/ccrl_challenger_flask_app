from flask import Flask, Response, request, redirect
import subprocess
import os
import time
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/img/<path:filename>')
def redirect_to_external_img(filename):
    # Redirect to the external URL, preserving the filename
    return redirect(f'https://www.jimmyrustles.com/img/{filename}', code=302)


@app.route("/", methods=["GET"])
def main_page():
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    to_move = 'black'
   # fen = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'
   # to_move = 'White'
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
                    <div class="info-text" id="info-text"></div>
                </div>
                <br>
            </center>
            '''
    outtext += '''

            <!-- Initialize Chessboard after ensuring scripts are loaded -->
            <script>
                $(document).ready(function() {
                    // Ensure Chessboard is initialized after the DOM is ready
                    var config = {
                    '''
    outtext += f'''
                        draggable: true,        // Allow piece dragging
                        position: '{fen}',      // Start position for pieces
                        orientation: '{to_move}'    // Show correct orientation
}};

                    var board = Chessboard('myBoard', config); // Initialize the chessboard
                }});
            </script>
                '''
    outtext += f'''
            
            <script>
                var whiteSquareGrey = '#a9a9a9'
                var blackSquareGrey = '#696969'
                var whiteSquareGreen = '#00d900'
                var blackSquareGreen = '#009900'
                const fen = "{fen}"; // Example FEN
                const engineName = "stockfish"; // Replace with your engine name
                const timeLimit = 5; // 5 seconds
                '''
    outtext += '''
                function getEngineMove() {
                    document.getElementById('info-text').innerHTML = "Getting engine move."
                    const eventSource = new EventSource(`https://tapir-bold-personally.ngrok-free.app/stream_engine?fen=${encodeURIComponent(fen)}&engine_name=${engineName}&time_limit=${timeLimit}`);
            
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
                            server_load = Math.round(data.current_clients * (100 / 75))
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
                        }
                    };
                    eventSource.onerror = (err) => {
                        console.error("Error receiving events", err);
                        eventSource.close();
                    };
                
                }
                function removeGreySquares () {
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
                getEngineMove()
            </script>
        </body>
        </html>'''
    return outtext

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)