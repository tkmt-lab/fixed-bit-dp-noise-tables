"""Generated mapping; caller supplies valid input index and uniform b-bit word."""
BITS = 4
MAP = [[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

def sample_from_bits(d, word):
    return MAP[d][word]
