# <img src="frontend/favicon.svg" alt="logo" width="128" height="128" align="middle"> SI2 - Battleship

SI2 - Battleship is a modular simulation platform designed for developing and testing autonomous agents in the classic game of Battleship. The system features a centralized Python-based WebSocket backend that manages game logic, a real-time web viewer for monitoring matches, and an extensible framework for implementing custom AI strategies.

The primary objective of the game is to sink all of the opponent's ships before they sink yours. Each player controls a 10x10 grid where their fleet is hidden from the opponent. Players take turns "firing" shots at specific coordinates, receiving immediate feedback on whether they hit a ship or splashed into the water, with successful hits granting an extra turn.

## Game Rules

The simulation follows the standard rules of Battleship with a few specific implementation details:
* **Grid Size**: 10x10.
* **Fleet**: Each player has 5 ships: Carrier (5), Battleship (4), Cruiser (3), Submarine (3), and Destroyer (2).
* **Turns**: Players alternate turns. If a player hits a ship, they receive an additional turn.
* **Victory**: The game ends when one player has all their ship segments destroyed.

### Game State and Actions
Agents receive a partial view of the world state during their turn:
* **`my_ships`**: A 10x10 matrix representing your own board, where each cell contains the ship's name (e.g., `"Carrier"`) or `0` for empty water.
* **`my_shots`**: A 10x10 matrix representing your history of offensive moves (0 = unknown, 1 = miss, 2 = hit).
* **`valid_actions`**: A list of available `[x, y]` coordinates that have not been targeted yet.

**Possible Action**:
* `fire(x, y)`: Submit a coordinate to attack the opponent's board.

## Setup

### 1. Launch the Simulation
Use Docker Compose to start the backend server and the frontend viewer:
```bash
docker compose up
```
* **Backend**: `ws://localhost:8765`
* **Frontend Viewer**: `http://localhost:8080`

### 2. Execute Agents
Agents should be executed locally using a Python virtual environment:

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run an agent (e.g., the Dummy agent)
python agents/dummy_agent.py
```

## Project Structure

* `backend/`: Contains `server.py`, the core game engine handling WebSockets and logic, and its `Dockerfile`.
* `frontend/`: Contains the single viewer (HTML, CSS, JS) used to monitor the game state.
* `agents/`: Contains the battleship agents:
    * `base_agent.py`: The abstract base class providing the communication layer.
    * `dummy_agent.py`: A simple automated agent that selects random targets.
    * `manual_agent.py`: An agent allowing manual interaction via terminal input.
* `compose.yml`: Docker Compose configuration for the backend and frontend.

## Development

To develop a new agent, create a new class that inherits from `BaseBSAgent` and implement the `deliberate` method. For detailed API references, please refer to the [official documentation](https://mariolpantunes.github.io/si2-battleship/).

```python
from agents.base_agent import BaseBSAgent

class MyNewAgent(BaseBSAgent):
    async def deliberate(self, my_ships, my_shots, valid_actions):
        # Implement your strategy here
        # Return a coordinate [x, y] from valid_actions
        return valid_actions[0]

if __name__ == "__main__":
    import asyncio
    agent = MyNewAgent()
    asyncio.run(agent.run())
```

## Authors

* **Mário Antunes** - [mariolpantunes](https://github.com/mariolpantunes)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
