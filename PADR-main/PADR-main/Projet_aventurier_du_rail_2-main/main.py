import tkinter as tk
from graphic_interface.start_screen import *

if __name__ == "__main__":
    # Créer et lancer l'écran d'accueil
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    start_screen = StartScreen(root)
    root.mainloop()