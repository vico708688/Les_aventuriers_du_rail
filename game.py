import random
from data.data import WAGON_COLORS

class Game:
    def __init__(self, players):
        self.players = players
        self.current_player_index = 0
        self.train_deck = WAGON_COLORS * 12  # 12 cartes de chaque couleur
        random.shuffle(self.train_deck)

    def get_current_player(self):
        return self.players[self.current_player_index]

    def draw_train_card(self):
        if self.train_deck:
            return self.train_deck.pop()
        return None

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
