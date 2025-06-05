class Player:
    def __init__(self, name, color, is_ai=False):
        self.name = name
        self.color = color
        self.train_cards = []
        self.destination_cards = []
        self.routes = []
        self.remaining_trains = 45
        self.score = 0
        self.accomplished_objectives = []
        self.is_ai = is_ai

    def draw_card(self, card):
        if card is not None:
            self.train_cards.append(card)

    def add_destination_card(self, card):
        self.destination_cards.append(card)

    def __repr__(self):
        return f'Player {self.name}'