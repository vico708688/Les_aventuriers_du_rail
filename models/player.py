from game import Game

class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.train_cards = []          # Liste des cartes wagons
        self.destination_cards = []    # À ajouter plus tard
        self.routes = []               # Les routes prises
        self.remaining_trains = 45     # Par défaut
        self.score = 0

    def draw_cards(self, cards):
        for card in cards:
            self.train_cards.append(card)
            Game.draw_train_card(card)