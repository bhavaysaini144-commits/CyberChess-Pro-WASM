from flask import Flask, render_template_string

app = Flask(__name__)

# --- CYBERCHESS: COACH EDITION (WASM) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>CyberChess | AI Coach</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <style>
        :root { --bg: #121212; --panel: #1e1e1e; --text: #e0e0e0; --accent: #00e676; --danger: #ff1744; --highlight: #2979ff; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; height: 100vh; display: flex; flex-direction: column; }
        
        /* NAV */
        .nav { padding: 15px 25px; background: #000; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }
        .brand { font-weight: 800; letter-spacing: 1px; color: #fff; display: flex; align-items: center; gap: 10px; }
        
        /* LAYOUT */
        .layout { flex: 1; display: flex; height: calc(100vh - 70px); }
        .game-area { flex: 1; display: flex; justify-content: center; align-items: center; background: #181818; flex-direction: column; }
        .sidebar { width: 350px; background: var(--panel); border-left: 1px solid #333; display: flex; flex-direction: column; padding: 20px; gap: 15px; }
        
        /* COACH WIDGETS */
        .coach-box { background: #252525; padding: 15px; border-radius: 8px; border: 1px solid #333; text-align: center; }
        .eval-score { font-size: 32px; font-weight: bold; color: var(--accent); margin: 10px 0; }
        .eval-text { color: #888; font-size: 14px; }
        
        .progress-container { height: 6px; background: #333; border-radius: 3px; margin-top: 10px; overflow: hidden; }
        .progress-bar { height: 100%; background: var(--accent); width: 50%; transition: width 0.5s ease; }

        /* CONTROLS */
        .btn { width: 100%; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; transition: 0.2s; }
        .btn-hint { background: var(--highlight); color: white; }
        .btn-hint:hover { opacity: 0.9; }
        .btn-reset { background: #444; color: white; }

        /* HIGHLIGHTS */
        .highlight-hint { box-shadow: inset 0 0 3px 3px var(--highlight); }

        @media(max-width: 900px) { 
            .layout { flex-direction: column; } 
            .sidebar { width: auto; height: auto; order: 2; }
            .game-area { padding: 20px; }
            #myBoard { width: 90vw !important; }
        }
    </style>
</head>
<body>

<div class="nav">
    <div class="brand"><i class="fas fa-microchip"></i> CYBERCHESS <span style="font-size:10px; background:var(--accent); color:#000; padding:2px 6px; border-radius:4px;">PRO</span></div>
    <div style="font-size: 12px; color: #666;">System: Online</div>
</div>

<div class="layout">
    <div class="game-area">
        <div id="myBoard" style="width: 480px"></div>
    </div>
    
    <div class="sidebar">
        <!-- COACH PANEL -->
        <div class="coach-box">
            <div style="text-transform: uppercase; font-size: 12px; letter-spacing: 1px; color: #666;">Win Probability</div>
            <div class="eval-score" id="win-percent">50%</div>
            <div class="eval-text" id="coach-msg">Game Started. White to move.</div>
            <div class="progress-container">
                <div class="progress-bar" id="win-bar"></div>
            </div>
        </div>

        <!-- ACTIONS -->
        <div class="coach-box" style="text-align: left;">
            <div style="color:#fff; font-weight:bold; margin-bottom:5px;">Actions</div>
            <div id="status" style="color:#888; font-size:14px; margin-bottom:15px;">Waiting for player...</div>
            
            <button class="btn btn-hint" onclick="askCoach()"><i class="far fa-lightbulb"></i> AI Hint</button>
            <div style="display:flex; gap:10px;">
                <button class="btn btn-reset" onclick="undo()"><i class="fas fa-undo"></i> Undo</button>
                <button class="btn btn-reset" onclick="reset()"><i class="fas fa-sync"></i> Reset</button>
            </div>
        </div>
    </div>
</div>

<!-- LIBRARIES -->
<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
<script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>

<script>
    var board = null;
    var game = new Chess();
    var stockfish = new Worker('https://cdnjs.cloudflare.com/ajax/libs/stockfish.js/10.0.0/stockfish.js');
    var bestMove = null;

    // --- ENGINE LOGIC ---
    stockfish.onmessage = function(event) {
        var msg = event.data;
        
        // 1. Capture Best Move (For Hints)
        if(msg.indexOf("bestmove") > -1) {
            bestMove = msg.split(" ")[1]; 
            
            // If AI's turn, play the move
            if(game.turn() === 'b') {
                game.move(bestMove, {sloppy: true});
                board.position(game.fen());
                updateStatus();
            }
        }

        // 2. Capture Evaluation (For Coach)
        if (msg.indexOf("score cp") > -1) {
            var score = parseInt(msg.split("score cp ")[1].split(" ")[0]);
            if(game.turn() === 'b') score = -score; // Invert for black
            updateCoach(score);
        }
    };

    // --- THE COACH BRAIN (Sigmoid Function) ---
    function updateCoach(cp) {
        // Convert raw score to percentage
        var chance = 1 / (1 + Math.pow(10, -cp/400)); 
        var percent = Math.round(chance * 100);
        
        // Update UI
        var bar = document.getElementById('win-bar');
        var text = document.getElementById('win-percent');
        var msg = document.getElementById('coach-msg');

        text.innerText = percent + "%";
        bar.style.width = percent + "%";

        if(percent > 60) {
            msg.innerText = "White is dominating.";
            text.style.color = "#00e676"; 
        } else if (percent < 40) {
            msg.innerText = "Black has the lead.";
            text.style.color = "#ff1744"; 
        } else {
            msg.innerText = "The game is equal.";
            text.style.color = "#e0e0e0"; 
        }
    }

    function makeEngineMove() {
        if(game.game_over()) return;
        document.getElementById('status').innerText = "Neural Network thinking...";
        stockfish.postMessage("position fen " + game.fen());
        stockfish.postMessage("go depth 12");
    }

    // --- USER INTERACTIONS ---
    function onDrop (source, target) {
        removeHighlights();
        var move = game.move({ from: source, to: target, promotion: 'q' });

        if (move === null) return 'snapback';
        
        updateStatus();
        window.setTimeout(makeEngineMove, 250);
    }

    function askCoach() {
        if(game.turn() === 'b') return; 
        if(!bestMove) return;
        
        var from = bestMove.substring(0, 2);
        var to = bestMove.substring(2, 4);
        
        // Visual Highlight
        var $board = $('#myBoard');
        $board.find('.square-' + from).addClass('highlight-hint');
        $board.find('.square-' + to).addClass('highlight-hint');
        
        document.getElementById('coach-msg').innerText = "Suggestion: " + from + " -> " + to;
    }

    function removeHighlights() {
        $('#myBoard .square-55d63').removeClass('highlight-hint');
    }

    function updateStatus() {
        var status = '';
        var moveColor = (game.turn() === 'b') ? 'Black' : 'White';

        if (game.in_checkmate()) { status = 'Checkmate! ' + moveColor + ' loses.'; }
        else if (game.in_draw()) { status = 'Draw!'; }
        else { status = moveColor + ' to move'; }
        document.getElementById('status').innerText = status;
    }

    function undo() { game.undo(); game.undo(); board.position(game.fen()); updateStatus(); }
    function reset() { game.reset(); board.start(); document.getElementById('win-percent').innerText="50%"; }

    var config = { draggable: true, position: 'start', onDrop: onDrop };
    board = Chessboard('myBoard', config);
    
    // Initialize Engine
    stockfish.postMessage("uci");
    $(window).resize(board.resize);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
