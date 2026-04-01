class App {
  constructor() {
    const serverHost = window.location.hostname;
    this.ws = new WebSocket(`ws://${serverHost}:8765`);

    this.c1 = document.getElementById("p1-canvas");
    this.ctx1 = this.c1.getContext("2d");
    this.c2 = document.getElementById("p2-canvas");
    this.ctx2 = this.c2.getContext("2d");

    this.size = 10;
    this.cellSize = 40;
    this.state = null;

    this.setupWebsocket();
  }

  setupWebsocket() {
    this.ws.onopen = () => this.ws.send(JSON.stringify({ client: "frontend" }));

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "update") {
        this.state = data;

        document.getElementById("p1-status").innerText = data.p1_connected
          ? "Player 1 (Red)"
          : "Player 1 (Disconnected)";
        document.getElementById("p2-status").innerText = data.p2_connected
          ? "Player 2 (Yellow)"
          : "Player 2 (Disconnected)";
        document.getElementById("p1-score").innerText = data.scores[1];
        document.getElementById("p2-score").innerText = data.scores[2];

        const turnText = document.getElementById("turn-indicator");
        if (data.p1_connected && data.p2_connected) {
          turnText.innerText = `Current Turn: Player ${data.current_turn}`;
          turnText.style.color =
            data.current_turn === 1 ? "#BF616A" : "#EBCB8B";
        } else {
          turnText.innerText = "Waiting for agents...";
          turnText.style.color = "#D8DEE9";
        }

        this.draw();
      }
    };
  }

  draw() {
    if (!this.state) return;

    // P1's board shows P1's ships and P2's shots against them
    this.drawBoard(this.ctx1, this.state.p1_ships, this.state.p2_shots);
    // P2's board shows P2's ships and P1's shots against them
    this.drawBoard(this.ctx2, this.state.p2_ships, this.state.p1_shots);
  }

  drawBoard(ctx, ships, enemy_shots) {
    ctx.clearRect(0, 0, 400, 400);

    for (let y = 0; y < this.size; y++) {
      for (let x = 0; x < this.size; x++) {
        const cx = x * this.cellSize;
        const cy = y * this.cellSize;

        // 1. Draw Water
        ctx.fillStyle = "#5E81AC"; // Nord10 Blue
        ctx.fillRect(cx, cy, this.cellSize, this.cellSize);
        ctx.strokeStyle = "#81A1C1";
        ctx.strokeRect(cx, cy, this.cellSize, this.cellSize);

        // 2. Draw Ships
        if (ships && ships[y][x] !== 0) {
          ctx.fillStyle = "#4C566A"; // Nord3 Dark Grey
          // Slight inset so it looks like a ship on the water
          ctx.fillRect(cx + 4, cy + 4, this.cellSize - 8, this.cellSize - 8);
        }

        // 3. Draw Pegs (Enemy Shots)
        if (enemy_shots && enemy_shots[y][x] !== 0) {
          ctx.beginPath();
          ctx.arc(
            cx + this.cellSize / 2,
            cy + this.cellSize / 2,
            this.cellSize / 3,
            0,
            Math.PI * 2,
          );

          if (enemy_shots[y][x] === 2) {
            ctx.fillStyle = "#BF616A"; // HIT (Red)
          } else if (enemy_shots[y][x] === 1) {
            ctx.fillStyle = "#ECEFF4"; // MISS (White)
          }

          ctx.fill();
          ctx.strokeStyle = "rgba(0,0,0,0.5)";
          ctx.lineWidth = 2;
          ctx.stroke();
          ctx.lineWidth = 1;
        }
      }
    }
  }
}
const app = new App();
