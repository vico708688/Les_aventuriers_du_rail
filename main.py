import game as g
import tkinter as tk
from graphic_interface.interface import GameApp
from data.data import *

def main():
    players = [['Victor', WAGON_COLORS[0]], ['AI', WAGON_COLORS[0]]]
    game = g.Game()

    root = tk.Tk()
    app = GameApp(root, players)
    root.mainloop()

    game.start(players)

if __name__ == "__main__":
    main()
