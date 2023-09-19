# This will serve as the gameplay loop for the Chess Engine
import ChessGUI

importPath = "Resources/Data/StartPositions"

GUI = ChessGUI.GraphicalUserInterface(importPath)  # This is responsible for all interactions
running = True

while running:
    GUI.update()