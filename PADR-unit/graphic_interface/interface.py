from collections import Counter
from PIL import Image, ImageTk
import math

import tkinter as tk
from tkinter import messagebox
from tkinter.simpledialog import askstring

from data.data import WAGON_COLORS
from game import Game
from histo import Historique


class GameApp:
    """
    Auteurs :

        - Dubedout Thomas
        - Oudin Victor

    GameApp est la classe principale de l'interface graphique du jeu "Les Aventuriers du Rail - USA".
    Elle s'appuie sur Tkinter pour afficher la carte, les cartes des joueurs, les objectifs,
    et gérer les interactions (pioche, revendication de routes, changement de tour, etc.).

    Attributs
    ----------
    root : fenêtre principale Tkinter
    game : instance de la classe Game

    Methods
    -------

    INITIALISATION :

    setup_ui()
        Crée toute la structure graphique (cadres, labels, boutons, canvas)
    init()
        Lance le jeu et gère la distribution initiale des objectifs aux joueurs

    INTERACTION CARTE :

    draw_graph()
        - Affiche les routes et villes sur le canevas
        - Gère les routes doubles avec des décalages visuels
        - Affiche les longueurs de route et la couleur du joueur si revendiquée
    on_canvas_click()
        Gère la sélection de deux villes pour revendiquer une route
    attempt_claim_route()
        Demande confirmation et prépare les routes libres entre deux villes
    choose_color_from_deck(length)
        Sélectionne une couleur pour revendiquer une route grise
    choose_road(roads)
        Permet de choisir une route en cas de route double
    claim_route()
        Appelle la logique de jeu pour revendiquer une route

    TIRAGE CARTE :

    show_popup_objective_cards(nb_min_cartes_a_tirer)
        Affiche la popup de choix des cartes objectif
    on_draw_objectives_click(nb_min_cartes_a_tirer=1)
        Test si le joueur a déjà réalisé une action, dans le cas contraire,
        appel de show_popup_objective_cards
    on_draw_card_click()
        Appelle la logique de jeu pour piocher une carte dans la pioche
    on_draw_visible_card_click(i)
        Appelle la logique de jeu pour piocher la i-ème carte visible

    UPDATE :

    update_objectives_display()
        Met à jour la liste des objectifs non encore réalisés
    update_objectif_accompli()
        Vérifie les objectifs réussis, les transfère, et ajoute les points
    update_accomplished_display()
        Affiche les objectifs déjà accomplis
    update_turn_display()
        Met à jour le nom et score du joueur actuel
    update_visible_cards()
        Met à jour les cartes visibles
    update_hand_display()
        Met à jour la main du joueur
    update_all()
        Appel groupé de tous les update_*()

    CHANGEMENT DE TOUR :

    next_turn()
        Passe au joueur suivant ; si IA, exécute automatiquement son tour

    FIN DE PARTIE :

    show_final_scores() :
        - Ferme la fenêtre principale
        - Crée une nouvelle fenêtre plein écran
        - Affiche les scores triés
        - Permet de quitter le jeu
    """
    def __init__(self, root, game):
        """
        Initialise l'interface graphique et le jeu, et configure la fenêtre principale.

        Appelle setup_ui() pour construire l'interface
        Appelle init() pour démarrer le jeu

        Parameters
        ----------
        root : fenêtre principale Tkinter
        game : instance de la classe Game
        """
        # Création de la fenètre principale
        self.root = root
        self.root.title("Les Aventuriers du Rail - USA")
        self.root.attributes('-fullscreen', True)

        root.update()

        self.larg_left_col = 200
        self.width_canvas = self.root.winfo_width() - self.larg_left_col
        self.height_canvas = self.root.winfo_height()

        self.bg_image_tk = None  # Stockage image fond

        self.selected_cities = []
        self.card_buttons = []  # Boutons pour les cartes visibles

        # Création de l'intance de Game
        self.game = game
        self.historique = Historique(self.game)
        # Initialisation de la partie
        self.setup_ui()
        self.init()

    # ----------------------------------- INITIALISATION ----------------------------------------------
    def setup_ui(self):
        """
        Construit tous les composants Tkinter (cadres, boutons, labels, canvas) :
            - Colonne gauche : infos du joueur, cartes, objectifs
            - Colonne droite : carte du jeu (canvas)
        """
        self.card_images = {
            color: ImageTk.PhotoImage(Image.open(f"data/{color}.jpg").resize((25, 12)))
            for color in WAGON_COLORS
        }

        # Cadre principal horizontal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Colonne gauche : Infos joueur
        # Canvas défilant à gauche
        left_canvas = tk.Canvas(main_frame, width=self.larg_left_col)
        left_canvas.pack(side=tk.LEFT, fill=tk.Y)
        left_canvas.pack_propagate(False)

        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=left_canvas.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # Frame contenant tous les éléments
        left_frame = tk.Frame(left_canvas)
        left_canvas.create_window((0, 0), window=left_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=scrollbar.set)

        # Mise à jour du scroll lorsque le contenu change
        def on_configure(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))

        left_frame.bind("<Configure>", on_configure)

        # Activer le scroll avec la molette
        def _on_mousewheel(event):
            left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        left_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Colonne droite : Carte
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Joueur actuel
        self.player_label = tk.Label(left_frame, text="", font=("Helvetica", 14, "bold"))
        self.player_label.pack(pady=10)

        # Boutons d'action
        actions_frame = tk.Frame(left_frame)
        actions_frame.pack(pady=15)

        tk.Button(actions_frame, text="Piocher wagon", command=self.on_draw_card_click).pack(pady=2)
        tk.Button(actions_frame, text="Piocher objectif", command=self.on_draw_objectives_click).pack(pady=2)
        tk.Button(actions_frame, text="Passer tour", command=self.next_turn).pack(pady=2)
        tk.Button(actions_frame, text="Quitter plein écran",
                  command=lambda: self.root.attributes("-fullscreen", False)).pack(pady=2)
        tk.Button(actions_frame, text="Fin de la partie",
                  command=self.action_quitter_enregistre_fichier).pack(side=tk.BOTTOM, pady=10)

        # Cartes visibles
        self.visible_label = tk.Label(left_frame, text="Cartes visibles :", font=("Helvetica", 12), anchor="center",
                                      justify="center")
        self.visible_label.pack(pady=10)
        self.visible_frame = tk.Frame(left_frame)
        self.visible_frame.pack()

        # Cartes wagon
        self.hand_label = tk.Label(left_frame, text="Cartes en main :", font=("Helvetica", 12), anchor="center", justify="center", pady=2)
        self.hand_label.pack(pady=10)
        self.cards_frame = tk.Frame(left_frame)
        self.cards_frame.pack(pady=5)

        # Objectifs
        self.objectives_label = tk.Label(left_frame, text="Objectifs :", font=("Helvetica", 12), anchor="center", justify="center")
        self.objectives_label.pack(pady=10)
        self.objectives_frame = tk.Frame(left_frame)
        self.objectives_frame.pack()

        # Objectifs réussis
        self.accomplished_label = tk.Label(left_frame, text="Objectifs atteints :", font=("Helvetica", 12), anchor="center", justify="center")
        self.accomplished_label.pack(pady=10)
        self.accomplished_frame = tk.Frame(left_frame)
        self.accomplished_frame.pack()

        # Canvas carte (grande zone)
        self.canvas = tk.Canvas(right_frame, width=self.width_canvas, height=self.height_canvas, bg="white")
        self.canvas.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def init(self):
        """
        Lance la partie, distribue les cartes objectifs aux joueurs, et prépare le premier tour.
        """
        self.game.start_game()
        self.update_all()
        for _ in self.game.players:
            self.on_draw_objectives_click(2)
            self.game.train_card_draw_count = 0
            self.game.next_player()
            self.update_hand_display()
            self.update_turn_display()
            self.update_objectives_display()
            self.game.current_player.action_done = False

    # ---------------------------------- INTERACTION CARTE --------------------------------------------
    def draw_graph(self):
        """
        Dessine le fond de carte, les routes (y compris les doubles) et les villes.
        Gestion graphique des routes doubles (décalage)
        Affichage des routes revendiquées par couleur
        """
        city_coords = {
            entry["city"]: (
                entry["i"] / 100 * self.width_canvas,
                self.height_canvas - entry["j"] / 100 * self.height_canvas
            )
            for entry in self.game.villes
        }

        # Ne supprime que le graphe, laisse l'image
        self.canvas.delete("graph")

        image = Image.open("data/USA_map.jpg").resize((int(self.width_canvas), int(self.height_canvas)))
        self.bg_image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw")

        # Regrouper les routes par paire de villes (pour gérer les doubles routes)
        route_groups = []
        for route in self.game.routes:
            found = False
            for group in route_groups:
                if route.is_between(group[0].city1, group[0].city2):
                    group.append(route)
                    found = True
                    break
            if not found:
                route_groups.append([route])

        for group in route_groups:
            route = group[0]
            city1, city2 = route.city1, route.city2

            if city1 in city_coords and city2 in city_coords:
                x1, y1 = city_coords[city1]
                x2, y2 = city_coords[city2]
                dx, dy = x2 - x1, y2 - y1
                length = math.hypot(dx, dy)
                offset_x, offset_y = -dy / length * 6, dx / length * 6  # perpendiculaire

                for i, route in enumerate(group):
                    shift = (i - (len(group) - 1) / 2)
                    ox = offset_x * shift
                    oy = offset_y * shift

                    draw_color = route.color
                    if route.claimed_by:
                        draw_color = route.claimed_by.color

                    self.canvas.create_line(
                        x1 + ox, y1 + oy, x2 + ox, y2 + oy,
                        fill=draw_color, width=4, tags="graph"
                    )

                    if not route.claimed_by:
                        mx, my = (x1 + x2) / 2 + ox, (y1 + y2) / 2 + oy
                        self.canvas.create_text(
                            mx, my, text=str(route.length),
                            font=("Helvetica", 10, 'bold'),
                            fill="darkgreen", tags="graph"
                        )

        # Dessiner les villes
        for city, (x, y) in city_coords.items():
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5,
                                    fill="lightblue", outline="black", tags="graph")
            self.canvas.create_text(x, y - 10, text=city,
                                    font=("Helvetica", 11, 'bold'),
                                    fill="black", tags="graph")

        self.city_coords = city_coords
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.selected_cities = []

    def on_canvas_click(self, event):
        """
        Gère les clics sur les villes de la carte.
        Sélectionne une ville si cliquée
        Si deux villes sont sélectionnées, propose de revendiquer la route correspondante
        """
        # Déterminer quelle ville est cliquée
        for city, (x, y) in self.city_coords.items():
            if abs(event.x - x) < 8 and abs(event.y - y) < 8:
                self.selected_cities.append(city)

                # Ajouter un cercle rouge temporaire
                self.canvas.create_oval(x - 8, y - 8, x + 8, y + 8, outline="red", width=2)
                break

        if len(self.selected_cities) == 2:
            city1, city2 = self.selected_cities

            self.selected_cities.clear()

            # Tenter de revendiquer la route
            self.attempt_claim_route(city1, city2)
            self.update_all()

    def attempt_claim_route(self, city1, city2):
        """
        Vérifie quelles routes sont libres entre deux villes et demande confirmation au joueur.

        Parameters
        ----------

        :param city1: ville de départ.
        :param city2: ville d'arrivée.
        """
        roads = []
        for route in self.game.routes:
            if route.is_between(city1, city2) and route.claimed_by is None:
                roads.append(route)
        answer = tk.messagebox.askyesno("Revendiquer la route", f"{city1} ↔ {city2} ?")
        if len(roads) == 0:
            return
        if answer:
            self.claim_route(roads)
        return

    def choose_color_from_deck(self, length):
        """
        Popup de sélection de couleur pour revendiquer une route grise.
        Le joueur choisit une couleur de sa main pour revendiquer une route grise.
        S'il n'a pas assez de cartes de cette couleur, on complète avec des locomotives.

        :param length: longueur de la route à revendiquer
        :return: liste des cartes à consommer ou None si refus
        """
        player = self.game.current_player
        hand = player.train_cards

        # Compter les cartes par couleur
        color_counts = {}
        for card in hand:
            color_counts[card] = color_counts.get(card, 0) + 1

        # Liste des couleurs jouables (hors locomotive)
        colors_in_hand = [c for c in color_counts if c != "locomotive"]

        if not colors_in_hand:
            messagebox.showwarning("Erreur", "Vous n'avez pas de couleur disponible pour prendre une route grise.")
            return None

        # Choix via popup
        choice = askstring("Choix de couleur", f"Choisissez une couleur parmi : {', '.join(colors_in_hand)}")

        if not choice or choice not in colors_in_hand:
            messagebox.showinfo("Annulé", "Aucune couleur valide choisie.")
            return None

        chosen_count = color_counts.get(choice, 0)
        joker_count = color_counts.get("locomotive", 0)

        if chosen_count + joker_count < length:
            messagebox.showwarning("Pas assez de cartes",
                                   f"Vous n'avez pas assez de cartes {choice} + jokers pour prendre cette route.")
            return None

        # Sélection des cartes à retirer
        to_remove = []
        for card in hand:
            if card == choice and len(to_remove) < length:
                to_remove.append(card)
        for card in hand:
            if card == "locomotive" and len(to_remove) < length:
                to_remove.append(card)

        return to_remove

    def choose_road(self, roads):
        """
        Le joueur choisit l'une des routes possibles entre deux villes (routes doubles).
        :param roads: liste des routes entre deux villes
        :return: la route choisie (dict) ou None
        """

        # Créer une chaîne pour les options
        if roads[0].get("color") == 'gray':
            return roads[0]
        options = []
        for idx, road in enumerate(roads):
            col = road.get("color")
            length = road.get("length")
            options.append(f"{idx + 1}. {col} ({length})")

        choice = askstring("Choix de route", "Choisissez la route :\n" + "\n".join(options))

        if not choice or not choice.isdigit():
            return None

        index = int(choice) - 1
        if 0 <= index < len(roads):
            return roads[index]
        return None

    def claim_route(self, route):
        """
        Appel de la logique interne pour revendiquer la route et met à jour le score et l'affichage si le joueur n'a pas déjà fait une action.
        """
        if self.game.ended:
            self.show_final_scores()

        if not self.game.current_player.action_done:
            self.game.current_player.action_done = True
            self.game.claim_route(route)
            self.draw_graph()
            self.update_objectif_accompli()
        else:
            messagebox.showinfo("Limite atteinte", "Vous avez déjà réalisé une action.")
            return

    # ------------------------------------ TIRAGE CARTE -----------------------------------------------
    def show_popup_objective_cards(self, nb_min_cartes_a_tirer):
        """
        Affiche une fenêtre de sélection de 1 à 3 cartes objectifs tirées.
        Le joueur doit en garder au moins nb_min_cartes_a_tirer

        :param nb_min_cartes_a_tirer: nombre de cartes objectifs minimum à tirer
        """
        if not self.game.current_player.is_ai:
            top = tk.Toplevel(self.root)
            top.title("Choisissez vos objectifs")
            top.grab_set()

            tk.Label(top, text=f"{self.game.current_player.name}, choisissez entre {nb_min_cartes_a_tirer} et 3 objectifs :", font=("Helvetica", 12)).pack(
                pady=10)

            vars = []
            initial_destinations = self.game.draw_destination_cards(3)
            for obj in initial_destinations:
                var = tk.IntVar()
                if "cities" in obj:
                    city_text = f"{obj['cities'][0]} → {obj['cities'][-1]} ({obj['value']} pts)"
                else:
                    city_text = f"{obj['city1']} → {obj['city2']} ({obj['value']} pts)"
                cb = tk.Checkbutton(top, text=city_text, variable=var)
                cb.pack(anchor="w")
                vars.append((var, obj))

            def validate():
                selected = [obj for var, obj in vars if var.get() == 1]
                if len(selected) < nb_min_cartes_a_tirer:
                    messagebox.showwarning("Choix invalide", f"Vous devez choisir au moins {nb_min_cartes_a_tirer} destinations.")
                    return

                self.game.current_player.destination_cards.extend(selected)

                top.destroy()  # Ferme la fenêtre => libère `wait_window`

            tk.Button(top, text="Valider", command=validate).pack(pady=10)

            # Attente : bloque le déroulement ici tant que top est ouvert
            self.root.wait_window(top)

            # Assure que la fenêtre principale repasse devant
            self.root.lift()
        else:
            self.game.current_player.draw_objective()

    def on_draw_objectives_click(self, nb_min_cartes_a_tirer=1):
        """
        Déclenche la popup de choix d'objectifs si le joueur n'a pas déjà fait une action.
        """
        if not self.game.current_player.action_done:
            self.game.current_player.action_done = True
            nb_cards = len(self.game.current_player.destination_cards)
            self.show_popup_objective_cards(nb_min_cartes_a_tirer)

            # Si le joueur n'a pas pioché de carte, il n'a pas réalisé d'action
            if len(self.game.current_player.destination_cards) == nb_cards:
                self.game.current_player.action_done = False

            self.update_objectives_display()
        else:
            messagebox.showinfo("Limite atteinte", "Vous avez déjà réalisé une action.")
            return

    def on_draw_card_click(self):
        """
        Appel de la logique interne pour piocher une carte depuis la pioche principale si le joueur n'a pas déjà fait une action.
        """
        if not self.game.current_player.action_done:
            self.game.draw_card()
            self.game.train_card_draw_count += 1
            if self.game.train_card_draw_count == 2:
                self.game.current_player.action_done = True
            self.update_hand_display()
        else:
            messagebox.showinfo("Limite atteinte", "Vous avez déjà réalisé une action.")
            return

    def on_draw_visible_card_click(self, i):
        """
        Appel de la logique interne pour piocher une carte visible à l'index i si le joueur n'a pas déjà fait une action.
        """
        if not self.game.current_player.action_done:
            self.game.draw_visible_card(i)
            self.game.train_card_draw_count += 1
            if self.game.train_card_draw_count == 2:
                self.game.current_player.action_done = True
            self.update_hand_display()
            self.update_visible_cards()
        else:
            messagebox.showinfo("Limite atteinte", "Vous avez déjà réalisé une action.")
            return

    # -------------------------------------- UPDATE -----------------------------------------------
    def update_objectives_display(self):
        """
        Affiche les objectifs non encore accomplis du joueur courant.
        """
        for widget in self.objectives_frame.winfo_children():
            widget.destroy()

        current = self.game.current_player

        for i, obj in enumerate(current.destination_cards):
            if "cities" in obj:
                obj_text = " → ".join(obj["cities"]) + f" ({obj['value']} pts)"
            else:
                obj_text = f"{obj['city1']} → {obj['city2']} ({obj['value']} pts)"

            obj_label = tk.Label(self.objectives_frame, text=obj_text, relief=tk.SOLID, borderwidth=1, padx=4, pady=2)
            obj_label.pack(anchor="w", padx=3, pady=3)

    def update_objectif_accompli(self):
        """
        Vérifie si un objectif est rempli, le transfère, ajoute les points, et affiche un message.
        """
        current = self.game.current_player

        for obj in current.destination_cards[:]:
            if self.game.is_objective_completed(obj, self.game.current_player):
                current.destination_cards.remove(obj)
                current.accomplished_objectives.append(obj)

                # Ajouter les points de l'objectif
                current.score += obj['value']

                # Générer une description lisible de l’objectif
                if "cities" in obj:
                    label = " → ".join(obj["cities"])
                else:
                    label = f"{obj['city1']} → {obj['city2']}"

                # Message de succès
                messagebox.showinfo(
                    "Objectif accompli",
                    f"{current.name} a accompli l'objectif {label} et gagne {obj['value']} points!"
                )

        # Rafraîchir l'affichage
        self.update_objectives_display()
        self.update_accomplished_display()
        self.update_turn_display()

    def update_accomplished_display(self):
        """
        Affiche les objectifs accomplis dans la section dédiée.
        """
        for widget in self.accomplished_frame.winfo_children():
            widget.destroy()

        current = self.game.current_player
        for i, obj in enumerate(current.accomplished_objectives):
            if "cities" in obj:
                obj_text = " → ".join(obj["cities"]) + f" ({obj['value']} pts)"
            else:
                obj_text = f"{obj['city1']} → {obj['city2']} ({obj['value']} pts)"

            obj_label = tk.Label(self.accomplished_frame, text=obj_text, relief=tk.GROOVE, bg="lightgreen", padx=4,
                                 pady=2)
            obj_label.pack(padx=2, pady=2, anchor="w")

    def update_turn_display(self):
        """
        Met à jour l'affichage du joueur courant et de son score.
        """
        current = self.game.current_player
        self.player_label.config(text=f"Joueur : {current.name}\n Score : {current.score} points")

    def update_visible_cards(self):
        """
        Met à jour l'affichage des cartes visibles disponibles à la pioche.
        """
        # Supprimer les anciens boutons
        for btn in self.card_buttons:
            btn.destroy()
        self.card_buttons = []

        for idx, color in enumerate(self.game.visible_cards):
            if color is not None:
                img = self.card_images.get(color)
                btn = tk.Button(self.visible_frame, image=img, command=lambda i=idx: self.on_draw_visible_card_click(i))
                btn.grid(row=0, column=idx, padx=5)
                self.card_buttons.append(btn)

    def update_hand_display(self):
        """
        Met à jour les cartes wagons affichées dans la main du joueur.
        """
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        counts = Counter(self.game.current_player.train_cards)

        for idx, (color, count) in enumerate(counts.items()):
            row = idx // 4
            col = idx % 4
            frame = tk.Frame(self.cards_frame)
            frame.grid(row=row, column=col, padx=5, pady=5)

            if color is not None:
                img_label = tk.Label(frame, image=self.card_images[color])
                img_label.image = self.card_images[color]
                img_label.pack(side="top")

            count_label = tk.Label(frame, text=f"x{count}", font=("Arial", 10))
            count_label.pack(side="top")

    def update_all(self):
        """
        Met à jour tous les composants de l'interface.
        """
        self.update_hand_display()
        self.update_turn_display()
        self.update_objectives_display()
        self.update_visible_cards()
        self.update_accomplished_display()
        self.draw_graph()

    # -------------------------------- CHANGEMENT DE TOUR -------------------------------------------

    def next_turn(self):
        """
        Passe au joueur suivant et déclenche le tour d'une IA si besoin.
        """
        self.game.train_card_draw_count = 0
        self.game.next_player()
        self.update_all()
        self.game.current_player.action_done = False

        # Si c'est à l'IA de jouer, lance son tour
        if self.game.current_player.is_ai:
            self.game.current_player.play_move()
            self.update_objectif_accompli()
            if self.game.ended:
                self.show_final_scores()
                return
            self.game.train_card_draw_count = 0
            self.game.next_player()
            self.update_all()
            self.game.current_player.action_done = False

    # --------------------------------------- FIN ---------------------------------------------------

    def show_final_scores(self):
        """
        Affiche une fenêtre plein écran avec les scores finaux des joueurs, triés par score décroissant.
        Ferme l'ancienne interface et propose de quitter.
        """
        # Fermer la fenêtre principale
        self.root.destroy()

        # Nouvelle fenêtre plein écran
        top = tk.Tk()
        top.title("Fin de la partie - Scores")
        top.attributes('-fullscreen', True)  # Met en plein écran

        # Titre
        label_title = tk.Label(top, text="Scores finaux", font=("Helvetica", 30, "bold"))
        label_title.pack(pady=50)

        # Tri des joueurs par score décroissant
        sorted_players = sorted(self.game.players, key=lambda p: p.score, reverse=True)

        for player in sorted_players:
            name = player.name
            score = player.score
            lbl = tk.Label(top, text=f"{name} : {score} points", font=("Helvetica", 20))
            lbl.pack(pady=10)

        self.historique.ecriture_partie("historique.txt")
        # Fermeture du jeu
        btn_close = tk.Button(top, text="Quitter", font=("Helvetica", 16), command=top.quit)
        btn_close.pack(pady=50)

        top.mainloop()

    def action_quitter_enregistre_fichier(self):
        print("Bouton cliqué")
        historique = Historique(self.game)
        historique.ecriture_partie("historique.txt")
        messagebox.showinfo("Fin de la partie", "L'historique a été enregistré.")
        self.root.destroy()
# show_final_score : game.ended, game.end_game()