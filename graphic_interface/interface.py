import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from game import Game
import random
import json


class GameApp:
    def __init__(self, root, players):
        self.root = root
        self.root.title("Les Aventuriers du Rail - USA")
        self.width = 1100
        self.height = 580
        self.larg_left_col = 250
        self.width_canvas = self.width - self.larg_left_col
        self.height_canvas = self.height
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.minsize(self.width, self.height)

        self.selected_cities = []

        with open("data/villes.json", "r", encoding="utf-8") as f:
            self.villes = json.load(f)

        with open("data/destinations.json", "r", encoding="utf-8") as f:
            self.routes = json.load(f)

        self.game = Game(players)
        self.game.start_game()
        self.bg_image_tk = None  # Stockage image fond

        self.setup_ui()

    def setup_ui(self):
        # 🧱 Cadre principal horizontal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ⬅️ Colonne gauche : Infos joueur
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

        # ➡️ Colonne droite : Carte
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 🧑‍💼 Joueur actuel
        self.player_label = tk.Label(left_frame, text="", font=("Helvetica", 14, "bold"))
        self.player_label.pack(pady=10)

        # 🎮 Boutons d'action
        actions_frame = tk.Frame(left_frame)
        actions_frame.pack(pady=15)

        tk.Button(actions_frame, text="Piocher wagon", command=self.draw_card).pack(pady=2)
        tk.Button(actions_frame, text="Piocher objectif", command=self.draw_objectives).pack(pady=2)
        tk.Button(actions_frame, text="Passer tour", command=self.next_turn).pack(pady=2)

        # 🎴 Cartes wagon
        self.hand_label = tk.Label(left_frame, text="Cartes en main :", font=("Helvetica", 12))
        self.hand_label.pack()
        self.cards_frame = tk.Frame(left_frame)
        self.cards_frame.pack(pady=5)

        # 🎯 Objectifs
        self.objectives_label = tk.Label(left_frame, text="Objectifs :", font=("Helvetica", 12))
        self.objectives_label.pack(pady=10)
        self.objectives_frame = tk.Frame(left_frame)
        self.objectives_frame.pack()

        # 🃏 Cartes visibles
        self.visible_label = tk.Label(left_frame, text="Cartes visibles :", font=("Helvetica", 12))
        self.visible_label.pack(pady=10)
        self.visible_frame = tk.Frame(left_frame)
        self.visible_frame.pack()

        # 🗺️ Canvas carte (grande zone)
        self.canvas = tk.Canvas(right_frame, width=self.width_canvas, height=self.height_canvas, bg="white")
        self.canvas.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Initialisation
        self.draw_graph()
        self.update_turn_display()
        self.update_hand_display()
        self.update_objectives_display()
        # self.update_visible_cards()

    def draw_graph(self):
        # Conversion coordonnées en pixels
        city_coords = {
            entry["city"]: (
                entry["i"] / 100 * self.width_canvas,
                self.height_canvas - entry["j"] / 100 * self.height_canvas
            )
            for entry in self.villes
        }

        self.canvas.delete("all")

        # Image de fond
        image = Image.open("data/USA_map.jpg").resize((int(self.width_canvas), int(self.height_canvas)))
        self.bg_image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw")

        # Dessiner les routes
        for route in self.routes:
            city1, city2 = route["city1"], route["city2"]
            points = route["length"]
            route_color = route.get("color", "gray")

            # Couleur par défaut
            line_color = "gray"

            # Si la route est revendiquée, utilise la couleur du joueur
            claimed = None
            for player in self.game.players:
                if (city1, city2) in player.routes or (city2, city1) in player.routes:
                    line_color = player.color
                    claimed = player
                    break
            else:
                # Sinon, utilise la couleur de la route si définie
                line_color = route_color if route_color != "gray" else "black"

            if city1 in city_coords and city2 in city_coords:
                x1, y1 = city_coords[city1]
                x2, y2 = city_coords[city2]
                self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=4)
                if not claimed:
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    self.canvas.create_text(mx, my, text=str(points), font=("Helvetica", 8), fill="darkred")

        # Villes (nœuds)
        for city, (x, y) in city_coords.items():
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="lightblue", outline="black")
            self.canvas.create_text(x, y - 10, text=city, font=("Helvetica", 7), fill="black")

        self.city_coords = city_coords
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.selected_cities = []

    # ---------------------------------- INTERACTION CARTE --------------------------------------------
    def on_canvas_click(self, event):
        # Déterminer quelle ville est cliquée
        for city, (x, y) in self.city_coords.items():
            if abs(event.x - x) < 8 and abs(event.y - y) < 8:
                self.selected_cities.append(city)

                # Ajouter un cercle rouge temporaire
                self.canvas.create_oval(x - 8, y - 8, x + 8, y + 8, outline="red", width=2)
                break

        if len(self.selected_cities) == 2:
            city1, city2 = self.selected_cities

            # Nettoyer la sélection visuelle
            # for circle in self.selected_cities:
            #     self.canvas.delete(circle)
            self.selected_cities.clear()

            # Tenter de revendiquer la route
            self.attempt_claim_route(city1, city2)
            self.update()

    def attempt_claim_route(self, city1, city2):
        if (city1, city2) in self.game.current_player.routes:
            return
        for route in self.routes:
            if {route["city1"], route["city2"]} == {city1, city2}:
                answer = tk.messagebox.askyesno("Revendiquer la route", f"{city1} ↔ {city2} ?")
                if answer:
                    self.claim_route(city1, city2, route)
                return

        # tk.messagebox.showinfo("Aucune route", f"Aucune route directe entre {city1} et {city2}")

    def claim_route(self, city1, city2, route):
        player = self.game.current_player
        length = route["length"]

        if len(player.train_cards) < length:
            messagebox.showwarning("Pas assez de cartes", f"{player.name} n’a pas {length} cartes.")
            return

        # A MODIFIER : SUPPRIMER LES CARTES SELECTIONNEES AU LIEU DES PREMIERES DU DECK
        del player.train_cards[:length]
        player.routes.append((city1, city2))
        player.score += self.game.SCORE_TABLE.get(length, length)

        messagebox.showinfo("Route revendiquée", f"{player.name} a pris la route {city1} ↔ {city2} !")

    def update(self):
        self.update_hand_display()
        self.update_turn_display()
        self.update_objectives_display()
        self.draw_graph()  # 🔁 met à jour visuellement la carte

    # -------------------------------------- TIRAGE -----------------------------------------------
    def draw_objectives(self):
        drawn = self.game.draw_destination_cards(3)

        if not drawn:
            tk.messagebox.showinfo("Objectifs", "Il n'y a plus d'objectifs à piocher.")
            return

        player = self.game.current_player

        # Interface temporaire de sélection (prend toutes les cartes pour l’instant)
        msg = "Objectifs tirés :\n" + "\n".join(
            f"{c['city1']} → {c['city2']} ({c['length']} pts)" for c in drawn
        )
        tk.messagebox.showinfo("Nouveaux objectifs", msg)

        for card in drawn:
            player.add_destination_card(card)

        self.update_objectives_display()

    def draw_card(self):
        self.game.player_draw_cards(1)
        self.update_hand_display()

    def visible_card_draw(self, index):
        self.game.visible_card_draw(index)
        self.update_hand_display()

    # -------------------------------------- UPDATE -----------------------------------------------
    def update_hand_display(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        current = self.game.current_player
        max_per_row = 4  # nombre de cartes par ligne

        for i, card in enumerate(current.train_cards):
            row = i // max_per_row
            col = i % max_per_row
            card_label = tk.Label(self.cards_frame, text=card, relief=tk.RIDGE, borderwidth=2, padx=5, pady=2)
            card_label.grid(row=row, column=col, padx=2, pady=2, sticky="w")

    def get_color_hex(self, color):
        color_map = {
            "red": "#d9534f",
            "blue": "#0275d8",
            "green": "#5cb85c",
            "yellow": "#f0ad4e",
            "black": "#292b2c",
            "white": "#f7f7f7",
            "purple": "#613d7c",
            "orange": "#f26522",
            "joker": "#cccccc",
            "gray": "#aaaaaa"
        }
        return color_map.get(color.lower(), "lightgray")

    def update_objectives_display(self):
        for widget in self.objectives_frame.winfo_children():
            widget.destroy()

        current = self.game.current_player
        max_per_row = 2  # par exemple : 2 objectifs par ligne

        for i, obj in enumerate(current.destination_cards):
            row = i // max_per_row
            col = i % max_per_row
            obj_text = f"{obj['city1']} → {obj['city2']} ({obj['length']} pts)"
            obj_label = tk.Label(self.objectives_frame, text=obj_text, relief=tk.SOLID, borderwidth=1, padx=4, pady=2)
            obj_label.grid(row=row, column=col, padx=3, pady=3, sticky="w")

    def update_turn_display(self):
        current = self.game.current_player
        self.player_label.config(text=f"Joueur : {current.name}")

    def update_hand_display(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        current = self.game.current_player
        max_per_row = 5  # nombre de cartes par ligne

        for i, card in enumerate(current.train_cards):
            row = i // max_per_row
            col = i % max_per_row
            card_label = tk.Label(self.cards_frame, text=card, relief=tk.RIDGE, borderwidth=2, padx=5, pady=2)
            card_label.grid(row=row, column=col, padx=2, pady=2)

    def next_turn(self):
        self.game.next_turn()
        self.update_turn_display()
        self.update_hand_display()
        self.update_objectives_display()