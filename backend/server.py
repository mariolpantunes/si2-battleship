import asyncio
import json
import logging
import random
from typing import Any, Dict, List, Optional, Tuple, Union

from websockets.asyncio.server import ServerConnection, serve

logging.basicConfig(level=logging.INFO, format="%(asctime)s - SERVER - %(levelname)s - %(message)s")


class BattleshipServer:
    """
    WebSocket server for the Battleship game.
    Manages the game state, connects agents and a single viewer (frontend).
    """

    def __init__(self) -> None:
        """
        Initializes the game state and tracking variables.
        """
        self.frontend_ws: Optional[ServerConnection] = None
        self.agent1_ws: Optional[ServerConnection] = None
        self.agent2_ws: Optional[ServerConnection] = None

        self.size: int = 10
        # 0 = Water, Ship Name = Ship
        self.p1_ships: List[List[Union[int, str]]] = [[0] * self.size for _ in range(self.size)]
        self.p2_ships: List[List[Union[int, str]]] = [[0] * self.size for _ in range(self.size)]
        # 0 = Unknown, 1 = Miss, 2 = Hit
        self.p1_shots: List[List[int]] = [[0] * self.size for _ in range(self.size)]
        self.p2_shots: List[List[int]] = [[0] * self.size for _ in range(self.size)]

        self.ship_fleet: Dict[str, int] = {
            "Carrier": 5,
            "Battleship": 4,
            "Cruiser": 3,
            "Submarine": 3,
            "Destroyer": 2,
        }
        self.p1_health: Dict[str, int] = {}
        self.p2_health: Dict[str, int] = {}

        self.first_player_this_round: int = 1
        self.current_turn: int = 1
        self.running: bool = False
        self.scores: Dict[int, int] = {1: 0, 2: 0}

    async def start(self, host: str = "0.0.0.0", port: int = 8765) -> None:
        """
        Starts the WebSocket server.

        Args:
            host (str): The host address to bind to.
            port (int): The port to listen on.
        """
        logging.info(f"Battleship Server started on ws://{host}:{port}")
        async with serve(self.handle_client, host, port):
            await asyncio.Future()

    async def handle_client(self, websocket: ServerConnection) -> None:
        """
        Handles incoming WebSocket connections and assigns them to a role.

        Args:
            websocket: The connecting WebSocket protocol instance.
        """
        client_type: str = "Unknown"
        try:
            init_msg = await websocket.recv()

            data: Dict[str, Any] = json.loads(init_msg)
            type_val = data.get("client", "Unknown")
            client_type = str(type_val) if type_val is not None else "Unknown"

            if client_type == "frontend":
                logging.info("Frontend connected.")
                self.frontend_ws = websocket
                await self.update_frontend()
                await self.frontend_loop(websocket)
            elif client_type == "agent":
                if not self.agent1_ws:
                    self.agent1_ws = websocket
                    logging.info("Player 1 connected.")
                    await websocket.send(json.dumps({"type": "setup", "player_id": 1, "size": self.size}))
                    await self.check_start_conditions()
                    await self.agent_loop(websocket, 1)
                elif not self.agent2_ws:
                    self.agent2_ws = websocket
                    logging.info("Player 2 connected.")
                    await websocket.send(json.dumps({"type": "setup", "player_id": 2, "size": self.size}))
                    await self.check_start_conditions()
                    await self.agent_loop(websocket, 2)
                else:
                    await websocket.close()
        except Exception as e:
            logging.error(f"Error handling client ({client_type}): {e}")
        finally:
            if websocket == self.frontend_ws:
                self.frontend_ws = None
            elif websocket == self.agent1_ws:
                self.agent1_ws = None
                self.running = False
            elif websocket == self.agent2_ws:
                self.agent2_ws = None
                self.running = False

    async def frontend_loop(self, websocket: ServerConnection) -> None:
        """
        Main loop for the frontend viewer connection.

        Args:
            websocket: The frontend WebSocket protocol instance.
        """
        async for _ in websocket:
            pass

    async def agent_loop(self, websocket: ServerConnection, player_id: int) -> None:
        """
        Main loop for an agent connection.

        Args:
            websocket: The agent's WebSocket protocol instance.
            player_id: The ID of the player (1 or 2).
        """
        async for message in websocket:
            if not self.running or self.current_turn != player_id:
                continue
            try:
                data: Dict[str, Any] = json.loads(message)
                if data.get("action") == "fire":
                    x, y = data.get("x"), data.get("y")
                    if isinstance(x, int) and isinstance(y, int):
                        valid, hit = self.process_shot(player_id, x, y)
                        if valid:
                            await self.update_frontend()
                            await self.check_game_over()
                            if self.running:
                                if not hit:
                                    self.current_turn = 3 - self.current_turn
                                await self.broadcast_state()
            except Exception as e:
                logging.error(f"Error processing move from Player {player_id}: {e}")

    async def check_start_conditions(self) -> None:
        """
        Checks if both agents are connected and starts a new round if needed.
        """
        if self.agent1_ws and self.agent2_ws and not self.running:
            self.running = True
            self.current_turn = self.first_player_this_round

            # Initialize empty boards
            self.p1_ships = [[0] * self.size for _ in range(self.size)]
            self.p2_ships = [[0] * self.size for _ in range(self.size)]
            self.p1_shots = [[0] * self.size for _ in range(self.size)]
            self.p2_shots = [[0] * self.size for _ in range(self.size)]

            # Place ships and track health
            self.p1_health = self.place_fleet(self.p1_ships)
            self.p2_health = self.place_fleet(self.p2_ships)

            await self.update_frontend()
            await self.broadcast_state()

    def place_fleet(self, board: List[List[Union[int, str]]]) -> Dict[str, int]:
        r"""
        Randomly places ships on the provided board.

        Args:
            board: The 10x10 matrix to place ships on.

        Returns:
            A dictionary tracking the health of each placed ship.
        """
        health_tracker: Dict[str, int] = {}
        for ship_name, length in self.ship_fleet.items():
            health_tracker[ship_name] = length
            placed = False
            while not placed:
                x, y = (
                    random.randint(0, self.size - 1),
                    random.randint(0, self.size - 1),
                )
                horizontal = random.choice([True, False])

                # Check bounds
                if horizontal and x + length > self.size:
                    continue
                if not horizontal and y + length > self.size:
                    continue

                # Check overlap
                overlap = False
                for i in range(length):
                    if horizontal:
                        if board[y][x + i] != 0:
                            overlap = True
                            break
                    else:
                        if board[y + i][x] != 0:
                            overlap = True
                            break

                if not overlap:
                    for i in range(length):
                        if horizontal:
                            board[y][x + i] = ship_name
                        else:
                            board[y + i][x] = ship_name
                    placed = True
        return health_tracker

    def get_valid_actions(self, player_id: int) -> List[List[int]]:
        """
        Calculates all valid target coordinates for a player.

        Args:
            player_id: The ID of the player (1 or 2).

        Returns:
            A list of [x, y] coordinates that have not been targeted yet.
        """
        shots = self.p1_shots if player_id == 1 else self.p2_shots
        actions: List[List[int]] = []
        for y in range(self.size):
            for x in range(self.size):
                if shots[y][x] == 0:
                    actions.append([x, y])
        return actions

    def process_shot(self, player_id: int, x: int, y: int) -> Tuple[bool, bool]:
        r"""
        Processes an agent's firing action.

        Given a coordinate $(x, y)$, where $x, y \in [0, 9]$, this method
        updates the shot history $M_{shots}$ and checks for a hit on the
        opponent's fleet $F$.

        Args:
            player_id: The ID of the player taking the shot.
            x: The x-coordinate target.
            y: The y-coordinate target.

        Returns:
            A tuple (valid_shot, was_hit).
        """
        shots = self.p1_shots if player_id == 1 else self.p2_shots
        enemy_ships = self.p2_ships if player_id == 1 else self.p1_ships
        enemy_health = self.p2_health if player_id == 1 else self.p1_health

        if not (0 <= x < self.size and 0 <= y < self.size) or shots[y][x] != 0:
            return False, False  # Invalid or already shot

        target = enemy_ships[y][x]
        is_hit = False
        if isinstance(target, str):
            shots[y][x] = 2  # Hit
            is_hit = True
            enemy_health[target] -= 1
            if enemy_health[target] == 0:
                logging.info(f"Player {player_id} SUNK the {target}!")
        else:
            shots[y][x] = 1  # Miss

        return True, is_hit

    async def check_game_over(self) -> None:
        """
        Checks if the current game session has concluded.
        """
        p1_dead = all(h == 0 for h in self.p1_health.values())
        p2_dead = all(h == 0 for h in self.p2_health.values())

        winner = None
        if p1_dead:
            winner = 2
        elif p2_dead:
            winner = 1

        if winner:
            self.scores[winner] += 1
            await self.end_round(f"Player {winner} Wins!")

    async def end_round(self, message: str) -> None:
        """
        Finishes a game round and schedules a restart.

        Args:
            message: The result message to send to clients.
        """
        self.running = False
        payload = {"type": "game_over", "message": message}
        if self.agent1_ws:
            await self.agent1_ws.send(json.dumps(payload))
        if self.agent2_ws:
            await self.agent2_ws.send(json.dumps(payload))
        await self.update_frontend()

        await asyncio.sleep(3.0)
        self.first_player_this_round = 3 - self.first_player_this_round
        await self.check_start_conditions()

    async def broadcast_state(self) -> None:
        """Sends partial state information to each connected agent."""
        if self.agent1_ws:
            await self.agent1_ws.send(
                json.dumps(
                    {
                        "type": "state",
                        "current_turn": self.current_turn,
                        "my_ships": self.p1_ships,
                        "my_shots": self.p1_shots,
                        "valid_actions": self.get_valid_actions(1),
                    }
                )
            )
        if self.agent2_ws:
            await self.agent2_ws.send(
                json.dumps(
                    {
                        "type": "state",
                        "current_turn": self.current_turn,
                        "my_ships": self.p2_ships,
                        "my_shots": self.p2_shots,
                        "valid_actions": self.get_valid_actions(2),
                    }
                )
            )

    async def update_frontend(self) -> None:
        """Sends the full game state to the frontend viewer."""
        if self.frontend_ws:
            await self.frontend_ws.send(
                json.dumps(
                    {
                        "type": "update",
                        "current_turn": self.current_turn,
                        "p1_ships": self.p1_ships,
                        "p2_ships": self.p2_ships,
                        "p1_shots": self.p1_shots,
                        "p2_shots": self.p2_shots,
                        "scores": self.scores,
                        "p1_connected": self.agent1_ws is not None,
                        "p2_connected": self.agent2_ws is not None,
                    }
                )
            )


if __name__ == "__main__":
    server = BattleshipServer()
    asyncio.run(server.start())
