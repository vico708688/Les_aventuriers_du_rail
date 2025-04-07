import game as g
import tkinter as tk
from graphic_interface.interface import GameApp
from data.data import *

def main():
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()

if __name__ == "__main__":
    players = ['Victor', WAGON_COLORS[0]]

    main()
    game = g.Game()

    game.start(players)