from .player import Player
import random
from data.data import WAGON_COLORS
from collections import Counter
import json

class AIPlayer(Player):
    def __init__(self, name, color, game, strategy):
        super().__init__(name, color, is_ai=True)
        self.game = game
        self.strategy = strategy  # Instance d'une stratégie IA

    def coups_possibles(self):
        return self.strategy.coups_possibles()

    def play_move(self):
        return self.strategy.play_move(self.game)

    # A FAIRE
    def draw_objective(self):
        return self.strategy.draw_objective(self.game)

class RandomAIStrategy:
    def coups_possibles(self, game):
        player = game.current_player

        possible_moves = []

        # 1. Piocher une carte wagon face cachée
        if game.train_deck:
            possible_moves.append(("draw_train_card", None))

        # 2. Piocher une carte visible
        for idx, card in enumerate(game.visible_cards):
            possible_moves.append(("draw_visible_card", idx))

        # 3. Piocher des cartes destination
        if len(game.destinations) >= 3:
            possible_moves.append(("draw_destinations", None))

        # 4. Revendiquer une route - PARTIE CRUCIALE
        cards_counter = Counter([c.lower() for c in player.train_cards])
        locos = cards_counter.get("locomotive", 0)

        #print(f"\n{player.name} possède: {dict(cards_counter)} (total: {len(player.train_cards)} cartes)")

        for route in game.routes:
            city1, city2 = route.city1, route.city2
            length = route.length
            color = route.color.lower()

            # Vérifier si la route est déjà prise
            if route.claimed_by is not None:
                continue

            # Vérifier si l'IA a assez de wagons
            if len(player.train_cards) < length:
                continue

            # Pour les routes grises
            if color == "gray":
                for c in WAGON_COLORS:
                    if c == "locomotive":
                        continue
                    count = cards_counter.get(c, 0)
                    if count + locos >= length:
                        possible_moves.append(("claim_route", (city1, city2, c, length)))
                        #print(f"Route possible (gris): {city1}-{city2} avec {c} ({count}+{locos} locos)")
                        break
            else:
                # Pour les routes colorées
                count = cards_counter.get(color, 0)
                if count + locos >= length:
                    possible_moves.append(("claim_route", (city1, city2, color, length)))
                    #print(f"Route possible ({color}): {city1}-{city2}")

        #print(f"Total coups possibles: {len(possible_moves)}")
        return possible_moves

    def play_move(self, game):
        # Pioche des objectifs si nécessaire
        if len(game.current_player.destination_cards) == 0:
            game.draw_objectives()
            return

        possible_moves = self.coups_possibles(game)
        #print(f"\nCoups possibles pour {game.current_player.name}:")
        # for i, (action, param) in enumerate(possible_moves):
        #     print(f"{i}. {action} {param if param else ''}")

        if not possible_moves:
            return

        move = random.choice(possible_moves)
        # print("coup choisi : ", move)
        action, param = move

        if action == "draw_train_card":
            nb_tirages = random.randint(1, 2)

            for i in range(nb_tirages):
                game.draw_card(0)
        elif action == "draw_visible_card":
            nb_tirages = random.randint(1, 2)

            for i in range(nb_tirages):
                card_number = random.randint(0, 4)
                game.draw_visible_card(card_number, 0)
        elif action == "draw_destinations":
            game.draw_objectives()
        elif action == "claim_route":
            city1, city2, color, length = param
            # Trouver la route correspondante dans les routes
            for route in game.routes:
                if route.is_between(city1, city2):
                    #print(f"\n{game.current_player.name} tente de prendre {city1}-{city2} ({color})")
                    game.claim_route(city1, city2, [route])
                    break

    def draw_objective(self, game):
        pass


import heapq


class OptiAIStrategy:
    """
        Cette classe a pour but de créer une stratégie qui
        cherche le chemin le plus court par l'utilisation
        de l'algorithme de Dijkstra
    """

    def is_route_useful(self, player, city1, city2):
        # Construction du graphe actuel des routes du joueur
        graph = {}
        for route in player.routes:
            city1 = route.city1
            city2 = route.city2
            graph.setdefault(city1, set()).add(city2)
            graph.setdefault(city2, set()).add(city1)

        # Ajout temporaire de la route candidate
        graph.setdefault(city1, set()).add(city2)
        graph.setdefault(city2, set()).add(city1)

        # Fonction de recherche simple
        def dfs(start, end):
            visited = set()
            stack = [start]
            while stack:
                node = stack.pop()
                if node == end:
                    return True
                if node not in visited:
                    visited.add(node)
                    stack.extend(neigh for neigh in graph.get(node, []) if neigh not in visited)
            return False

        # Vérifie chaque objectif complexe
        for obj in player.destination_cards:
            cities = obj.get("cities")
            if not cities or len(cities) < 2:
                continue

            for i in range(len(cities) - 1):
                start = cities[i]
                end = cities[i + 1]
                if not dfs(start, end):
                    # Si ce lien n'existe pas encore, la route candidate pourrait aider à le compléter
                    if (start == city1 and end == city2) or (start == city2 and end == city1):
                        return True  # C'est exactement le lien manquant
                    # Même si ce n'est pas le lien direct, peut-être que cette route crée un chemin intermédiaire
                    # => donc on peut être conservateur et renvoyer True dès qu’un segment est incomplet
                    return True

        return False  # Tous les segments sont déjà complétés => cette route n’aide pas

    def build_graph_from_routes(self, routes):  # Création du graphe utile pour l'implémentation de l'algo de Dijkstra
        graph = {}
        for route in routes:
            c1, c2 = route.city1, route.city2
            length = route.length
            graph.setdefault(c1, []).append((c2, length))
            graph.setdefault(c2, []).append((c1, length))  # car bidirectionnel
        return graph

    def dijkstra(self, graph, start, end):
        # File de priorité : (coût total depuis start, ville actuelle, chemin parcouru)
        heap = [(0, start, [])]
        visited = set()

        while heap:
            (cost, current, path) = heapq.heappop(heap)

            if current in visited:
                continue
            visited.add(current)

            path = path + [current]

            if current == end:
                return path, cost

            for neighbor, weight in graph.get(current, []):
                if neighbor not in visited:
                    heapq.heappush(heap, (cost + weight, neighbor, path))

        return None, float('inf')  # Aucun chemin trouvé
