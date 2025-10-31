import random
import logging

logger = logging.getLogger(__name__)

def roll_dice(num_sides: int) -> int:
    """
    Simulates rolling a single die with a specified number of sides.
    Args:
        num_sides: The number of sides on the die (e.g., 6 for a D6).
    Returns:
        An integer representing the result of the roll (1 to num_sides).
    """
    if num_sides < 1:
        raise ValueError("Number of sides must be at least 1.")
    return random.randint(1, num_sides)

def roll_d100() -> int:
    """
    Simulates rolling a 100-sided die, often used for percentage-based checks.
    Returns:
        An integer representing the result of the roll (1 to 100).
    """
    return random.randint(1, 100)

def chance_check(percentage: float) -> bool:
    """
    Performs a percentage-based success check.
    Args:
        percentage: The target percentage for success (e.g., 75 for 75%).
    Returns:
        True if the check succeeds, False otherwise.
    """
    if not (0 <= percentage <= 100):
        raise ValueError("Percentage must be between 0 and 100.")
    return roll_d100() <= percentage

# --- Example Usage (for testing the utility functions) ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Testing Dice Rolls ---")
    logger.info("Rolling a D6: %s", roll_dice(6))
    logger.info("Rolling a D20: %s", roll_dice(20))
    logger.info("Rolling a D100: %s", roll_d100())

    logger.info("--- Testing Chance Checks ---")
    success_chance = 75
    num_tests = 10
    logger.info("Testing %s%% chance %s times:", success_chance, num_tests)
    successful_checks = 0
    for i in range(num_tests):
        if chance_check(success_chance):
            logger.info("  Check %s: SUCCESS!", i+1)
            successful_checks += 1
        else:
            logger.info("  Check %s: FAILURE.", i+1)
    logger.info("Summary: %s out of %s checks succeeded.", successful_checks, num_tests)

    logger.info("--- Edge Cases ---")
    logger.info("0%% chance: %s", chance_check(0))
    logger.info("100%% chance: %s", chance_check(100))
    try:
        chance_check(101)
    except ValueError as e:
        logger.exception("Error for 101%% chance: %s", e)
