import tkinter as tk
from tkinter import messagebox
import random
from data.data import *

class GameApp:
    def __init__(self, root, players):
        self.root = root
        self.root.title("Les Aventuriers du Rail - USA")

        self.players = players
        self.hands = {player[0]: [] for player in self.players}

        self.current_player_index = 0

        self.setup_ui()

    def setup_ui(self):
        # Titre
        title_label = tk.Label(self.root, text="Les Aventuriers du Rail - USA", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # Affichage des joueurs
        self.player_label = tk.Label(self.root, text=f"Tour de : {self.players[0][0]}", font=("Helvetica", 12))
        self.player_label.pack()

        # Bouton pour piocher une carte
        draw_button = tk.Button(self.root, text="Piocher une carte wagon", command=self.draw_card)
        draw_button.pack(pady=10)

        next_button = tk.Button(self.root, text="Tour suivant", command=self.next_turn)
        next_button.pack(pady=5)

        # Zone d'affichage des cartes en main
        self.hand_label = tk.Label(self.root, text="Cartes en main : ", font=("Helvetica", 12))
        self.hand_label.pack(pady=10)

        self.cards_frame = tk.Frame(self.root)
        self.cards_frame.pack()

    def draw_card(self):
        card = random.choice(WAGON_COLORS)
        current_player = self.players[self.current_player_index][0]

        self.hands[current_player].append(card)
        self.update_hand_display()

        messagebox.showinfo("Carte piochée", f"{current_player} a pioché une carte {card} !")

    def update_hand_display(self):
        # Efface les cartes affichées
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        # Affiche les cartes en main
        for card in self.train_cards:
            card_label = tk.Label(self.cards_frame, text=card, relief=tk.RIDGE, borderwidth=2, padx=5, pady=2)
            card_label.pack(side=tk.LEFT, padx=3)

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.update_turn_display()
        self.update_hand_display()

    def update_turn_display(self):
        current_player = self.players[self.current_player_index][0]
        self.player_label.config(text=f"Tour de : {current_player}")

    def update_hand_display(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        current_player = self.players[self.current_player_index][0]
        for card in self.hands[current_player]:
            card_label = tk.Label(self.cards_frame, text=card, relief=tk.RIDGE, borderwidth=2, padx=5, pady=2)
            card_label.pack(side=tk.LEFT, padx=3)
