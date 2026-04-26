from flask import Flask, render_template_string

app = Flask(__name__)

# --- CYBERCHESS: FINAL (WITH SAVE SYSTEM) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>CyberChess | Portfolio Edition</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <style>
        :root { --bg: #121212; --panel: #1e1e1e; --text: #e0e0e0; --accent: #00e676; --highlight: #2979ff; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; height: 100vh; display: flex; flex-direction: column; }
        
        .nav { padding: 15px 25px; background: #000; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }
        .brand { font-weight: 800; letter-spacing: 1px; color: #fff; display: flex; align-items: center; gap: 10px; }
        
        .layout { flex: 1; display: flex; height: calc(100vh - 70px); }
        .game-area { flex: 1; display: flex; justify-content: center; align-items: center; background: #181818; flex-direction: column; }
        .sidebar { width: 350px; background: var(--panel); border-left: 1px solid #333; display: flex; flex-direction: column; padding: 20px; gap: 15px; }
        
        .coach-box { background: #252525; padding: 15px; border-radius: 8px; border: 1px solid #333; text-align: center; }
        .eval-score { font-size: 32px; font-weight: bold; color: var(--accent); margin: 10px 0; }
        
        .progress-container { height: 6px; background: #333; border-radius: 3px; margin-top: 10px; overflow: hidden; }
        .progress-bar { height: 100%; background: var(--accent); width: 50%; transition: width 0.5s ease; }

        .btn { width: 100%; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; transition: 0.2s; }
        .btn-hint { background: var(--highlight); color: white; }
        .btn-save { background: #ff9100; color: black; } 
        .btn-reset { background: #444; color: white; }
        .btn:hover { opacity: 0.9; transform: translateY(-1px); }

        select { width: 100%; padding: 10px; background: #333; color: white; border: 1px solid #555; border-radius: 5px; margin-top: 5px; font-weight: bold; cursor: pointer; }
        
        .highlight-hint { box-shadow: inset 0 0 3px 3px var(--highlight); }
        #debug-log { position: fixed; bottom: 0; left: 0; background: rgba(0,0,0,0.8); color: orange; font-size: 10px; padding: 5px; }

        /* TOAST NOTIFICATION */
        #toast { visibility: hidden; min-width: 200px; background-color: #333; color: #fff; text-align: center; border-radius: 4px; padding: 16px; position: fixed; z-index: 1; left: 50%; bottom: 30px; transform: translateX(-50%); border: 1px solid var(--accent); }
        #toast.show { visibility: visible; animation: fadein 0.5s, fadeout 0.5s 2.5s; }
        @keyframes fadein { from {bottom: 0; opacity: 0;} to {bottom: 30px; opacity: 1;} }
        @keyframes fadeout { from {bottom: 30px; opacity: 1;} to {bottom: 0; opacity: 0;} }

        @media(max-width: 900px) { 
            .layout { flex-direction: column; } 
            .sidebar { width: auto; height: auto; order: 2; }
            #myBoard { width: 90vw !important; }
        }
    </style>
</head>
<body>

<div class="nav">
    <div class="brand"><i class="fas fa-chess"></i> CYBERCHESS <span style="font-size:10px; background:var(--accent); color:#000; padding:2px 6px; border-radius:4px;">FINAL</span></div>
    <div style="font-size: 12px; color: #666;">Engine: <span id="sys-status">Init...</span></div>
</div>

<div class="layout">
    <div class="game-area">
        <div id="myBoard" style="width: 480px"></div>
        <div id="debug-log">Graphics: SVG Injected</div>
    </div>
    
    <div class="sidebar">
        <!-- SETTINGS -->
        <div class="coach-box" style="text-align: left;">
            <div style="color:#fff; font-weight:bold; font-size: 12px; text-transform: uppercase;">Difficulty</div>
            <select id="difficulty">
                <option value="1">Novice (Depth 1)</option>
                <option value="6" selected>Club (Depth 6)</option>
                <option value="15">Master (Depth 15)</option>
            </select>
        </div>

        <!-- STATS -->
        <div class="coach-box">
            <div style="text-transform: uppercase; font-size: 12px; letter-spacing: 1px; color: #666;">Win Chance</div>
            <div class="eval-score" id="win-percent">50%</div>
            <div style="color: #888; font-size: 14px;" id="coach-msg">Board Ready.</div>
            <div class="progress-container"><div class="progress-bar" id="win-bar"></div></div>
        </div>

        <!-- CONTROLS -->
        <div class="coach-box" style="text-align: left;">
            <div style="color:#fff; font-weight:bold; margin-bottom:5px;">Controls</div>
            <button class="btn btn-hint" onclick="askCoach()"><i class="far fa-lightbulb"></i> Get Hint</button>
            
            <div style="display:flex; gap:10px; margin-top:10px;">
                <button class="btn btn-save" onclick="saveGame()"><i class="fas fa-save"></i> Save</button>
                <button class="btn btn-save" onclick="loadGame()"><i class="fas fa-upload"></i> Load</button>
            </div>

            <div style="display:flex; gap:10px;">
                <button class="btn btn-reset" onclick="undo()"><i class="fas fa-undo"></i> Undo</button>
                <button class="btn btn-reset" onclick="reset()"><i class="fas fa-sync"></i> Reset</button>
            </div>
        </div>
    </div>
</div>

<div id="toast">Game Saved Locally!</div>

<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
<script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>

<script>
    var board = null;
    var game = new Chess();
    var stockfish = null;
    var bestMove = null;

    // --- 1. SVG RENDERER ---
    function pieceGenerator(piece) {
        const symbols = { 'wP': '♟', 'wN': '♞', 'wB': '♝', 'wR': '♜', 'wQ': '♛', 'wK': '♔', 'bP': '♟', 'bN': '♞', 'bB': '♝', 'bR': '♜', 'bQ': '♛', 'bK': '♚' };
        const color = piece[0] === 'w' ? '#e0e0e0' : '#121212';
        const stroke = piece[0] === 'w' ? '#121212' : '#e0e0e0';
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80">
            <text x="50%" y="50%" dy=".35em" text-anchor="middle" font-size="60" font-family="Arial" font-weight="bold" fill="${color}" stroke="${stroke}" stroke-width="2">${symbols[piece]}</text></svg>`;
        return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
    }

    // --- 2. SAVE/LOAD SYSTEM (LOCAL STORAGE) ---
    function saveGame() {
        // Save the FEN string (The DNA of the current board)
        localStorage.setItem('cyberchess_save', game.fen());
        showToast("Game Saved to Browser Storage!");
    }

    function loadGame() {
        var savedFen = localStorage.getItem('cyberchess_save');
        if(savedFen) {
            game.load(savedFen);
            board.position(savedFen);
            updateStatus();
            showToast("Game Loaded!");
            // Force engine to re-evaluate
            if(stockfish) {
                stockfish.postMessage("position fen " + game.fen());
                stockfish.postMessage("go depth 10");
            }
        } else {
            showToast("No saved game found.");
        }
    }

    function showToast(msg) {
        var x = document.getElementById("toast");
        x.innerText = msg;
        x.className = "show";
        setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
    }

    // --- 3. CORE LOGIC ---
    function onDrop (source, target) {
        removeHighlights();
        var move = game.move({ from: source, to: target, promotion: 'q' });
        if (move === null) return 'snapback';
        updateStatus();
        if(stockfish) window.setTimeout(makeEngineMove, 250);
    }

    var config = { draggable: true, position: 'start', onDrop: onDrop, pieceTheme: pieceGenerator };
    board = Chessboard('myBoard', config);
    $(window).resize(board.resize);

    var engineUrl = 'https://cdnjs.cloudflare.com/ajax/libs/stockfish.js/10.0.0/stockfish.js';
    fetch(engineUrl).then(r => r.blob()).then(blob => {
        stockfish = new Worker(URL.createObjectURL(blob));
        stockfish.onmessage = function(event) {
            var msg = event.data;
            if(msg.indexOf("bestmove") > -1) {
                bestMove = msg.split(" ")[1]; 
                if(game.turn() === 'b') {
                    game.move(bestMove, {sloppy: true});
                    board.position(game.fen());
                    updateStatus();
                }
            }
            if (msg.indexOf("score cp") > -1) {
                var score = parseInt(msg.split("score cp ")[1].split(" ")[0]);
                if(game.turn() === 'b') score = -score;
                updateCoach(score);
            }
        };
        stockfish.postMessage("uci");
        document.getElementById('sys-status').innerText = "Ready";
        document.getElementById('sys-status').style.color = "#00e676";
    });

    function makeEngineMove() {
        if(game.game_over()) return;
        var depth = document.getElementById('difficulty').value;
        document.getElementById('coach-msg').innerText = "Thinking...";
        stockfish.postMessage("position fen " + game.fen());
        stockfish.postMessage("go depth " + depth);
    }

    function updateCoach(cp) {
        var chance = 1 / (1 + Math.pow(10, -cp/400)); 
        var percent = Math.round(chance * 100);
        document.getElementById('win-bar').style.width = percent + "%";
        document.getElementById('win-percent').innerText = percent + "%";
        var msg = document.getElementById('coach-msg');
        if(percent > 60) { msg.innerText = "White Leads"; msg.style.color = "#00e676"; }
        else if(percent < 40) { msg.innerText = "Black Leads"; msg.style.color = "#ff1744"; }
        else { msg.innerText = "Equal"; msg.style.color = "#888"; }
    }

    function updateStatus() {
        var status = '';
        var moveColor = (game.turn() === 'b') ? 'Black' : 'White';
        if (game.in_checkmate()) status = 'Checkmate!';
        else if (game.in_draw()) status = 'Draw!';
        else status = moveColor + ' to move';
        document.getElementById('coach-msg').innerText = status;
    }

    function askCoach() {
        if(game.turn() === 'b' || !bestMove) return;
        var from = bestMove.substring(0, 2);
        var to = bestMove.substring(2, 4);
        var $board = $('#myBoard');
        $board.find('.square-' + from).addClass('highlight-hint');
        $board.find('.square-' + to).addClass('highlight-hint');
    }

    function removeHighlights() { $('#myBoard .square-55d63').removeClass('highlight-hint'); }
    function undo() { game.undo(); game.undo(); board.position(game.fen()); updateStatus(); }
    function reset() { game.reset(); board.start(); }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
