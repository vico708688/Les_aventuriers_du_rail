"""
Initialisation des joueurs

Distribution des cartes

Tour par tour : piocher, prendre une route, choisir des objectifs

Fin de partie
"""
from models.player import Player


class Game:
    def __init__(self):
        self.players = []

    def init_player(self, players):
        for i in range(len(players)):
            self.players.append(Player(players[0], players[1]))

    def distribution_cartes(self):
        pass

    def init_game(self, players):
        self.init_player(players)
        self.distribution_cartes()

    def start(self, players):
        self.init_game(players)
        self.play()

    def play(self):
        while all(self.players[i].remaining_trains > 2 for i in range(len(self.players))):
            for i in range(len(self.players)):
                self.piocher(self.players[i])
                self.prendre_route(self.players[i])
                self.choix_objectifs(self.players[i])

    def piocher(self, player):
        pass

    def prendre_route(self, player):
        pass

    def choix_objectifs(self, player):
        pass