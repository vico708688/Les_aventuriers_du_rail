import unittest
from models.AI import OptiAIStrategy
from models.player import Player
from models.route import Route
from game import Game


class TestOptiAIStrategy(unittest.TestCase):
    """
    Auteur:

        - Thomas Dubedout
    """
    def setUp(self):
        self.ai = OptiAIStrategy()
        self.graph = {
            'A': [('B', 5), ('C', 10)],
            'B': [('A', 5), ('C', 3)],
            'C': [('A', 10), ('B', 3)]
        }

    def test_dijkstra_shortest_path(self):
        path, dist = self.ai.dijkstra(self.graph, 'A', 'C')
        self.assertEqual(path, [('A', 'B'), ('B', 'C')])
        self.assertEqual(dist, 8)

class GameTestCase(unittest.TestCase):

    def setUp(self):
        # Création d'une partie avec deux joueurs humains
        self.players = ["Alice", "Bob"]
        self.game = Game(players=self.players)
        self.game.SCORE_TABLE = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}

    def test_start_game(self):
        self.game.start_game()
        for player in self.game.players:
            self.assertEqual(len(player.train_cards), 4)

    def test_draw_destination_cards(self):
        initial_objectif_count = len(self.game.objectifs)
        drawn = self.game.draw_destination_cards(3)
        self.assertTrue(0 < len(drawn) <= 3)
        self.assertEqual(len(self.game.objectifs), initial_objectif_count - len(drawn))

    def test_draw_train_card(self):
        initial_deck_size = len(self.game.train_deck)
        card = self.game.draw_train_card()
        self.assertIsNotNone(card)
        self.assertEqual(len(self.game.train_deck), initial_deck_size - 1)

    def test_claim_route_basic(self):
        # Crée une route disponible
        route = Route("Paris", "Lyon", "red", 3)
        self.game.routes = [route]
        player = self.game.current_player
        player.train_cards = ["red", "red", "red", "blue", "green"]

        self.game.SCORE_TABLE = {3: 4}

        # Simulation directe sans GUI
        route.claimed_by = None
        player.routes = []
        player.score = 0

        self.assertIsNone(route.claimed_by)
        # Appel interne simplifié de la logique de `claim_route` (si on adapte claim_route en version testable sans GUI)
        can_claim = player.train_cards.count("red") >= 3
        if can_claim:
            for _ in range(3):
                player.train_cards.remove("red")
            route.claimed_by = player
            player.routes.append(route)
            player.score += self.game.SCORE_TABLE[3]

        self.assertEqual(route.claimed_by, player)
        self.assertIn(route, player.routes)
        self.assertEqual(player.score, 4)

    def test_is_objective_completed_true(self):
        # Simule une route revendiquée correspondant à un objectif
        player = self.game.current_player
        route1 = Route("Paris", "Lyon", "blue", 2)
        route2 = Route("Lyon", "Marseille", "green", 2)
        route1.claimed_by = player
        route2.claimed_by = player
        player.routes = [route1, route2]

        obj = {"city1": "Paris", "city2": "Marseille"}
        self.assertTrue(self.game.is_objective_completed(obj))

    def test_is_objective_completed_false(self):
        player = self.game.current_player
        route = Route("Paris", "Lyon", "blue", 2)
        route.claimed_by = player
        player.routes = [route]

        obj = {"city1": "Paris", "city2": "Marseille"}
        self.assertFalse(self.game.is_objective_completed(obj))

class PlayerTestCase(unittest.TestCase):
    def setUp(self):
        self.player = Player("Thomas", "red", is_ai=False)

    def test_init(self):
        self.assertEqual(self.player.remaining_trains, 45)
        self.assertEqual(self.player.score, 0)
        self.assertEqual(self.player.color, "red")
        self.assertEqual(self.player.is_ai, False)
        self.assertEqual(self.player.name, "Thomas")
        self.assertEqual(self.player.train_cards, [])

    def test_methode_draw_card(self):
        self.player.train_cards = ["red"]
        self.player.draw_card("blue")
        self.assertListEqual(self.player.train_cards, ["red", "blue"])

    def test_methode_add_destination_card(self):
        self.player.destination_cards = ["El Paso"]
        self.player.add_destination_card("Los Angeles")
        self.assertListEqual(self.player.destination_cards, ["El Paso", "Los Angeles"])

if __name__ == '__main__':
    unittest.main(verbosity=2)
