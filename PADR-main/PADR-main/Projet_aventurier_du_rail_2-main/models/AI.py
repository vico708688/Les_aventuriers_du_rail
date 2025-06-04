from .player import Player
import random
from data.data import WAGON_COLORS
from collections import Counter

class AIPlayer(Player):
    def __init__(self, name, color, game, strategy):
        super().__init__(name, color, is_ai=True)
        self.game = game
        self.strategy = strategy  # Instance d'une stratégie IA

    def coups_possibles(self):
        return self.strategy.coups_possibles()

    def play_move(self):
        return self.strategy.play_move(self.game)

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

            if player.is_ai and not game.is_route_useful(player, city1, city2):
                continue

            # Vérifier si le joueur a assez de wagons
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
        print("coup choisi : ", move)
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

class GreedyAIStrategy:
    def coups_possibles(self, player, game):
        # Même méthode que ci-dessus
        return possible_moves

    def play_move(self, player, game):
        moves = self.coups_possibles(player, game)
        if not moves:
            game.next_turn()
            return False

        # Priorité aux routes longues
        claim_moves = [m for m in moves if m[0] == "claim_route"]
        if claim_moves:
            action, param = max(claim_moves, key=lambda m: m[1][3])  # tri par longueur
        else:
            action, param = random.choice(moves)

        # Exécution du coup comme dans RandomAIStrategy
        return True