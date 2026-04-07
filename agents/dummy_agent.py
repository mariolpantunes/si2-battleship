import asyncio
import random
from typing import List, Optional, Tuple, Union

from agents.base_agent import BaseBSAgent


class DummyBSAgent(BaseBSAgent):
    """
    A simple automated Battleship agent that selects targets randomly.
    """

    async def deliberate(
        self,
        my_ships: List[List[Union[int, str]]],
        my_shots: List[List[int]],
        valid_actions: List[List[int]],
    ) -> Optional[Union[List[int], Tuple[int, int]]]:
        r"""
        Picks a random target from the available valid actions.

        Selects $(x, y) \sim \mathcal{U}(A)$, where $A$ is the set of valid actions.

        Args:
            my_ships: 10x10 grid with your ship names.
            my_shots: 10x10 grid with your shot history.
            valid_actions: List of coordinates [x, y] that haven't been targeted yet.

        Returns:
            A random [x, y] coordinate.
        """
        # Add a tiny delay so human observers can watch the game unfold
        await asyncio.sleep(0.1)

        # Pick a random un-shot [x, y] coordinate
        chosen_target = random.choice(valid_actions)
        return chosen_target


if __name__ == "__main__":
    agent = DummyBSAgent()
    asyncio.run(agent.run())
