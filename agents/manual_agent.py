import asyncio
from typing import List, Optional, Tuple, Union

from agents.base_agent import BaseBSAgent


class ManualBSAgent(BaseBSAgent):
    """
    A human-controlled agent that reads target coordinates from the terminal.
    """

    async def deliberate(
        self,
        my_ships: List[List[Union[int, str]]],
        my_shots: List[List[int]],
        valid_actions: List[List[int]],
    ) -> Optional[Union[List[int], Tuple[int, int]]]:
        r"""
        Prompts the user for a coordinate via the terminal.

        Args:
            my_ships: 10x10 grid with your ship names.
            my_shots: 10x10 grid with your shot history.
            valid_actions: List of coordinates $[x, y]$ that haven't been targeted yet.

        Returns:
            The coordinate $[x, y]$ entered by the user.
        """
        print(f"\n--- YOUR TURN (Player {self.player_id}) ---")

        while True:
            # Prevent the asyncio loop from freezing while waiting for human input
            user_input = await asyncio.to_thread(input, "Enter target coordinate 'x,y' (e.g., 3,4): ")

            try:
                # Parse the "x,y" string into a list of two integers
                parts = user_input.strip().split(",")
                if len(parts) != 2:
                    raise ValueError

                x, y = int(parts[0]), int(parts[1])
                target = [x, y]

                if target in valid_actions:
                    return target
                else:
                    print("Invalid coordinate. Either out of bounds or already fired upon. Try again.")
            except ValueError:
                print("Invalid input format. Please use 'x,y' with numbers from 0 to 9.")


if __name__ == "__main__":
    agent = ManualBSAgent()
    print("Starting Manual Battleship Agent...")
    asyncio.run(agent.run())
