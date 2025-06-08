class Route:
    """
    Auteur :

        - Oudin Victor

    Représente une route entre deux villes. Chaque route est définie par :
        - deux extrémités (city1, city2)
        - une couleur
        - une longueur (en wagons)
        - un éventuel propriétaire (claimed_by)

    Attributs
    ---------

    city1 : nom de la première ville
    city2 : nom de la deuxième ville
    color : couleur de la route
    length : longueur de la route (en wagons)
    claimed_by : joueur ayant revendiqué cette route (ou None si libre)

    Méthods
    -------

    is_between(v1, v2)
        Retourne True si la route est entre v1 et v2, False sinon.
    set_claimed(player)
        Définit le player comme étant le propriétaire de la route via claimed_by.
    """
    def __init__(self, city1, city2, color, length):
        self.city1 = city1
        self.city2 = city2
        self.color = color.lower() if color else "gray"
        self.length = length
        self.claimed_by = None  # Joueur ayant revendiqué la route

    def is_between(self, c1, c2):
        """
        Retourne True si la route est entre c1 et c2, False sinon.
        """
        return sorted([self.city1, self.city2]) == sorted([c1, c2])

    def set_claimed(self, player):
        """
        Définit le player comme étant le propriétaire de la route via claimed_by.
        """
        self.claimed_by = player
