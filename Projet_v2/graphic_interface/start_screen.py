from graphic_interface.interface import *
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class StartScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Les Aventuriers du Rail")

        # Récupérer les dimensions de l'écran
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Charger et redimensionner l'image de fond
        self.bg_image = Image.open("data/start_screen_bg.jpg")
        self.bg_image = self.bg_image.resize((self.screen_width, self.screen_height))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Créer un canvas pour l'interface
        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        root.attributes('-fullscreen', True)

        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        button_style = {
            'text': "Un ticket pour l'aventure",
            'font': ("Helvetica", 18, "bold"),
            'bg': "#e74c3c",
            'fg': "white",
            'activebackground': "#c0392b",
            'activeforeground': "white",
            'relief': tk.RAISED,
            'borderwidth': 3,
            'padx': 30,
            'pady': 15
        }

        # Création et positionnement du bouton
        self.start_btn = tk.Button(
            self.canvas,
            **button_style,
            command=self.start_game
        )

        # Positionnement en bas de l'écran (87% de la hauteur)
        self.canvas.create_window(
            self.screen_width // 2,
            self.screen_height * 0.91,
            window=self.start_btn
        )

        # Effets de survol
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg="#c0392b"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg="#e74c3c"))

        # Création du menu déroulant pour choisir la difficulté de son adversaire
        options = ["Facile", "Difficile"]
        self.selected_difficulty = tk.StringVar()
        self.selected_difficulty.set("Selectionner la difficulté")  # Valeur par défaut

        self.dropdown = tk.OptionMenu(self.canvas, self.selected_difficulty, *options)
        self.dropdown.config(
            font=("Helvetica", 16, "bold"),  # Texte plus grand
            bg="white",
            width=25,  # Plus large en nombre de caractères (~pixels selon police)
            padx=10,
            pady=5
        )

        # Positionner le menu déroulant au-dessus du bouton
        self.canvas.create_window(
            self.screen_width // 2,
            self.screen_height * 0.82,
            window=self.dropdown
        )

    def start_game(self):
        difficulty = self.selected_difficulty.get()
        if difficulty not in ["Facile", "Difficile"]:
            messagebox.showwarning("Choix manquant", "Veuillez sélectionner une difficulté.")
            return

        self.root.destroy()
        players = ['Victor', 'IA']

        game_root = tk.Tk()
        game = Game(players, difficulty=difficulty)
        app = GameApp(game_root, game)  # si GameApp prend un Game
        game_root.mainloop()

