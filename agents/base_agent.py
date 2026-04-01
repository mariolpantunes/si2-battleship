import json
import logging

import websockets

logging.basicConfig(level=logging.INFO, format="%(asctime)s - AGENT - %(message)s")


class BaseBSAgent:
    """
    Abstract base class for Battleship agents.
    Subclasses MUST implement the deliberate() method.
    """

    def __init__(self, server_uri="ws://localhost:8765"):
        self.server_uri = server_uri
        self.player_id = None

    async def run(self):
        try:
            async with websockets.connect(self.server_uri) as websocket:
                await websocket.send(json.dumps({"client": "agent"}))

                async for message in websocket:
                    data = json.loads(message)

                    if data.get("type") == "setup":
                        self.player_id = data.get("player_id")
                        self.board_size = data.get("size")
                        logging.info(f"Connected! Assigned Player {self.player_id}")

                    elif data.get("type") == "state":
                        current_turn = data.get("current_turn")
                        my_ships = data.get("my_ships")
                        my_shots = data.get("my_shots")
                        valid_actions = data.get("valid_actions")

                        if current_turn == self.player_id:
                            # Pass the partial state to the subclass logic
                            target_coord = await self.deliberate(
                                my_ships, my_shots, valid_actions
                            )

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

                    elif data.get("type") == "game_over":
                        logging.info(f"Round Over: {data.get('message')}")
                        logging.info("Waiting for next round to start...")

        except Exception as e:
            logging.error(f"Connection lost: {e}")

    async def deliberate(self, my_ships, my_shots, valid_actions):
        """
        MUST be implemented by subclasses.
        Returns a list/tuple of [x, y] representing the target coordinate.
        """
        raise NotImplementedError("Subclasses must implement deliberate()")
