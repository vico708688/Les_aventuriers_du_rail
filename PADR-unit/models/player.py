class Player:
    """
    Représente un joueur humain (ou IA). Gère l’état courant de son jeu : cartes, objectifs, score, routes prises, etc.

    Attributs
    ---------

    name : nom du joueur
    color : couleur du joueur sur le plateau
    train_cards : cartes wagon possédées
    destination_cards : objectifs non accomplis
    accomplished_objectives : objectifs déjà réussis
    score : score actuel du joueur
    routes : liste des routes prises
    is_ai : booléen indiquant si ce joueur est une IA
    remaining_trains : nombre de wagons restants
    action_done : booléen indiquant si une action a été jouée ce tour

    Méthods
    -------

    draw_card(card)
        Ajoute une carte card à la main du joueur.
    add_destination_card(card)
        Ajoute un objectif card à la main du joueur.
    """
    def __init__(self, name, color, is_ai=False):
        self.name = name
        self.color = color
        self.train_cards = []
        self.destination_cards = []
        self.routes = []
        self.remaining_trains = 45
        self.score = 0
        self.accomplished_objectives = []
        self.action_done = False
        self.is_ai = is_ai

    def draw_card(self, card):
        """"
        Si il y a une carte, ajoute une carte card à la main du joueur.
        """
        if card is not None:
            self.train_cards.append(card)

    def add_destination_card(self, card):
        """
        Si il y a une carte, ajoute un objectif card à la main du joueur.
        """
        if card is not None:
            self.destination_cards.append(card)

    def __repr__(self):
        return f'Player {self.name}'