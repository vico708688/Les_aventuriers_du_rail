import game as g
import tkinter as tk
from graphic_interface.interface import GameApp
from data.data import *
from models.player import Player

def main():
    players = [Player('Victor', 'red'), Player('AI', 'blue')]

    root = tk.Tk()
    app = GameApp(root, players)
    root.mainloop()

if __name__ == "__main__":
    main()
