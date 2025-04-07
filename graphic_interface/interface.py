import tkinter as tk
from tkinter import messagebox
import random

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Les Aventuriers du Rail - USA")

        self.player_name = "Joueur 1"
        self.train_cards = []

        self.setup_ui()

    def setup_ui(self):
        # Titre
        title_label = tk.Label(self.root, text="Les Aventuriers du Rail - USA", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # Affichage du joueur
        self.player_label = tk.Label(self.root, text=f"Tour de : {self.player_name}", font=("Helvetica", 12))
        self.player_label.pack()

        # Bouton pour piocher une carte
        draw_button = tk.Button(self.root, text="Piocher une carte wagon", command=self.draw_card)
        draw_button.pack(pady=10)

        # Zone d'affichage des cartes en main
        self.hand_label = tk.Label(self.root, text="Cartes en main : ", font=("Helvetica", 12))
        self.hand_label.pack(pady=10)

        self.cards_frame = tk.Frame(self.root)
        self.cards_frame.pack()

    def draw_card(self):
        # Simule la pioche d'une carte wagon aléatoire
        card = random.choice(WAGON_COLORS)
        self.train_cards.append(card)

        # Met à jour l'affichage
        self.update_hand_display()

        # Message temporaire
        messagebox.showinfo("Carte piochée", f"Vous avez pioché une carte {card} !")

    def update_hand_display(self):
        # Efface les cartes affichées
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        # Affiche les cartes en main
        for card in self.train_cards:
            card_label = tk.Label(self.cards_frame, text=card, relief=tk.RIDGE, borderwidth=2, padx=5, pady=2)
            card_label.pack(side=tk.LEFT, padx=3)