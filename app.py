from flask import Flask, render_template_string

app = Flask(__name__)

# --- CYBERCHESS: STANDALONE EDITION (NO DOWNLOADS) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>CyberChess | Standalone</title>
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
        .btn-reset { background: #444; color: white; }

        .highlight-hint { box-shadow: inset 0 0 3px 3px var(--highlight); }
        #debug-log { position: fixed; bottom: 0; left: 0; background: rgba(0,0,0,0.8); color: orange; font-size: 10px; padding: 5px; }

        @media(max-width: 900px) { 
            .layout { flex-direction: column; } 
            .sidebar { width: auto; height: auto; order: 2; }
            #myBoard { width: 90vw !important; }
        }
    </style>
</head>
<body>

<div class="nav">
    <div class="brand"><i class="fas fa-shield-alt"></i> CYBERCHESS <span style="font-size:10px; background:var(--accent); color:#000; padding:2px 6px; border-radius:4px;">SECURE</span></div>
    <div style="font-size: 12px; color: #666;">System: <span id="sys-status">Initializing...</span></div>
</div>

<div class="layout">
    <div class="game-area">
        <div id="myBoard" style="width: 480px"></div>
        <div id="debug-log">Status: Graphics Generated Locally</div>
    </div>
    
    <div class="sidebar">
        <div class="coach-box">
            <div style="text-transform: uppercase; font-size: 12px; letter-spacing: 1px; color: #666;">Win Probability</div>
            <div class="eval-score" id="win-percent">50%</div>
            <div style="color: #888; font-size: 14px;" id="coach-msg">Ready.</div>
            <div class="progress-container"><div class="progress-bar" id="win-bar"></div></div>
        </div>

        <div class="coach-box" style="text-align: left;">
            <div style="color:#fff; font-weight:bold; margin-bottom:5px;">Actions</div>
            <button class="btn btn-hint" onclick="askCoach()"><i class="far fa-lightbulb"></i> AI Hint</button>
            <div style="display:flex; gap:10px;">
                <button class="btn btn-reset" onclick="undo()"><i class="fas fa-undo"></i> Undo</button>
                <button class="btn btn-reset" onclick="reset()"><i class="fas fa-sync"></i> Reset</button>
            </div>
        </div>
    </div>
</div>

<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
<script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>

<script>
    var board = null;
    var game = new Chess();
    var stockfish = null;
    var bestMove = null;

    // --- 1. THE GRAPHICS GENERATOR (NO DOWNLOADS) ---
    // This function draws the pieces using code, so they cannot be blocked.
    function pieceGenerator(piece) {
        const symbols = {
            'wP': '♟', 'wN': '♞', 'wB': '♝', 'wR': '♜', 'wQ': '♛', 'wK': '♔',
            'bP': '♟', 'bN': '♞', 'bB': '♝', 'bR': '♜', 'bQ': '♛', 'bK': '♚'
        };
        const color = piece[0] === 'w' ? '#e0e0e0' : '#121212';
        const stroke = piece[0] === 'w' ? '#121212' : '#e0e0e0';
        const char = symbols[piece];
        
        // Create an SVG image on the fly
        const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80">
            <text x="50%" y="50%" dy=".35em" text-anchor="middle" 
                  font-size="60" font-family="Arial, sans-serif" font-weight="bold"
                  fill="${color}" stroke="${stroke}" stroke-width="2">${char}</text>
        </svg>`;
        
        return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
    }

    // --- 2. INITIALIZE BOARD ---
    function onDrop (source, target) {
        removeHighlights();
        var move = game.move({ from: source, to: target, promotion: 'q' });
        if (move === null) return 'snapback';
        updateStatus();
        if(stockfish) window.setTimeout(makeEngineMove, 250);
    }

    var config = { 
        draggable: true, 
        position: 'start', 
        onDrop: onDrop,
        pieceTheme: pieceGenerator // <--- WE USE OUR GENERATOR HERE
    };
    board = Chessboard('myBoard', config);
    $(window).resize(board.resize);

    // --- 3. INITIALIZE ENGINE (BLOB METHOD) ---
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
        document.getElementById('sys-status').innerText = "Engine Ready";
        document.getElementById('sys-status').style.color = "#00e676";
    }).catch(e => {
        document.getElementById('sys-status').innerText = "PvP Mode (Engine Blocked)";
    });

    // --- 4. LOGIC ---
    function makeEngineMove() {
        if(game.game_over()) return;
        stockfish.postMessage("position fen " + game.fen());
        stockfish.postMessage("go depth 12");
    }

    function updateCoach(cp) {
        var chance = 1 / (1 + Math.pow(10, -cp/400)); 
        var percent = Math.round(chance * 100);
        document.getElementById('win-bar').style.width = percent + "%";
        document.getElementById('win-percent').innerText = percent + "%";
        
        var msg = document.getElementById('coach-msg');
        if(percent > 60) { msg.innerText = "White Advantage"; msg.style.color = "#00e676"; }
        else if(percent < 40) { msg.innerText = "Black Advantage"; msg.style.color = "#ff1744"; }
        else { msg.innerText = "Equal Game"; msg.style.color = "#888"; }
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

