from .player import Player
import random
from data.data import WAGON_COLORS
from collections import Counter

class AIPlayer(Player):
    def __init__(self, name, color, game, strategy):
        super().__init__(name, color, is_ai=True)
        self.game = game
        self.strategy = strategy

    def coups_possibles(self):
        return self.strategy.coups_possibles(self.game)

    def play_move(self):
        return self.strategy.play_move(self.game)

    def draw_objective(self):
        return self.strategy.draw_objective(self.game)

class RandomAIStrategy:
    def coups_possibles(self, game):
        player = game.current_player
        possible_moves = []

        # Pioche carte wagon face cachée
        if game.train_deck:
            possible_moves.append(("draw_train_card", None))

        # Pioche carte visible
        for idx, card in enumerate(game.visible_cards):
            possible_moves.append(("draw_visible_card", idx))

        # Pioche cartes destination
        if len(game.destinations) >= 3:
            possible_moves.append(("draw_destinations", None))

        cards_counter = Counter([c.lower() for c in player.train_cards])
        locos = cards_counter.get("locomotive", 0)

        for route in game.routes:
            city1, city2 = route.city1, route.city2
            length = route.length
            color = route.color.lower()

            if route.claimed_by is not None:
                continue

            for destination in player.destination_cards:
                city1 = destination.get("city1")
                city2 = destination.get("city2")

                if route.is_between(city1, city2):
                    continue

            if len(player.train_cards) < length:
                continue

            if color == "gray":
                for c in WAGON_COLORS:
                    if c == "locomotive":
                        continue
                    count = cards_counter.get(c, 0)
                    if count + locos >= length:
                        possible_moves.append(("claim_route", (city1, city2, c, length)))
                        break
            else:
                count = cards_counter.get(color, 0)
                if count + locos >= length:
                    possible_moves.append(("claim_route", (city1, city2, color, length)))

        return possible_moves

    def play_move(self, game):
        player = game.current_player

        if len(player.destination_cards) == 0:
            game.draw_objectives()  # Ne pas return immédiatement

        possible_moves = self.coups_possibles(game)
        if not possible_moves:
            return

        move = random.choice(possible_moves)
        action, param = move

        if action == "draw_train_card":
            nb_tirages = random.randint(1, 2)
            for _ in range(nb_tirages):
                game.draw_card()

        elif action == "draw_visible_card":
            nb_tirages = random.randint(1, 2)
            for _ in range(nb_tirages):
                idx = random.randint(0, 4)
                game.draw_visible_card(idx)

        elif action == "draw_destinations":
            game.draw_objectives()

        elif action == "claim_route":
            city1, city2, color, length = param
            for route in game.routes:
                if route.is_between(city1, city2) and route.claimed_by is None:
                    if player.is_ai and route in player.destination_cards:
                        continue  # sécurité supplémentaire
                    game.claim_route(city1, city2, [route])
                    break

    def draw_objective(self, game):
        game.draw_objectives()


class OptiAIStrategy:
    def __init__(self):
        pass

    def build_graph_from_routes(self, routes):
        graph = {}
        for route in routes:
            c1, c2 = route.city1, route.city2
            length = route.length
            graph.setdefault(c1, []).append((c2, length))
            graph.setdefault(c2, []).append((c1, length))
        return graph

    def dijkstra(self, graph, start, end):
        dist = {node: float('inf') for node in graph}
        dist[start] = 0
        prev = {node: None for node in graph}
        non_visites = dict(dist)

        while non_visites:
            courant = min(non_visites, key=lambda node: non_visites[node])
            if courant == end:
                break

            for voisin, poids in graph[courant]:
                if voisin in non_visites:
                    nouvelle_dist = dist[courant] + poids
                    if nouvelle_dist < dist[voisin]:
                        dist[voisin] = nouvelle_dist
                        prev[voisin] = courant
                        non_visites[voisin] = nouvelle_dist

            del non_visites[courant]

        chemin = []
        courant = end
        while courant is not None:
            chemin.insert(0, courant)
            courant = prev[courant]

        path = []
        for i in range(len(chemin) - 1):
            path.append((chemin[i], chemin[i + 1]))

        return path, dist[end]

    def play_move(self, game):
        player = game.current_player

        if not player.destination_cards:
            game.draw_objectives()
            return

        graph_all_routes = self.build_graph_from_routes(game.routes)

        for objective in player.destination_cards:
            cities = [objective.get("city1"), objective.get("city2")]
            if None in cities:
                continue

            start, end = cities
            path, dist_tot = self.dijkstra(graph_all_routes, start, end)

            for i in range(len(path)):
                city1 = path[i][0]
                city2 = path[i][1]

                route = next(
                    (r for r in game.routes if r.is_between(city1, city2) and r.claimed_by is None), None
                )
                if not route:
                    continue

                length = route.length
                color = route.color.lower()
                cards_counter = Counter([c.lower() for c in player.train_cards])
                locos = cards_counter.get("locomotive", 0)


                if len(player.train_cards) < length:
                    continue

                if color == "gray":
                    for c in WAGON_COLORS:
                        if c == "locomotive":
                            continue
                        count = cards_counter.get(c, 0)
                        if count + locos >= length:
                            game.claim_route(city1, city2, [route])
                            return
                else:
                    count = cards_counter.get(color, 0)
                    if count + locos >= length:
                        game.claim_route(city1, city2, [route])
                        return

        drawn = 0
        while drawn < 2 and game.train_deck:
            game.draw_card()
            drawn += 1

    def draw_objective(self, game):
        game.draw_objectives()
