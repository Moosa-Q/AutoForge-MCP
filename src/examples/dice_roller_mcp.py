import random
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dice_roller")

@mcp.tool()
def roll_dice(sides: int = 6, rolls: int = 1) -> str:
    """
    Simulate rolling dice.
    Args:
        sides: Number of sides on the dice (default 6).
        rolls: Number of dice to roll (default 1).
    """
    if sides < 2 or rolls < 1 or rolls > 100:
        return "Invalid input. Sides must be >=2, rolls between 1 and 100."
    results = [random.randint(1, sides) for _ in range(rolls)]
    return f"Rolled {rolls}d{sides}: {results}"

if __name__ == "__main__":
    mcp.run(transport="sse")