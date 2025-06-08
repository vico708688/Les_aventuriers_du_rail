class Route:
    def __init__(self, city1, city2, color, length):
        self.city1 = city1
        self.city2 = city2
        self.color = color.lower() if color else "gray"
        self.length = length
        self.claimed_by = None  # Joueur ayant revendiqué la route

    def is_between(self, c1, c2):
        return sorted([self.city1, self.city2]) == sorted([c1, c2])

    def set_claimed(self, player):
        self.claimed_by = player
