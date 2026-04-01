import asyncio
import random

from agents.base_agent import BaseBSAgent


class DummyBSAgent(BaseBSAgent):
    """
    A completely random agent for Battleship.
    """

    async def deliberate(self, my_ships, my_shots, valid_actions):
        # Add a tiny delay so human observers can watch the game unfold
        await asyncio.sleep(0.1)

        # Pick a random un-shot [x, y] coordinate
        chosen_target = random.choice(valid_actions)
        return chosen_target


if __name__ == "__main__":
    agent = DummyBSAgent()
    asyncio.run(agent.run())
