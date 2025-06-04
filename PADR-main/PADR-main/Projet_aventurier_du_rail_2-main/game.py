import random
from collections import Counter
import tkinter as tk
from tkinter import messagebox
import tkinter.simpledialog as simpledialog
from data.data import *
from models.player import Player
from models.AI import AIPlayer, RandomAIStrategy
import json


class Game:
    def __init__(self, players):
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
        self.train_deck = WAGON_COLORS * 12
        random.shuffle(self.train_deck)

        self.SCORE_TABLE = {}

        with open("data/destinations.json", "r", encoding="utf-8") as f:
            self.destinations = json.load(f)

        self.visible_cards = []
        for _ in range(5):
            if self.train_deck:
                self.visible_cards.append(self.train_deck.pop())

        self.routes = []

    def start_game(self):
        for player in self.players:
            for _ in range(4):
                if self.train_deck:
                    player.draw_card(self.train_deck.pop())

    def get_visible_cards(self):
        return self.visible_cards

    def draw_destination_cards(self, count=3):
        cards = []
        for _ in range(count):
            if self.destinations:
                cards.append(self.destinations.pop())
        return cards

    def draw_objectives(self):
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

    def is_route_useful(self, player, city1, city2):
        # Construction du graphe actuel des routes du joueur
        graph = {}
        for route in player.routes:
            graph.setdefault(route.city1, set()).add(route.city1)
            graph.setdefault(route.city2, set()).add(route.city2)

        # Ajout temporaire de la route candidate
        graph.setdefault(city1, set()).add(city2)
        graph.setdefault(city2, set()).add(city1)

        # Vérifie pour chaque objectif si un chemin existe
        def dfs(current, target, visited):
            if current == target:
                return True
            visited.add(current)
            for neighbor in graph.get(current, []):
                if neighbor not in visited and dfs(neighbor, target, visited):
                    return True
            return False

        for obj in player.destination_cards:
            start = obj.get("from") or obj.get("city1")
            end = obj.get("to") or obj.get("city2")
            if not start or not end:
                continue

            if dfs(start, end, set()):
                return True  # Cette route aide à atteindre un objectif

        return False  # Route inutile à tout objectif