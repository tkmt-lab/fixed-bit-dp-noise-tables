"""Generated mapping; caller supplies valid input index and uniform b-bit word."""
BITS = 4
MAP = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 4, 4, 4, 4, 5], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 4, 4, 4, 4, 5], [1, 1, 1, 1, 1, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5], [1, 1, 1, 1, 1, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5], [1, 1, 1, 1, 1, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5], [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 4, 4, 4, 4, 5, 5]]

def sample_from_bits(d, word):
    return MAP[d][word]
