class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.train_cards = []
        self.destination_cards = []
        self.claimed_routes = []
        self.remaining_trains = 45  # Par défaut
