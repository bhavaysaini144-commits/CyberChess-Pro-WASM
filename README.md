# ♟️ CyberChess: The "Unbreakable" Chess Engine

> A passion project exploring how to make high-performance web apps that work offline, instantly, and without external dependencies.

## 🚀 Play the Demo
**[Click here to try CyberChess](https://cyberchess-pro-wasm.onrender.com)**

## 👋 The Story Behind This Project
I started building CyberChess with a simple goal: **I wanted to understand how Grandmaster AIs actually work.**

My first attempt used a Python server to calculate moves, but I quickly realized the "lag" between the server and the player made the game feel slow. I decided to scrap the server approach and challenge myself to run the **entire engine directly in the user's browser**.

The result is a chess app that loads instantly, plays with zero lag (even on slow Wi-Fi), and uses some creative engineering to ensure it never crashes.

## 🛠️ How I Built It
*   **The Brain:** Stockfish 10 (Compiling C++ to WebAssembly/WASM).
*   **The Logic:** JavaScript (ES6) & Web Workers for multithreading.
*   **The Graphics:** Custom SVG Generation (No image files!).
*   **The Memory:** HTML5 LocalStorage for saving games.

## 🧠 My Favorite Engineering Challenges

### 1. Solving the "Invisible Piece" Problem
During development, I noticed that on restricted networks (like school Wi-Fi), the chess piece images (`pawn.png`, `knight.png`) were getting blocked, leaving the board empty.
*   **My Fix:** I decided to stop downloading images altogether. I wrote a **dynamic renderer** that draws the pieces using SVG code *inside* the browser.
*   **The Result:** The game is now "bulletproof." If the webpage loads, the pieces load. No 404 errors, ever.

### 2. Bringing "Stockfish" to the Browser
Running a supercomputer-level chess engine in a web browser is heavy. To prevent the page from freezing while the AI thinks, I implemented **WebAssembly (WASM)** running on a background thread.
*   This reduced move calculation time from **400ms** (server trip) to **~15ms** (local CPU). It feels instantaneous.

### 3. The "Human" Element
Raw chess engines are intimidating—they just crush you. I wanted this tool to be a coach, not just an opponent.
*   I built a **"Win Probability" Tracker** that translates the engine's complex math into a simple percentage (e.g., *"White has a 65% chance to win"*).
*   I also added a **Difficulty Selector** that throttles the engine's brain power, simulating everything from a Beginner (800 ELO) to a Grandmaster (2800 ELO).

## 📦 Run it on your machine
If you want to look at the code or play offline:

```bash
# 1. Clone my repo
git clone https://github.com/YOUR_USERNAME/CyberChess-Pro-WASM.git

# 2. Install the simple server
pip install -r requirements.txt

# 3. Play
python app.py
