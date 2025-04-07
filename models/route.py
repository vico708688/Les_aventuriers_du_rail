class Route:
    def __init__(self, city1, city2, color, length):
        self.city1 = city1
        self.city2 = city2
        self.color = color
        self.length = length
        self.claimed_by = None
