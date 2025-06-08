import random
# import json
import shlex
from collections import Counter, deque

import tkinter as tk
from tkinter import messagebox
import tkinter.simpledialog as simpledialog

from data.data import *
from models.route import Route
from models.player import Player
from models.AI import AIPlayer, RandomAIStrategy, OptiAIStrategy


class Game:
    def __init__(self, players, difficulty="Facile"):
        self.difficulty = difficulty  # Stocke la difficulté choisie

        # Players
        self.players = []
        for i, player_info in enumerate(players):
            player_info = {'name': player_info, 'is_ai': player_info == 'IA'}

            if player_info.get('is_ai'):
                if self.difficulty == "Facile":
                    strategy = RandomAIStrategy()
                else:
                    strategy = OptiAIStrategy()

                player = AIPlayer(
                    name=player_info['name'],
                    color=PLAYER_COLORS[i],
                    game=self,
                    strategy=strategy
                )
            else:
                player = Player(
                    name=player_info['name'],
                    color=PLAYER_COLORS[i]
                )

            self.players.append(player)

        self.current_player_index = 0

        # Cartes
        self.train_car = 0  # Nombre de cartes train déjà piochées ce tour
        self.train_deck = WAGON_COLORS * 12
        self.train_card_defaussees = [] # Les cartes train défaussées

        random.shuffle(self.train_deck)
        self.visible_cards = [self.train_deck.pop() for _ in range(5)]

        while self.visible_cards.count('locomotive') >= 3:
            self.train_deck = self.train_deck + self.visible_cards
            random.shuffle(self.train_deck)
            self.visible_cards = [self.train_deck.pop() for _ in range(5)]

        # Score
        self.SCORE_TABLE = {
            1: 1,
            2: 2,
            3: 4,
            4: 7,
            5: 10,
            6: 15
        }

        # Donnees
        self.villes = []
        self.routes = []
        self.objectifs = []
        self.ended = False

    def start_game(self):
        self.lit_dsl("data/config.dsl")

        for player in self.players:
            for _ in range(4):
                if self.train_deck:
                    player.draw_card(self.train_deck.pop())

    def end_game(self):
        self.ended = True

    def lit_dsl(self, filepath):
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # ignore les commentaires et les lignes vides

                # shlex.split respecte les guillemets
                parts = shlex.split(line)

                if parts[0] == "VILLE":
                    self.villes.append({
                        "city": parts[1],
                        "i": float(parts[2]),
                        "j": float(parts[3])
                    })
                elif parts[0] == "ROUTE":
                    self.routes.append(Route(parts[1], parts[2], parts[4], int(parts[3])))
                elif parts[0] == "OBJECTIF":
                    self.objectifs.append({
                        "city1": parts[1],
                        "city2": parts[2],
                        "value": int(parts[3])
                    })

    def draw_destination_cards(self, count=3):
        cards = []
        for _ in range(count):
            if self.objectifs:
                cards.append(self.objectifs.pop())
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
            f"{c['city1']} → {c['city2']} ({c['value']} pts)" for c in drawn
        )
        tk.messagebox.showinfo("Nouveaux objectifs", msg)

        for card in drawn:
            player.add_destination_card(card)

    def draw_card(self):
        for _ in range(1):
            card = self.draw_train_card()
            if card:
                self.current_player.draw_card(card)

    def draw_visible_card(self, index):
        # Si il n'y a plus de carte dans la pioche,
        # on mélange les cartes defaussées et on les met dans la pioche
        if len(self.train_deck) == 0:
            self.train_deck = self.train_card_defaussees.copy()
            random.shuffle(self.train_deck)
            self.train_card_defaussees.clear()

        if len(self.visible_cards) < 5 and len(self.train_deck) > 0:
            for card in range(self.visible_cards):
                if self.visible_cards[card] is None:
                    if len(self.train_deck) > 0:
                        self.visible_cards[card] = self.train_deck.pop()


        picked_card = self.visible_cards[index]
        if picked_card is None:
            self.current_player.action_done = False
            return
        self.current_player.train_cards.append(picked_card)

        if picked_card == "locomotive":
            self.current_player.action_done = True

        # Remplacer la carte visible par une nouvelle
        self.visible_cards[index] = self.draw_train_card()

        while self.visible_cards.count('locomotive') >= 3:
            self.train_deck = self.train_deck + self.visible_cards
            random.shuffle(self.train_deck)
            self.visible_cards = [self.train_deck.pop() for _ in range(5)]

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def draw_train_card(self):
        if self.train_deck:
            return self.train_deck.pop()
        return None

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def claim_route(self, city1, city2, routes):# Un même joueur ne peut pas prendre 2 routes reliant les 2 mêmes villes.
        player = self.current_player

        # SÉLECTION DE LA ROUTE SI PLUSIEURS OPTIONS
        if len(routes) > 1:
            # Construire une liste lisible des options
            route_options = [f"{i + 1}: {r.color.capitalize()} ({r.length})" for i, r in enumerate(routes)]
            prompt = f"Plusieurs routes disponibles entre {city1} et {city2} (Sélectionnez le numéro) :\n" + "\n".join(route_options)
            choice_str = simpledialog.askstring("Choix de la route", prompt)

            if not choice_str or not choice_str.isdigit() or not (1 <= int(choice_str) <= len(routes)):
                messagebox.showinfo("Annulé", "Aucune route valide sélectionnée.")
                player.action_done = False
                return

            route = routes[int(choice_str) - 1]
        else:
            route = routes[0]

        length = route.length
        route_color = route.color.lower()

        if player.remaining_trains - length <= 0:
            messagebox.showinfo("Annulé", "Plus assez de wagons.")
            self.end_game()
            return

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
                player.action_done = False
                return

            if len(possible_colors) > 1 and not player.is_ai:
                color_choice = simpledialog.askstring("Choix couleur",
                                                      f"Route grise. Couleurs possibles : {possible_colors}")
                if not color_choice or color_choice.lower() not in possible_colors:
                    messagebox.showinfo("Annulé", "Aucune couleur valide sélectionnée.")
                    player.action_done = False
                    return
                chosen_color = color_choice.lower()
            else:
                chosen_color = possible_colors[0]

        # ROUTE COULEUR FIXE
        else:
            chosen_color = route_color
            if color_counts.get(chosen_color, 0) + loco_count < length:
                messagebox.showwarning("Pas assez de cartes", f"{player.name} n’a pas assez de cartes {route_color}.")
                player.action_done = False
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

        # 3. Retirer le nombre de wagon égal à la longueur de la route
        player.remaining_trains -= length
        if player.remaining_trains <= 2:
            self.end_game()

        # 4. Retirer les cartes de la main et les defausses
        for card in chosen_cards:
            player.train_cards.remove(card)
            self.train_card_defaussees.append(card)

        # MISE À JOUR
        route.claimed_by = player
        player.routes.append(route)
        messagebox.showinfo("Route revendiquée",
                            f"{player.name} a pris la route {city1} ↔ {city2} ({route.color}) !")

    def is_objective_completed(self, obj, player):
        """
        Cette méthode permet de savoir si un objectif a été complété
         c'est à dire si la ville d'arrivée est bien celle indiquée
         sur la carte objectif.
        :param obj:
        :return:
        """
        graph = {}
        for route in player.routes:
            city1 = route.city1
            city2 = route.city2
            graph.setdefault(city1, []).append(city2)
            graph.setdefault(city2, []).append(city1)

        cities = obj.get("cities")
        if cities:
            for i in range(len(cities) - 1):
                if not self._bfs_path_exists(graph, cities[i], cities[i + 1]):
                    return False
            return True
        else:
            return self._bfs_path_exists(graph, obj.get("city1"), obj.get("city2"))

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

    def calculate_final_scores(self):
        for player in self.players:
            for obj in player.destination_cards:
                if "done" not in obj:  # Non réalisé
                    player.score -= obj["value"]

    def update_objective_score(self, player):
        for obj in player.destination_cards:
            if "done" not in obj and self.is_objective_completed(obj):
                player.score += obj["value"]
                obj["done"] = True  # Marquer comme fait
