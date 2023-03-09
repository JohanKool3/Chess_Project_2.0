import pygame


pygame.init()  # As to make sure that pygame functions work as intended
""" Graphical User Interface Customisation """

# / Image related Variables \
BOARDSTYLE = "Resources/Chess_Board.png"
MOVEMARKERSTYLE = "Resources/Assets/PossibleSquare.png"
ICONIMAGE = "Resources/Assets/Black/Queen.png"

# Default Font
MAINFONT = pygame.font.Font("Resources/Assets/Extra_GUI/Fonts/EuropeanTypewriter.ttf", 25)
MAINFONT.set_bold(True)

# / Window Size Variables \

# For the help options as well as settings menu
HELP_BAR_Y = 40

# For the display of the Square Coordinate System
COORD_BAR_DIMENSIONS = tuple((40, 40))

# For the display of the taken pieces
MATERIAL_BAR_Y = 40