# Les_aventuriers_du_rail

Structure code :

les_aventuriers_du_rail/
│
├── main.py                     # Point d'entrée du jeu
├── game.py                     # Boucle principale et logique du jeu
│
├── models/                     # Les classes principales du jeu
│   ├── player.py               # Classe Joueur
│   ├── route.py                # Classe Route
│   ├── destination.py          # Classe Objectif / Destination
│   ├── train_card.py           # Carte Wagon
│   ├── destination_card.py     # Carte Destination
│   ├── board.py                # Plateau du jeu (liste des routes, etc.)
│   └── deck.py                 # Piles de cartes (wagons, destinations)
│
├── utils/                      # Fonctions utilitaires (ex: vérifications, affichages)
│   └── helpers.py
│
├── data/                       # Fichiers de données (JSON des villes, routes, etc.)
│   ├── routes.json
│   ├── destinations.json
│   └── config.json
│
├── ui/                         # (optionnel) Interface texte ou graphique (console, tkinter, etc.)
│   └── console_ui.py
│
└── README.md                   # Explications du projet
