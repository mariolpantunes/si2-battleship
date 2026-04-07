import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import websockets

logging.basicConfig(level=logging.INFO, format="%(asctime)s - AGENT - %(levelname)s - %(message)s")


class BaseBSAgent:
    """
    Abstract base class for Battleship agents.

    Subclasses MUST implement the deliberate() method to define their
    decision-making logic.
    """

    def __init__(self, server_uri: str = "ws://localhost:8765") -> None:
        """
        Initializes the agent with the server URI.

        Args:
            server_uri (str): The WebSocket URI of the Battleship server.
        """
        self.server_uri: str = server_uri
        self.player_id: Optional[int] = None
        self.board_size: Optional[int] = None

    async def run(self) -> None:
        """
        Connects to the server and enters the main message loop.
        """
        try:
            async with websockets.connect(self.server_uri) as websocket:
                await websocket.send(json.dumps({"client": "agent"}))

                async for message in websocket:
                    if not isinstance(message, str):
                        continue

                    data = cast(Dict[str, Any], json.loads(message))

                    msg_type = str(data.get("type", ""))
                    if msg_type == "setup":
                        self.player_id = cast(Optional[int], data.get("player_id"))
                        self.board_size = cast(Optional[int], data.get("size"))
                        logging.info(f"Connected! Assigned Player {self.player_id}")

                    elif msg_type == "state":
                        current_turn = data.get("current_turn", -1)
                        my_ships_val = data.get("my_ships", [])
                        my_shots_val = data.get("my_shots", [])
                        valid_actions_val = data.get("valid_actions", [])

                        if (
                            isinstance(current_turn, int)
                            and isinstance(my_ships_val, list)
                            and isinstance(my_shots_val, list)
                            and isinstance(valid_actions_val, list)
                            and self.player_id is not None
                            and current_turn == self.player_id
                        ):
                            # Type narrowing for my_ships, my_shots, valid_actions
                            my_ships = cast(List[List[Union[int, str]]], my_ships_val)
                            my_shots = cast(List[List[int]], my_shots_val)
                            valid_actions = cast(List[List[int]], valid_actions_val)

                            # Pass the partial state to the subclass logic
                            target_coord = await self.deliberate(my_ships, my_shots, valid_actions)

                            if target_coord is not None:
                                await websocket.send(
                                    json.dumps(
                                        {
                                            "action": "fire",
                                            "x": target_coord[0],
                                            "y": target_coord[1],
                                        }
                                    )
                                )

                    elif msg_type == "game_over":
                        logging.info(f"Round Over: {data.get('message', 'Unknown result')}")
                        logging.info("Waiting for next round to start...")

        except Exception as e:
            logging.error(f"Connection lost: {e}")

    async def deliberate(
        self,
        my_ships: List[List[Union[int, str]]],
        my_shots: List[List[int]],
        valid_actions: List[List[int]],
    ) -> Optional[Union[List[int], Tuple[int, int]]]:
        r"""
        Determines the next target to fire upon.

        MUST be implemented by subclasses.

        Args:
            my_ships: 10x10 grid with your ship names or 0 for water.
                $M_{ships} \in \{0, \text{'Carrier'}, \dots\}^{10 \times 10}$
            my_shots: 10x10 grid with your shot history (0=unknown, 1=miss, 2=hit).
                $M_{shots} \in \{0, 1, 2\}^{10 \times 10}$
            valid_actions: List of [x, y] coordinates you haven't shot at yet.
                $A = \{(x, y) \mid M_{shots}[y][x] = 0\}$

        Returns:
            A list or tuple of [x, y] representing the target coordinate.
        """
        raise NotImplementedError("Subclasses must implement deliberate()")
