import random

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
    print("--- Testing Dice Rolls ---")
    print(f"Rolling a D6: {roll_dice(6)}")
    print(f"Rolling a D20: {roll_dice(20)}")
    print(f"Rolling a D100: {roll_d100()}")

    print("\n--- Testing Chance Checks ---")
    success_chance = 75
    num_tests = 10
    print(f"Testing {success_chance}% chance {num_tests} times:")
    successful_checks = 0
    for i in range(num_tests):
        if chance_check(success_chance):
            print(f"  Check {i+1}: SUCCESS!")
            successful_checks += 1
        else:
            print(f"  Check {i+1}: FAILURE.")
    print(f"Summary: {successful_checks} out of {num_tests} checks succeeded.")

    print("\n--- Edge Cases ---")
    print(f"0% chance: {chance_check(0)}")
    print(f"100% chance: {chance_check(100)}")
    try:
        chance_check(101)
    except ValueError as e:
        print(f"Error for 101% chance: {e}")
