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
        while True:
            self.piocher()
            self.prendre_route()
            self.choix_objectifs()

    def piocher(self):
        pass

    def prendre_route(self):
        pass

    def choix_objectifs(self):
        pass