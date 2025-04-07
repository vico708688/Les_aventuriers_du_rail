class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.train_cards = []          # Liste des cartes wagons
        self.destination_cards = []    # À ajouter plus tard
        self.routes = []               # Les routes prises
        self.remaining_trains = 45     # Par défaut

    def draw_card(self, card):
        self.train_cards.append(card)