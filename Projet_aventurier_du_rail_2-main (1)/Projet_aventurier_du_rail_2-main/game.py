import random
import json
from collections import Counter, deque

import tkinter as tk
from tkinter import messagebox
import tkinter.simpledialog as simpledialog

from data.data import *

from models.route import Route
from models.player import Player
from models.AI import AIPlayer, RandomAIStrategy


class Game:
    def __init__(self, players):
        # Player
        self.players = []
        for i, player_info in enumerate(players):
            player_info = {'name': player_info, 'is_ai': player_info == 'IA'}

            if player_info.get('is_ai'):
                # Créer une stratégie IA
                random_strategy = RandomAIStrategy()

                # Créer un joueur IA
                player = AIPlayer(
                    name=player_info['name'],
                    color=PLAYER_COLORS[i],
                    game=self,  # Pour que l'IA ait accès au jeu
                    strategy=random_strategy
                )
            else:
                player = Player(
                    name=player_info['name'],
                    color=PLAYER_COLORS[i]
                )

            # ajoute le joueur à la partie
            self.players.append(player)

        self.current_player_index = 0

        # Cartes
        self.train_card_draw_count = 0  # Nombre de cartes train déjà piochées ce tour
        self.destination_card_draw_count = 0  # Nombre de cartes destination déjà piochées ce tour
        self.train_deck = WAGON_COLORS * 12
        random.shuffle(self.train_deck)

        self.visible_cards = [self.draw_train_card() for _ in range(5)]

        # Score
        self.SCORE_TABLE = {}

        # Donnees
        with open("data/destinations.json", "r", encoding="utf-8") as f:
            self.destinations = json.load(f)

        with open("data/objectifs.json", "r", encoding="utf-8") as f_ob:
            self.objectif = json.load(f_ob)

        with open("data/villes.json", "r", encoding="utf-8") as f:
            self.villes = json.load(f)

        self.routes = [
            Route(route["city1"], route["city2"], route["color"], route["length"])
            for route in self.destinations
        ]

    def start_game(self):
        for player in self.players:
            for _ in range(4):
                if self.train_deck:
                    player.draw_card(self.train_deck.pop())

    def draw_destination_cards(self, count=3):
        cards = []
        for _ in range(count):
            if self.objectif:
                cards.append(self.objectif.pop())
        return cards

    def draw_objectives(self):
        """
            Un joueur peut utiliser son tour de jeu pour récupérer des cartes Destination supplémentaires.
            Pour cela, il doit prendre 3 cartes sur le dessus de la pile des cartes Destination.
            Il doit conserver au moins l’une des trois cartes, mais peut bien sûr en garder 2 ou même 3.
            S’il  reste moins de 3 cartes Destination dans la pile, le joueur ne peut prendre que le nombre de cartes disponibles.
            Chaque carte qui n’est pas conservée par le joueur est remise face cachée sous la pile.
        """
        drawn = self.draw_destination_cards(3)

        if not drawn:
            tk.messagebox.showinfo("Objectifs", "Il n'y a plus d'objectifs à piocher.")
            return

        player = self.current_player
        msg = "Objectifs tirés :\n" + "\n".join(
            f"{c['city1']} → {c['city2']} ({c['length']} pts)" for c in drawn
        )
        tk.messagebox.showinfo("Nouveaux objectifs", msg)

        for card in drawn:
            player.add_destination_card(card)

    def draw_card(self, draw_count):
        if draw_count >= 2:
            messagebox.showinfo("Limite atteinte", "Vous avez déjà pioché 2 cartes.")
            return

        self.player_draw_cards(1)

    def draw_visible_card(self, index, draw_count):
        if draw_count >= 2:
            messagebox.showinfo("Limite atteinte", "Vous avez déjà pioché 2 cartes.")
            return

        picked_card = self.visible_cards[index]
        self.current_player.train_cards.append(picked_card)

        # Remplacer la carte visible par une nouvelle
        if self.train_deck:
            self.visible_cards[index] = self.draw_train_card()
        else:
            self.visible_cards[index] = None  # ou une image vide

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def draw_train_card(self):
        if self.train_deck:
            return self.train_deck.pop()
        return None

    def player_draw_cards(self, nb_cards):
        for _ in range(nb_cards):
            card = self.draw_train_card()
            if card:
                self.current_player.draw_card(card)

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    # remettre les cartes jouées sous la pile de carte
    def claim_route(self, city1, city2, routes):
        player = self.current_player

        # SÉLECTION DE LA ROUTE SI PLUSIEURS OPTIONS
        if len(routes) > 1:
            # Construire une liste lisible des options
            route_options = [f"{i + 1}: {r.color.capitalize()} ({r.length})" for i, r in enumerate(routes)]
            prompt = f"Plusieurs routes disponibles entre {city1} et {city2} (Sélectionnez le numéro) :\n" + "\n".join(route_options)
            choice_str = simpledialog.askstring("Choix de la route", prompt)

            if not choice_str or not choice_str.isdigit() or not (1 <= int(choice_str) <= len(routes)):
                messagebox.showinfo("Annulé", "Aucune route valide sélectionnée.")
                return

            route = routes[int(choice_str) - 1]
        else:
            route = routes[0]

        length = route.length
        route_color = route.color.lower()

        cards = [c.lower() for c in player.train_cards]
        color_counts = Counter(cards)
        loco_count = color_counts.get("locomotive", 0)

        # ROUTE GRISE
        if route_color == "gray":
            possible_colors = [
                color for color in color_counts
                if color != "locomotive" and color_counts[color] + loco_count >= length
            ]

            if not possible_colors:
                messagebox.showwarning("Pas assez de cartes", f"{player.name} ne peut pas prendre cette route grise.")
                return

            if len(possible_colors) > 1 and not player.is_ai:
                color_choice = simpledialog.askstring("Choix couleur",
                                                      f"Route grise. Couleurs possibles : {possible_colors}")
                if not color_choice or color_choice.lower() not in possible_colors:
                    messagebox.showinfo("Annulé", "Aucune couleur valide sélectionnée.")
                    return
                chosen_color = color_choice.lower()
            else:
                chosen_color = possible_colors[0]

        # ROUTE COULEUR FIXE
        else:
            chosen_color = route_color
            if color_counts.get(chosen_color, 0) + loco_count < length:
                messagebox.showwarning("Pas assez de cartes", f"{player.name} n’a pas assez de cartes {route_color}.")
                return

        # Retirer exactement les cartes nécessaires
        to_remove = length
        chosen_cards = []

        # 1. Enlever les cartes de la couleur choisie
        for card in player.train_cards:
            if to_remove > 0 and card.lower() == chosen_color:
                chosen_cards.append(card)
                to_remove -= 1

        # 2. Compléter avec des locomotives si besoin
        if to_remove > 0:
            for card in player.train_cards:
                if to_remove > 0 and card.lower() == "locomotive":
                    chosen_cards.append(card)
                    to_remove -= 1

        # Retirer les cartes de la main
        for card in chosen_cards:
            player.train_cards.remove(card)

        # MISE À JOUR
        route.claimed_by = player
        player.routes.append(route)
        player.score += self.SCORE_TABLE.get(length, length)
        messagebox.showinfo("Route revendiquée",
                            f"{player.name} a pris la route {city1} ↔ {city2} ({route.color}) !")

    def is_objective_completed(self, obj):
        graph = {}
        for route in self.current_player.routes:
            city1 = route.city1
            city2 = route.city2
            graph.setdefault(city1, []).append(city2)
            graph.setdefault(city2, []).append(city1)

        cities = obj.get("cities")
        if cities:
            for i in range(len(cities) - 1):
                start = cities[i]
                end = cities[i + 1]
                if not self._bfs_path_exists(graph, start, end):
                    return False
            return True
        else:
            start, end = obj.get("city1"), obj.get("city2")
            return self._bfs_path_exists(graph, start, end)

    def _bfs_path_exists(self, graph, start, end):
        visited = set()
        queue = deque([start])
        while queue:
            city = queue.popleft()
            if city == end:
                return True
            visited.add(city)
            for neighbor in graph.get(city, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        return False