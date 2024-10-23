from numpy import random

def get_random_number(low_bound: float = 0.0, high_bound: float = 1.0) -> float:
    return random.uniform(low_bound, high_bound)