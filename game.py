import random
from data.data import WAGON_COLORS

class Game:
    def __init__(self, players):
        self.players = players
        self.current_player_index = 0
        self.end = False
        self.train_deck = WAGON_COLORS * 12  # 12 cartes de chaque couleur + 12 cartes locomotives

    def start_game(self):
        # démarrage du jeu

        # on mélange les cartes
        random.shuffle(self.train_deck)

        # distribue 4 cartes wagon aux joueurs
        for player in self.players:
            player.draw_cards(self.train_deck[:4])

    def play_game(self):
        while not self.end:
            pass


    def get_current_player(self):
        return self.players[self.current_player_index]

    def draw_train_card(self):
        if self.train_deck:
            return self.train_deck.pop()
        return None

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
