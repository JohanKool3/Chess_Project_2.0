# By creating all of the graphical dependencies away from the main loop, it will be easier to debug and develop

from ChessObjects import BoardState
from ChessObjects import convertCoordsToSquare, convertSquareToCoords
from ChessObjects import cleanImport
import sys
from copy import deepcopy
from Settings import *  # As to keep the contents of this file purely functional

pygame.init()

# Functions and Procedures
""" Functions """

""" Procedures"""


# Creates the entries for the dictionary 'COORD LOOKUP TABLE'
def createSquareCoordLookupTable():
    rawImport = cleanImport("Resources/Data/SquareCoords")

    for row in rawImport:
        COORDLOOKUPTABLE[row[0]] = tuple((int(row[1]), int(row[2]) + HELP_BAR_Y + MATERIAL_BAR_Y))


# Logic Based Global Variables
COORDLOOKUPTABLE = {}
MOUSEPOSITION = None

# Runtime variables
CURRENT_TURN = 1
createSquareCoordLookupTable()

# PlaceHolder Images For EXTRA gui functions
PLACEHOLDER = pygame.image.load("Resources/Assets/Extra_GUI/CoordinateMarker.png")
BACKGROUND_COLOUR = (175, 169, 169)


class GraphicalBoard(pygame.sprite.Sprite):

    def __init__(self, parentGUI):

        super().__init__()
        self.image = pygame.image.load(BOARDSTYLE)
        self.rect = self.image.get_rect()

        # Set the offset for the help bar
        self.rect.y = HELP_BAR_Y + MATERIAL_BAR_Y

        self.contents = []
        self.parentGUI = parentGUI

        self.selectedMarker = None

        markerImage = ["Resources/Assets/Extra_GUI/PreviousSquareMarkers/Marker_1.png"]
        # Previous Square Marker
        self.previousSquare = None
        self.previousSquareMarker = Tile((79, 79), (0, 0), self.parentGUI)
        self.previousSquareMarker.setCustomImages(markerImage)

        # New Square Marker

        self.newSquare = None
        self.newSquareMarker = Tile((79, 79), (0, 0), self.parentGUI)
        self.newSquareMarker.setCustomImages(markerImage)

    def update(self):

        # Previous Square Highlighting
        if self.previousSquare is not None:
            self.previousSquareMarker.setPosition(COORDLOOKUPTABLE[self.previousSquare])

        # New Square Highlighting
        if self.newSquare is not None:
            self.newSquareMarker.setPosition((COORDLOOKUPTABLE[self.newSquare]))

        # Basic Features for board intractability

        for marker in self.contents:
            marker.update()

        if pygame.mouse.get_pressed()[2]:
            self.selectedMarker = None

    def draw(self):
        # Board gets displayed first
        self.parentGUI.surface.blit(self.image, self.rect)

        # Display Previous Square
        if self.previousSquare is not None:
            self.previousSquareMarker.draw(self.parentGUI.surface)

        # Display New Square
        if self.newSquare is not None:
            self.newSquareMarker.draw(self.parentGUI.surface)

        for marker in self.contents:
            marker.draw()

        if self.selectedMarker is not None:
            self.selectedMarker.drawMoveMarkers()

    def addMarker(self, markerObject):
        markerObject.update()
        self.contents.append(markerObject)

    def selectMarker(self, markerObject):
        self.selectedMarker = markerObject

    def deselectMarkers(self):
        self.selectedMarker = None
        self.previousSquare = None
        self.newSquare = None


""" Start of Graphical Elements Definitions"""


class PieceMarker(pygame.sprite.Sprite):  # The graphic that will represent each piece

    def __init__(self, relativePiece, parentBoard, king):

        # Logical functions
        super().__init__()
        self.piece = relativePiece
        self.square = relativePiece.square
        self.parentBoard = parentBoard
        self.color = self.piece.color

        # Gui Orientated code
        color = self.piece.color
        pieceName = str(type(self.piece).__name__)
        filePath = f"Resources/Assets/{color}/{pieceName}.png"

        self.image = pygame.image.load(filePath)
        self.rect = self.image.get_rect()

        self.pieceMoves = []  # Graphical representation of the pieces move
        self.lastPlayedMoves = 0
        self.localTurn = 0

        # Move Interpolation Stuffs
        self.isMoving = False
        self.previousSquare = None
        self.interpIncrement = None
        self.interpFrames = 10

        self.cycles = 0
        self.king = king

        self.isKing = False
        self.checkMarker = None
        if self.king == self.piece:
            self.isKing = True

            self.checkMarker = Tile((78, 78), (0, 0), self.parentBoard.parentGUI)
            self.checkMarker.setCustomImages(["Resources/Assets/Extra_GUI/InCheckMarkers/CheckMarker_1.png"])

    def draw(self):

        surface = self.parentBoard.parentGUI.surface

        if self.isKing and self.king.isCheck and self.parentBoard.parentGUI.gameState is None:
            self.checkMarker.draw(surface)

        surface.blit(self.image, self.rect)

    def drawMoveMarkers(self):

        for possibleMove in self.pieceMoves:
            possibleMove.draw()

    # Graphical Input and Update Stuff
    def __updatePosition(self):
        currentPos = COORDLOOKUPTABLE[self.square]
        self.square = self.piece.square
        self.rect.x, self.rect.y = currentPos
        if self.checkMarker is not None:
            self.checkMarker.setPosition((currentPos))

    def __detectInput(self):
        even = False
        if CURRENT_TURN % 2 == 0:
            even = True

        if even and self.color == "Black":

            if MOUSEPOSITION is not None:

                if self.rect.collidepoint(MOUSEPOSITION):

                    if pygame.mouse.get_pressed()[0]:
                        self.parentBoard.selectMarker(self)

        elif not even and self.color == "White":

            if MOUSEPOSITION is not None:

                if self.rect.collidepoint(MOUSEPOSITION):

                    if pygame.mouse.get_pressed()[0]:
                        self.parentBoard.selectMarker(self)

    def __interpolateMove(self):

        if self.interpIncrement is None:
            startSquare = self.previousSquare
            destination = self.square

            startCoords = COORDLOOKUPTABLE[startSquare]
            endCoords = COORDLOOKUPTABLE[destination]

            self.interpIncrement = ((endCoords[0] - startCoords[0]) // self.interpFrames,
                                    (endCoords[1] - startCoords[1]) // self.interpFrames)

        else:
            self.rect.x, self.rect.y = (self.rect.x + self.interpIncrement[0],
                                        self.rect.y + self.interpIncrement[1])
            self.cycles += 1

            if self.cycles >= self.interpFrames:
                self.isMoving = False
                self.interpIncrement = None
                self.cycles = 0

    def __updateMoveSquares(self):
        parentGui = self.parentBoard.parentGUI

        if self.localTurn != CURRENT_TURN:
            self.pieceMoves = []
            if not self.pieceMoves or (self.king.isCheck and parentGui.gameState is None):

                self.piece.deriveMoves()
                movesAvailable = self.piece.returnMoves()

                for move in movesAvailable:
                    self.pieceMoves.append(MoveMarker(move, self.parentBoard, self))

                self.lastFetchedMoves = movesAvailable  # Creates a value copy of the last fetched moves

                if not movesAvailable:  # Prevents the function from constantly checking when no moves are available
                    self.pieceMoves.append(None)

            self.localTurn = CURRENT_TURN

    def drawMoveMarkers(self):

        if not self.isMoving:

            for marker in self.pieceMoves:

                if marker is not None:
                    marker.draw()

    def handleMoveInput(self, moveMarker):

        self.parentBoard.selectedMarker = None
        self.isMoving = True
        self.previousSquare = self.square
        destination = moveMarker.square
        self.pieceMoves = []

        if moveMarker.square[1] == "Normal":

            if self.piece.movePiece(destination):
                self.lastPlayedMoves += 1
                self.square = self.piece.square
                self.parentBoard.newSquare = self.square  # Current Square

        elif moveMarker.square[1] == "Take":

            for piece in self.parentBoard.contents:

                if piece.square == moveMarker.square[0]:
                    self.parentBoard.contents.remove(piece)

            if self.piece.movePiece(destination):
                self.lastPlayedMoves += 1
                self.square = self.piece.square
                self.parentBoard.newSquare = self.square  # Current Square

        elif moveMarker.square[1] == "Promotion":

            # Create the new queen object at destination square
            self.piece.movePiece(destination)
            newPiece = PieceMarker(self.parentBoard.parentGUI.logicBoard.fetchContents()[moveMarker.square[0]],
                                   self.parentBoard,
                                   self.king)

            newPiece.previousSquare = self.square
            newPiece.isMoving = True

            self.parentBoard.contents.append(newPiece)

            # Delete the pawn from existence
            self.parentBoard.contents.remove(self)
            self.parentBoard.newSquare = newPiece.square
            del self

        elif moveMarker.square[1] == "Long Castling" or "Short Castling":
            movingKing = self.piece  # The king that is moving

            # The current Position of the King
            kingPosition = self.piece.square
            kingCoords = convertSquareToCoords(kingPosition)

            # The final Position of the King after the move
            kingDestination = moveMarker.square[0]
            kingDestCoords = convertSquareToCoords(kingDestination)

            if moveMarker.square[1] == "Long Castling":  # Different destinations depending on the side
                rookPosition = convertCoordsToSquare((kingCoords[0] - 4, kingCoords[1]))
                rookDestination = convertCoordsToSquare((kingDestCoords[0] + 2, kingDestCoords[1]))

            else:
                rookPosition = convertCoordsToSquare((kingCoords[0] + 3, kingCoords[1]))
                rookDestination = convertCoordsToSquare((kingDestCoords[0] - 1, kingDestCoords[1]))

            movingRook = movingKing.board.fetchContents()[rookPosition]  # Logical Rook

            for piece in self.parentBoard.contents:  # Iterates through to find the parent piece marker object

                if piece.piece == movingRook:
                    movingRookSprite = piece  # Graphical Rook

            """ Commit the graphical movement of castling """

            # self.parentBoard.selectedMarker = None
            # self.isMoving = True
            # self.previousSquare = self.square
            # destination = moveMarker.square
            # self.pieceMoves = []

            if self.piece.movePiece(moveMarker.square):

                self.square = self.piece.square
                movingRookSprite.isMoving = True
                movingRookSprite.previousSquare = movingRookSprite.square
                movingRookSprite.pieceMoves = []

                movingRookSprite.square = movingRookSprite.piece.square

                self.parentBoard.newSquare = self.square

    def update(self):

        if not self.isMoving:
            self.__updatePosition()

        else:
            self.__interpolateMove()

        self.__detectInput()
        self.__updateMoveSquares()


class MoveMarker(pygame.sprite.Sprite):  # The graphic that will represent the possible move available to a piece

    def __init__(self, moveSquare, parentBoard, parentPieceMarker):
        self.square = moveSquare
        self.parentBoard = parentBoard
        self.parentPieceMarker = parentPieceMarker

        self.image = pygame.image.load(MOVEMARKERSTYLE)

        self.rect = self.image.get_rect()

    def draw(self):

        self.__updatePosition()
        self.__detectInput()
        surface = self.parentBoard.parentGUI.surface

        surface.blit(self.image, self.rect)

    def __updatePosition(self):

        self.rect.x, self.rect.y = COORDLOOKUPTABLE[self.square[0]]

    def __detectInput(self):
        global CURRENT_TURN

        if self.rect.collidepoint(MOUSEPOSITION):

            if pygame.mouse.get_pressed()[0]:
                self.parentBoard.previousSquare = self.parentPieceMarker.square  # Previous Square
                self.parentPieceMarker.handleMoveInput(self)

                """     Update Material Bar     """
                self.parentBoard.parentGUI
                CURRENT_TURN += 1
                # The move object has done its purpose


class Tile(pygame.Rect):  # Intractable / UnIntractable graphical elements

    def __init__(self, dimensions, coordinates, graphicalUserInterface, text=None):

        self.rect = pygame.Rect(coordinates[0], coordinates[1], dimensions[0], dimensions[1])
        self.images = [PLACEHOLDER]
        self.text = text

        self.isInteractible = False
        self.subWindowIndex = None

        finalList = []
        for image in self.images:
            image = pygame.transform.scale(image, dimensions)
            finalList.append(image)

        self.images = finalList
        self.currentImage = self.images[0]

        self.parentGui = graphicalUserInterface

    def setPosition(self, newPosition):

        self.rect.x, self.rect.y = newPosition

    def setText(self, textIn):
        self.text = textIn

    def draw(self, surface):

        surface.blit(self.currentImage, self.rect)
        self.renderText(surface)

    def renderText(self, surface):

        if self.text is not None:
            textImage = MAINFONT.render(self.text, False, (255, 255, 255))

            position = (self.rect.center[0] - int(0.95 * textImage.get_rect().center[0]),
                        self.rect.center[1] - int(0.95 * textImage.get_rect().center[1]))
            surface.blit(textImage, position)

    def setCustomImages(self, imagePaths):
        newImages = []
        for path in imagePaths:
            newImage = pygame.image.load(path)
            newImage = pygame.transform.scale(newImage, (self.rect.width, self.rect.height))

            newImages.append(newImage)
        self.images = newImages
        self.currentImage = self.images[0]

    def makeInteractible(self):
        self.isInteractible = True

    def setSubWindowLink(self, index):
        self.subWindowIndex = index

    def returnSubWindowIndex(self):

        if self.subWindowIndex is None:
            print("No Index On Given Tile")
            return 0
        else:
            return self.subWindowIndex

    def detectInput(self):

        if self.isInteractible:
            if self.rect.collidepoint(MOUSEPOSITION):
                self.currentImage = self.images[1]

                if pygame.mouse.get_pressed()[0]:
                    self.currentImage = self.images[2]

                    # Select Sub Window
                    if self.subWindowIndex is not None:
                        self.parentGui.openSubWindow(self.subWindowIndex)

            else:
                self.currentImage = self.images[0]


class MaterialPieceSprite(pygame.sprite.Sprite):

    def __init__(self, imagePath, location, pieceName):
        self.name = pieceName
        self.image = pygame.image.load(imagePath)

        self.image = pygame.transform.scale(self.image, (27, 30))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(int(location[0]), int(location[1]))

        self.isToggled = True

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class MaterialTextIndicator(pygame.sprite.Sprite):

    def __init__(self, color, parentPosition):
        self.color = color
        self.text = 0

        self.image = MAINFONT.render("None", True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(parentPosition[0] + 416, parentPosition[1] + 8)

        self.parentPositionTuple = parentPosition

    def updateText(self, textIn):
        self.text = str(textIn)

        self.image = MAINFONT.render(f"+{self.text}", True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(self.parentPositionTuple[0] + 416, self.parentPositionTuple[1] + 8)

    def draw(self, surface):
        if self.text != "0":
            surface.blit(self.image, self.rect)


class MaterialBar(Tile):

    def __init__(self, dimensions, coordinates, graphicalUserInterface, color, text=None):

        super().__init__(dimensions, coordinates, graphicalUserInterface, text)

        self.surface = graphicalUserInterface.surface
        self.pieces = []  # This will contain the sprites of the taken Pieces
        self.color = color
        self.localTurn = 0

        # This holds the information about how many enemy pieces have been taken
        self.amountDict = {"Pawn": 0,
                           "Bishop": 0,
                           "Knight": 0,
                           "Rook": 0,
                           "Queen": 0}

        self.materialTextIndicator = None  # The text that will show the advantage of a side in terms of material
        self.__pieceSetup()

    def __resetPieceToggles(self):

        for piece in self.pieces:
            piece.isToggled = False

    def __pieceSetup(self):

        infoIn = cleanImport("Resources/Assets/Extra_GUI/MaterialBar/Data/PiecePositions")

        for row in infoIn:

            if self.color == "White":
                currentPath = f"Resources/Assets/Black/{row[0]}.png"

            else:
                currentPath = f"Resources/Assets/White/{row[0]}.png"
            self.pieces.append(MaterialPieceSprite(currentPath, (int(row[1]) + self.rect.x,
                                                                 int(row[2]) + self.rect.y), row[0]))

        # Setup material advantage text
        self.materialTextIndicator = MaterialTextIndicator(self.color, self.rect.topleft)
        self.pieces.append(self.materialTextIndicator)

    def __togglePiecesWithName(self, targetName, amount):

        pieces = []

        for piece in self.pieces:
            if type(piece).__name__ == "MaterialPieceSprite" and piece.name == targetName:
                pieces.append(piece)

        for entry in pieces[0:amount]:
            entry.isToggled = True

    def __resetAmountDict(self):

        for row in self.amountDict:
            self.amountDict[row] = 0

    def __update(self):

        def convertVectorToScalar(valueIn):

            if self.color == "Black" and valueIn < 0:
                return valueIn * -1

            elif self.color == "White" and valueIn > 0:
                return valueIn

            else:
                return 0

        if CURRENT_TURN != self.localTurn:

            self.__resetAmountDict()
            takenPieces = deepcopy(self.parentGui.logicBoard.takenPieces)

            # add to the amounts dictionary / Update dictionary amounts
            for piece in takenPieces:

                pieceName = type(piece).__name__

                if pieceName == "Pawn" and piece.color != self.color:
                    self.amountDict["Pawn"] += 1

                elif pieceName == "Knight" and piece.color != self.color:
                    self.amountDict["Knight"] += 1

                elif pieceName == "Bishop" and piece.color != self.color:
                    self.amountDict["Bishop"] += 1

                elif pieceName == "Rook" and piece.color != self.color:
                    self.amountDict["Rook"] += 1

                elif pieceName == "Queen" and piece.color != self.color:
                    self.amountDict["Queen"] += 1

                else:
                    pass

            self.__resetPieceToggles()  # Sets all pieces to toggle false

            for row in self.amountDict:
                self.__togglePiecesWithName(row, self.amountDict[row])
                # This sets the pieces with the same name to toggled to show up on the material bar

            materialAdvantage = self.parentGui.logicBoard.returnMaterialAdvantage()
            self.materialTextIndicator.updateText(str(convertVectorToScalar(materialAdvantage)))
            self.localTurn = CURRENT_TURN

    def draw(self, surface):

        self.__update()
        super().draw(surface)

        for piece in self.pieces:

            if type(piece).__name__ == "MaterialPieceSprite" and piece.isToggled:
                piece.draw(surface)

            elif type(piece).__name__ == "MaterialTextIndicator":
                piece.draw(surface)


class Button(Tile):

    def __init__(self, dimensions, coordinates, graphicalUserInterface, text=None):

        super().__init__(dimensions, coordinates, graphicalUserInterface, text)

        images = ["Resources/Assets/Extra_GUI/HelpBar/HelpBar_Banner_Tile.png",
                  "Resources/Assets/Extra_GUI/HelpBar/HelpBar_Banner_Tile_Hover.png"]

        self.setCustomImages(images)

    def detectInput(self):

        if self.isInteractible:

            if self.rect.collidepoint(MOUSEPOSITION):
                self.currentImage = self.images[1]

                if pygame.mouse.get_pressed()[0]:
                    self.parentGui.activeSubWindow = None

            else:
                self.currentImage = self.images[0]


class PieceButton(Button):

    def __init__(self, dimensions, coordinates, graphicalUserInterface, index, text=None):

        super().__init__(dimensions, coordinates, graphicalUserInterface, text)

        self.index = index

    def detectInput(self):

        if self.rect.collidepoint(MOUSEPOSITION):
            self.currentImage = self.images[1]

            if pygame.mouse.get_pressed()[0]:
                return True

        else:
            self.currentImage = self.images[0]


""" End Of Graphical Marker Definitions"""


class SubWindow(object):

    def __init__(self, identifier, linkGui):

        placeHolderBackground = Tile((681, 801), (0, 0), linkGui)
        placeHolderBackground.setCustomImages(["Resources/Assets/Extra_GUI/PlaceHolderBackground.png"])
        # This will be used if there is no contents to the given window
        self.surface = linkGui.surface
        self.identifier = identifier
        self.contents = [placeHolderBackground]
        self.parentGui = linkGui

        self.backGroundImage = None
        self.backGroundImageRect = None
        self.currentSubWindowIndex = None

    def addContents(self, itemsIn):

        for item in itemsIn:
            self.contents.append(item)

        if len(self.contents) <= 2 and self.identifier != "Help":
            # If it is just the placeholder background and return button
            return

        else:  # If there is a large amount of content, remove the placeholder
            self.contents = []

            for item in itemsIn:
                self.contents.append(item)

    def wipeCurrentSubWindowIndex(self):

        self.currentSubWindowIndex = None

    def addBackgroundImage(self, path):

        self.backGroundImage = pygame.image.load(path)
        self.backGroundImageRect = self.backGroundImage.get_rect()

    def detectReturnToMainProgram(self):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_BACKSPACE]:
            self.parentGui.activeSubWindow = None

    def detectInputs(self):

        for tile in self.contents:

            if type(tile).__name__ == "PieceButton":

                if tile.detectInput():
                    self.currentSubWindowIndex = tile.index

            if tile.isInteractible:
                tile.detectInput()

    def update(self):
        self.detectReturnToMainProgram()
        self.detectInputs()

        if self.backGroundImage is None:
            self.surface.fill((0, 0, 0))

        else:
            self.surface.blit(self.backGroundImage, self.backGroundImageRect)

        for item in self.contents:
            item.draw(self.surface)
            item.detectInput()

        pygame.display.update()


class PieceExplanation(SubWindow):

    def __init__(self, identifier, linkGui):

        pieces = ["Bishop", "King", "Knight", "Pawn", "Queen", "Rook"]

        def returnNewPosition():
            newPosition = tuple((position[0] + dimensions[0], 0))

            return newPosition

        super().__init__(identifier, linkGui)
        self.currentActiveIndex = 0

        dimensions = (linkGui.dimensions[0] // 6, 40)
        position = (0, 0)

        # Bishop Tile Setup
        bishop = PieceButton(dimensions, position, self.parentGui, 0, "Bishop")

        # King Tile Setup
        king = PieceButton(dimensions, returnNewPosition(), self.parentGui, 1, "King")
        position = returnNewPosition()

        # Knight Tile Setup
        knight = PieceButton(dimensions, returnNewPosition(), self.parentGui, 2, "Knight")
        position = returnNewPosition()

        # Pawn Tile Setup
        pawn = PieceButton(dimensions, returnNewPosition(), self.parentGui, 3, "Pawn")
        position = returnNewPosition()

        # Queen Tile Setup
        queen = PieceButton(dimensions, returnNewPosition(), self.parentGui, 4, "Queen")
        position = returnNewPosition()

        # Rook Tile Setup
        rook = PieceButton(dimensions, returnNewPosition(), self.parentGui, 5, "Rook")
        position = returnNewPosition()

        tileList = [bishop, king, knight, pawn, queen, rook]

        dimensions = (2 * (self.parentGui.graphicalBoard.rect.width // 8), HELP_BAR_Y)
        # Exit Button
        position = (linkGui.dimensions[0] - dimensions[0],
                    linkGui.dimensions[1] - dimensions[1])
        exitButton = Button(dimensions, position, self, "Return")
        exitButton.makeInteractible()

        tileList.append(exitButton)

        self.subWindows = [SubWindow(0, self.parentGui),  # Bishop
                           SubWindow(1, self.parentGui),  # King
                           SubWindow(2, self.parentGui),  # Knight
                           SubWindow(3, self.parentGui),  # Pawn
                           SubWindow(4, self.parentGui),  # Queen
                           SubWindow(5, self.parentGui)]  # Rook

        for index, subWindow in enumerate(self.subWindows):
            subWindow.addContents(tileList)

            subWindow.addBackgroundImage(f"Resources/Assets/Extra_GUI/SubWindows/Piece_Explanation/{pieces[index]}.png")

    def updateCurrentIndex(self):

        if self.subWindows[self.currentActiveIndex].currentSubWindowIndex is not None:
            oldIndex = self.currentActiveIndex
            index = self.subWindows[self.currentActiveIndex].currentSubWindowIndex

            self.currentActiveIndex = index
            self.subWindows[oldIndex].wipeCurrentSubWindowIndex()

    def update(self):

        self.detectReturnToMainProgram()
        self.updateCurrentIndex()
        self.detectInputs()

        if self.backGroundImage is None:
            self.surface.fill((0, 0, 0))

        else:
            self.surface.blit(self.backGroundImage, self.backGroundImageRect)

        self.subWindows[self.currentActiveIndex].update()

        pygame.display.update()


# This is the main object that will be used in the 'MAIN' file
class GraphicalUserInterface(object):

    def __init__(self, importPath):

        self.__importPath = importPath

        self.logicBoard = BoardState()
        self.logicBoard.setupBoardFromCSV(importPath)
        self.graphicalBoard = GraphicalBoard(self)

        # Actual Pygame Stuff
        xWidth = self.graphicalBoard.rect.size[0] + (COORD_BAR_DIMENSIONS[0])
        yHeight = self.graphicalBoard.rect.size[1] + HELP_BAR_Y + (COORD_BAR_DIMENSIONS[1]) + MATERIAL_BAR_Y * 2

        self.dimensions = [xWidth, yHeight]

        # Allows the dimensions of the window to be referenced in older versions of pygame.

        self.surface = pygame.display.set_mode((xWidth, yHeight))
        pygame.display.set_caption("Chess")
        pygame.display.set_icon(pygame.image.load(ICONIMAGE))

        self.__setupMarkers()

        # Material Bars
        self.materialBars = []

        # Extra Graphics setup & definitions
        self.extraGUI = []  # Sub windows
        self.__setupCoordinateBar()
        self.__setupOptionsBar()
        self.__setupMaterialBar()

        # Sub window setup
        self.subWindows = [SubWindow("Help", self),
                           SubWindow("Settings", self),
                           PieceExplanation("Instructions", self),
                           SubWindow("Customisation", self)]

        self.activeSubWindow = None

        # Sub Windows  Setup
        self.__setupSubWindowHeaders()

        # Image backgrounds for each window
        self.subWindows[0].addBackgroundImage("Resources/Assets/Extra_GUI/SubWindows/HelpMenu.png")

        # Important Logical Part
        self.gameState = None

        # The image that will indicate the win condition for the game
        self.winConditionImage = None
        self.winConditionImage_rect = None

    def __setupMarkers(self):

        for square in self.logicBoard.fetchContents().values():

            if square is not None:

                if square.color == "Black":
                    self.graphicalBoard.addMarker(PieceMarker(square, self.graphicalBoard, self.logicBoard.blackKing))

                else:
                    self.graphicalBoard.addMarker(PieceMarker(square, self.graphicalBoard, self.logicBoard.whiteKing))
                # This creates a new piece marker that is linked to the piece in question

    def __setupSubWindowHeaders(self):
        headerList = ["Help", "Settings", "Instructions", "Customisation"]

        for i in range(0, 4):
            newTiles = []

            dimensions = ((self.graphicalBoard.rect.width // 4) + COORD_BAR_DIMENSIONS[0], HELP_BAR_Y)

            # Exit Button
            position = (self.dimensions[0] - dimensions[0],
                        self.dimensions[1] - dimensions[1])
            exitButton = Button(dimensions, position, self, "Return To Game")
            exitButton.makeInteractible()
            newTiles.append(exitButton)

            self.subWindows[i].addContents(newTiles)

    def __setupCoordinateBar(self):
        # Setup for the Rank Indicator
        yOffsets = HELP_BAR_Y + MATERIAL_BAR_Y

        files = ["A", "B", "C", "D", "E", "F", "G", "H"]

        dimensions = (COORD_BAR_DIMENSIONS[0], self.graphicalBoard.rect.height)
        coordinates = (self.dimensions[0] - COORD_BAR_DIMENSIONS[0], yOffsets)

        singleTileDimensions = (dimensions[0], dimensions[1] // 8)
        currentCoordinates = deepcopy(coordinates)

        for i in range(1, 9):
            self.extraGUI.append(Tile(singleTileDimensions, currentCoordinates, self, str(9 - i)))

            currentCoordinates = (currentCoordinates[0],
                                  currentCoordinates[1] + singleTileDimensions[1])

        # Setup for the File Indicator
        dimensions = (dimensions[1], dimensions[0])
        coordinates = (0, self.dimensions[1] - yOffsets)

        singleTileDimensions = (dimensions[0] // 8, dimensions[1])
        currentCoordinates = deepcopy(coordinates)

        for i in range(8):
            self.extraGUI.append(Tile(singleTileDimensions, currentCoordinates, self, str(files[i])))
            currentCoordinates = (currentCoordinates[0] + singleTileDimensions[0],
                                  currentCoordinates[1])

    def __setupOptionsBar(self):
        position = (0, 0)
        bannerImage = "Resources/Assets/Extra_GUI/HelpBar/HelpBar_Banner_Tile.png"

        bannerHover = "Resources/Assets/Extra_GUI/HelpBar/HelpBar_Banner_Tile_Hover.png"
        bannerInteract = "Resources/Assets/Extra_GUI/HelpBar/HelpBar_Banner_Tile_Clicked.png"

        newImages = [bannerImage, bannerHover, bannerInteract]

        # Help Options Tile
        dimensions = (2 * (self.graphicalBoard.rect.width // 8), HELP_BAR_Y)
        helpOption = Tile(dimensions, position, self, "Help")

        helpOption.setCustomImages(newImages)
        helpOption.makeInteractible()
        helpOption.setSubWindowLink(0)
        self.extraGUI.append(helpOption)

        # Settings Tile
        position = (position[0] + dimensions[0], 0)
        settingsOption = Tile(dimensions, position, self, "Settings")
        settingsOption.setCustomImages(newImages)
        settingsOption.makeInteractible()
        settingsOption.setSubWindowLink(1)
        self.extraGUI.append(settingsOption)

        # Instructions
        position = (position[0] + dimensions[0], 0)
        instructionsOption = Tile(dimensions, position, self, "Instructions")
        instructionsOption.setCustomImages(newImages)
        instructionsOption.makeInteractible()
        instructionsOption.setSubWindowLink(2)
        self.extraGUI.append(instructionsOption)

        # Customisation
        position = (position[0] + dimensions[0], 0)
        dimensions = (dimensions[0] + COORD_BAR_DIMENSIONS[0], dimensions[1])
        customisationOption = Tile(dimensions, position, self, "Customisation")
        customisationOption.setCustomImages(newImages)
        customisationOption.makeInteractible()
        customisationOption.setSubWindowLink(3)
        self.extraGUI.append(customisationOption)

    def __setupMaterialBar(self):

        whiteMaterialBarImage = "Resources/Assets/Extra_GUI/MaterialBar/WhiteMaterial_Banner.png"
        blackMaterialBarImage = "Resources/Assets/Extra_GUI/MaterialBar/BlackMaterial_Banner.png"

        dimensions = (self.dimensions[0], MATERIAL_BAR_Y)
        position = (0, self.dimensions[1] - MATERIAL_BAR_Y)

        whiteMaterialBar = MaterialBar(dimensions, position, self, "White")
        whiteMaterialBar.setCustomImages([whiteMaterialBarImage])
        self.extraGUI.append(whiteMaterialBar)

        position = (0, HELP_BAR_Y)

        blackMaterialBar = MaterialBar(dimensions, position, self, "Black")
        blackMaterialBar.setCustomImages([blackMaterialBarImage])
        self.extraGUI.append(blackMaterialBar)

        #  Material Bar Setup
        self.materialBars.append(whiteMaterialBar)
        self.materialBars.append(blackMaterialBar)

    def __drawExtraGraphics(self):

        for tile in self.extraGUI:
            tile.draw(self.surface)

    def __updateExtraGraphics(self):

        self.__drawExtraGraphics()

        for tile in self.extraGUI:
            tile.detectInput()

    def openSubWindow(self, subWindowIndex):

        if self.subWindows[subWindowIndex] is not None:

            subWindow = self.subWindows[subWindowIndex]
            self.activeSubWindow = subWindow
            self.graphicalBoard.deselectMarkers()

        else:
            return None

    def __detectGameState(self):
        whiteInCheck = self.logicBoard.whiteKing.isCheck
        blackInCheck = self.logicBoard.blackKing.isCheck

        whiteMoves = len(self.logicBoard.returnSideMoves("White"))
        blackMoves = len(self.logicBoard.returnSideMoves("Black"))

        # Game Conditions

        # For white to be checkmated|  they must have no moves and be in check
        if whiteMoves == 0 and whiteInCheck:
            self.gameState = "BlackWins"

        # For black to be checkmated|  they must have no moves and be in check
        elif blackMoves == 0 and blackInCheck:
            self.gameState = "WhiteWins"

        # For stalemate, the stalemated side must have no moves but not be in check
        elif (blackMoves == 0 and not blackInCheck) or (whiteMoves == 0 and not whiteInCheck):
            self.gameState = "Stalemate"

        else:
            self.gameState = None

    def __displayWinCondition(self):
        """ This places a popup that indicates the game state to the player in a graphical manner """

        if self.winConditionImage is None:

            self.winConditionImage = pygame.image.load(f"Resources/Assets/GameStates/{self.gameState}.png")
            self.winConditionImage_rect = self.winConditionImage.get_rect()
            centralPosition = [self.dimensions[0] // 2, self.dimensions[1] // 2]

            self.winConditionImage_rect.center = centralPosition

            print("Press Escape to restart the game")

        self.surface.blit(self.winConditionImage, self.winConditionImage_rect)

    def __restartGame(self):
        """ This will restart the program as well as the objects inside this class """

        self.logicBoard = BoardState()
        self.logicBoard.setupBoardFromCSV(self.__importPath)
        self.graphicalBoard = GraphicalBoard(self)

        self.__setupMarkers()

        # Restart game variables
        self.gameState = None
        self.winConditionImage = None

        # Material Bar Setup
        self.materialBars = []
        self.__setupMaterialBar()

    def update(self):

        global MOUSEPOSITION
        MOUSEPOSITION = pygame.mouse.get_pos()
        """ This method is responsible for updating all graphical and logical processes in one place """

        # Simple exit statement for leaving the program nice and cleanly
        """     Quit statements for both clicking the close window button or pressing escape on the keyboard    """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.quit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    if self.gameState is None:
                        sys.exit()
                        pygame.quit()

                    else:
                        self.__restartGame()

        if self.activeSubWindow is None:
            # Main Graphical Bit
            self.surface.fill(BACKGROUND_COLOUR)
            self.graphicalBoard.draw()
            self.graphicalBoard.update()
            self.__updateExtraGraphics()

            # For handling the game state
            if self.gameState is None:
                # To Continue
                self.__detectGameState()

            else:
                # To End
                self.__displayWinCondition()

            pygame.display.update()

        else:
            self.activeSubWindow.update()
