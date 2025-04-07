import tkinter as tk
from tkinter import messagebox
from game import Game

class GameApp:
    def __init__(self, root, players):
        self.root = root
        self.root.title("Les Aventuriers du Rail - USA")
        self.root.geometry("500x500")
        self.root.minsize(500, 500)

        self.game = Game(players)

        self.setup_ui()

    def setup_ui(self):
        # Titre
        title_label = tk.Label(self.root, text="Les Aventuriers du Rail - USA", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # Affichage des joueurs
        self.player_label = tk.Label(self.root, text=f"Tour de : {self.game.get_current_player().name}", font=("Helvetica", 12))
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
        card = self.game.draw_train_card()

        if card:
            player = self.game.get_current_player()
            player.draw_card(card)

            self.update_hand_display()
            # messagebox.showinfo("Carte piochée", f"{player.name} a pioché une carte {card} !")
        else:
            messagebox.showinfo("Pioche vide", "Il n'y a plus de cartes à piocher.")


    def update_hand_display(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        for card in self.game.get_current_player().train_cards:
            card_label = tk.Label(self.cards_frame, text=card, relief=tk.RIDGE, borderwidth=2, padx=5, pady=2)
            card_label.pack(side=tk.LEFT, padx=3)

    def next_turn(self):
        self.game.next_turn()
        self.update_turn_display()
        self.update_hand_display()

    def update_turn_display(self):
        self.player_label.config(text=f"Tour de : {self.game.get_current_player().name}")