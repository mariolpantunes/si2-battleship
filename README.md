# <img src="frontend/favicon.svg" alt="logo" width="128" height="128" align="middle"> SI2 - Battleship AI Arena

A modular Battleship simulation platform with a Python-based WebSocket backend, an HTML/JS frontend for visualization, and an extensible agent system.

## Features

- **Multiplayer Arena**: Two AI agents (or humans) compete in a real-time Battleship match.
- **Single Viewer**: A dedicated frontend for observing the game state, including ship positions and shot history for both players.
- **Infinite Game Loop**: The server automatically restarts rounds, alternating the starting player each time.
- **Classic Mechanics**: Includes a "hit-again" rule where a successful hit grants the player another turn.
- **Modular Agents**: Easy-to-extend `BaseBSAgent` class for implementing custom AI strategies.
- **Dockerized Environment**: Quick setup for the backend and frontend viewer using Docker Compose.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mariolpantunes/si2-battleship.git
   cd si2-battleship
   ```

2. **Local environment setup (for agents)**:
   Agents *must* run locally without Docker:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

### 1. Start the Arena
The easiest way to start the backend server and the frontend viewer is using Docker Compose:
```bash
docker compose up
```
- The **Backend** will be available at `ws://localhost:8765`.
- The **Frontend Viewer** will be available at `http://localhost:8080`.

### 2. Open the Viewer
Open your browser and navigate to `http://localhost:8080` to watch the match unfold.

### 3. Run the Agents
Connect two agents to the running server. You can mix and match manual and AI agents.

- **Manual Control**:
  ```bash
  python3 agents/manual_agent.py
  ```
  Follow the terminal prompts to enter coordinates (e.g., `3,4`).

- **Dummy (Random) Agent**:
  ```bash
  python3 agents/dummy_agent.py
  ```

## Project Structure

- `backend/server.py`: The core game logic and WebSocket server.
- `frontend/`: HTML, CSS, and JavaScript for the web-based viewer.
- `agents/`:
    - `base_agent.py`: Abstract base class handling WebSocket communication and state parsing.
    - `dummy_agent.py`: A simple agent that picks random valid targets.
    - `manual_agent.py`: An agent that allows for manual player interaction via the terminal.
- `compose.yml`: Docker Compose configuration for the full stack.

## Development

### Adding a New Agent
To create a new agent, subclass `BaseBSAgent` and implement the `deliberate()` method:

```python
from agents.base_agent import BaseBSAgent

class MyCustomAgent(BaseBSAgent):
    async def deliberate(self, my_ships, my_shots, valid_actions):
        # my_ships: 10x10 grid with your ship names
        # my_shots: 10x10 grid with your shot history (0=unknown, 1=miss, 2=hit)
        # valid_actions: list of [x, y] coordinates you haven't shot at yet
        
        # Return a list/tuple of [x, y] representing the target coordinate
        return valid_actions[0]
```

## Authors

* **Mário Antunes** - [mariolpantunes](https://github.com/mariolpantunes)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
