import csv
from copy import deepcopy


# Useful Functions to use in the entire program
def cleanImport(target):  # Useful fore multiple functions, Saves alot of time

    def openFile():
        with open(target + ".csv", "rt") as text_file:
            step1 = csv.reader(text_file)
            output = list(step1)
            return output

    rawImport = openFile()

    del rawImport[0]  # Removes Headers

    return rawImport

def validate(piece, move):  # Function for determining if a move is legal or not

    checkBoard = deepcopy(piece.board)
    checkPiece = checkBoard.fetchContents()[piece.square]

    movingColor = checkPiece.color

    if movingColor == "White":
        kingInQuestion = checkBoard.whiteKing

    else:
        kingInQuestion = checkBoard.blackKing

    # To remove illegal taking moves
    if move[1] == "Take":

        if type(piece.board.fetchContents()[move[0]]).__name__ == "King":
            piece.board.fetchContents()[move[0]]
            return False

    checkBoard.movePiece(piece.square, move[0], move[1])

    # Detects whether the move puts the moving side into check
    if kingInQuestion.detectInCheck():

        return False
    else:

        return True

def convertCoordsToSquare(coordsIn):
    returnCoords = tuple()
    files = ["A", "B", "C", "D", "E", "F", "G", "H"]

    letter = int(coordsIn[0])
    number = int(coordsIn[1])

    return str(f"{files[letter - 1]}{number}")

def convertSquareToCoords(squareIn):
    files = ["A", "B", "C", "D", "E", "F", "G", "H"]

    letter = squareIn[0]
    number = int(squareIn[1])

    for index, char in enumerate(files):

        if char == squareIn[0]:
            return tuple((index + 1, number))


class BoardState(object):

    def __init__(self):
        files = ["A", "B", "C", "D", "E", "F", "G", "H"]

        self.__contents = {}
        self.blank = "(<*>)"
        for rank in range(1, 9):
            for file in files:  # Sets up the board with blank entries
                self.__contents[file + str(rank)] = None

        self.blackPieces = []  # This will be a reference to all black pieces in the contents of the board
        self.whitePieces = []  # This will be a reference to all white pieces in the contents of the board

        self.takenPieces = []  # This will keep a track of the taken pieces. This can be used for GUI purposes.

        self.blackKing = None
        self.whiteKing = None

        # More logical stuff
        self.materialAdvantage = 0  # This means that the advantage is even
        """ This will be in the form of a vector quantity. A negative value indicates that black has the advantage
            whereas a positive value indicates that white has an advantage  """

        self.playedMoves = [] # This will keep track of the moves that have been played in the game

    def __str__(self):  # Text based representation of the board
        output = ""
        currentRank = None
        for entry in self.__contents:

            if currentRank != entry[1]:
                currentRank = entry[1]
                output += "\n"

            newItem = self.blank  # Code for a blank place

            if self.__contents[entry] is not None:
                newItem = f"({self.__contents[entry].returnCode()})"

            output += f" |{newItem}| "

        return output

    def __addPiece(self, pieceObject, square):
        # This has been made private as to act as a form of encapsulation
        try:
            self.__contents[square] = pieceObject

            if pieceObject.color == "White":
                self.whitePieces.append(pieceObject)
            else:
                self.blackPieces.append(pieceObject)

        except:
            print("Error with placing the piece")

    def setupBoardFromCSV(self, path):  # Requires a functional relationship with piece Objects

        inputData = cleanImport(path)

        for row in inputData:

            if row[0] == "Pawn":
                self.__addPiece(Pawn(row[1], row[2], self), row[2])

            elif row[0] == "Knight":
                self.__addPiece(Knight(row[1], row[2], self), row[2])

            elif row[0] == "Bishop":
                self.__addPiece(Bishop(row[1], row[2], self), row[2])

            elif row[0] == "Rook":
                self.__addPiece(Rook(row[1], row[2], self), row[2])

            elif row[0] == "Queen":
                self.__addPiece(Queen(row[1], row[2], self), row[2])

            elif row[0] == "King":
                newKing = King(row[1], row[2], self)
                self.__addPiece(newKing, row[2])

                if row[1] == "White":
                    self.whiteKing = newKing

                else:
                    self.blackKing = newKing

    def returnSideMoves(self, side):  # This will be used to determine if a certain side is in checkmate
        possibleMoves = []
        if side == "White":

            for piece in self.whitePieces:

                for move in piece.filteredMoves:
                    possibleMoves.append(move)

        else:

            for piece in self.blackPieces:

                for move in piece.filteredMoves:
                    possibleMoves.append(move)

        return possibleMoves

    def __updateMaterialAdvantage(self):
        pieceValues = {"Pawn": 1,
                       "Knight": 3,
                       "Bishop": 3,
                       "Rook": 5,
                       "Queen": 9}

        whiteTakenValue = 0  # The value of the black pieces that have been taken
        blackTakenValue = 0  # The value of the white pieces that have been taken

        for piece in self.takenPieces:

            try:
                currentPieceValue = pieceValues[type(piece).__name__]

                if piece.color == "White":
                    blackTakenValue += currentPieceValue

                else:
                    whiteTakenValue += currentPieceValue

            except IndexError as error:
                print(error)

        #  Now to convert to vector form, white - black values
        self.materialAdvantage = whiteTakenValue - blackTakenValue

    def returnMaterialAdvantage(self):
        return self.materialAdvantage

    def movePiece(self, oldPosition, newPosition, moveType):
        # Moves the piece from the start position to the new position

        if moveType == "Normal":
            self.__contents[oldPosition].square = newPosition  # Updates the moving piece's current square
            self.__contents[newPosition] = self.__contents[oldPosition]
            self.__contents[oldPosition] = None

        elif moveType == "Take":

            self.__contents[oldPosition].square = newPosition  # Updates the moving piece's current square
            takenPiece = self.__contents[newPosition]
            self.__contents[newPosition] = self.__contents[oldPosition]
            self.__contents[oldPosition] = None

            if takenPiece.color == "Black":
                self.blackPieces.remove(takenPiece)

            else:
                self.whitePieces.remove(takenPiece)

            self.takenPieces.append(takenPiece)
            # Going to need to update material information
        elif moveType == "Promotion":
            # This will later be able to be dictated to determine which piece should be promoted to
            self.__addPiece(Queen(self.__contents[oldPosition].color, newPosition, self),
                            newPosition)

            promotedPawn = self.__contents[oldPosition]

            self.__contents[oldPosition] = None

            # Update the piece arrays
            if promotedPawn.color == "Black":
                self.blackPieces.remove(promotedPawn)

            else:
                self.whitePieces.remove(promotedPawn)

        elif moveType == "Long Castling" or moveType == "Short Castling":

            movingKing = self.__contents[oldPosition]  # Reference to the castling King

            if moveType == "Long Castling":
                newKingPosition = convertSquareToCoords(newPosition)

                # This is just to fetch a reference to the moving rook
                currentRookPosition = (newKingPosition[0] - 2, newKingPosition[1])
                movingRook = self.__contents[convertCoordsToSquare(currentRookPosition)]

                newRookPosition = convertCoordsToSquare((currentRookPosition[0] + 3, currentRookPosition[1]))

            else:
                # The square that the king will move to after castling
                newKingPosition = convertSquareToCoords(newPosition)

                # This is just to fetch a reference to the moving rook
                currentRookPosition = (newKingPosition[0] + 1, newKingPosition[1])
                movingRook = self.__contents[convertCoordsToSquare(currentRookPosition)]

                newRookPosition = convertCoordsToSquare((currentRookPosition[0] - 2, currentRookPosition[1]))

            """    Now that the important information about the moving pieces has been retrieved, it is time 
                   to commit the move to the board!    """

            movingKing.square = newPosition
            self.__contents[newPosition] = movingKing
            self.__contents[oldPosition] = None

            oldRookSquare = movingRook.square

            movingRook.square = newRookPosition
            self.__contents[newRookPosition] = movingRook
            self.__contents[oldRookSquare] = None

        # This must be done at the end of this method as to maintain up to date information about the game at hand
        self.__updateMaterialAdvantage()

    def fetchContents(self):
        return self.__contents

# Start Of Piece classification
class Piece(object):

    def __init__(self, color, square, parentBoard):
        # Basic attributes for any piece
        self.color = color
        self.square = square
        self.board = parentBoard

        self.name = None
        self.code = color[0] + ":"
        self.value = 0
        self.rawMoves = []
        self.filteredMoves = []

        self.playedMoves = 0

    def evaluate(self):

        if self.code[1:] == "P":
            self.value = 1

        elif self.code[1:] == "N" or self.code[1:] == "B":
            self.value = 3

        elif self.code[1:] == "R":
            self.value = 5

        elif self.code[1:] == "Q":
            self.value = 9

    def chessToGridConversion(self, coordsIn=None):  # This will save confusion later on in development
        files = ["A", "B", "C", "D", "E", "F", "G", "H"]

        if coordsIn is None:
            currentY = self.square[1]

            for index, file in enumerate(files):

                if file == self.square[0]:
                    currentX = index + 1

                    return tuple((int(currentX), int(currentY)))

        elif coordsIn is not None:
            return str(files[int(coordsIn[0]) - 1]) + str(coordsIn[1])

    def validateMoves(self):
        self.filteredMoves = []

        for move in self.rawMoves:

            if validate(self, move):
                self.filteredMoves.append(move)

    def movePiece(self, inputSquare):  # The move method for any chess piece
        if inputSquare in self.filteredMoves:

            self.board.movePiece(self.square, inputSquare[0], inputSquare[1])  # Board Update
            self.square = inputSquare[0]  # Piece Update
            self.playedMoves += 1

            self.board.whiteKing.detectInCheck()
            self.board.blackKing.detectInCheck()
            return True
        else:
            print("Square not a possible move for this piece")
            print(self)
            print(self.board)
            return False

    def fetchAllPossibleMovesFromInterpolation(self, modifiers):

        self.rawMoves = []

        currentCoordinates = self.chessToGridConversion()
        derivedMoves = self.rawMoves

        for modifier in modifiers:

            localCoordinates = currentCoordinates
            while 0 < localCoordinates[0] <= 8 and 0 < localCoordinates[1] <= 8:

                localCoordinates = (localCoordinates[0] + modifier[0], localCoordinates[1] + modifier[1])

                if 8 >= localCoordinates[0] > 0 and 8 >= localCoordinates[1] > 0:
                    currentSquare = self.chessToGridConversion(localCoordinates)

                    if self.board.fetchContents()[currentSquare] is not None:

                        if self.board.fetchContents()[currentSquare].color == self.color:
                            break

                        else:
                            derivedMoves.append([currentSquare, "Take"])
                            break

                    else:
                        derivedMoves.append([currentSquare, "Normal"])

    # Attribute return functions
    def returnCode(self):
        return self.code

    def returnMoves(self):
        return self.filteredMoves

    def returnPlayedMovesAmount(self):
        return self.playedMoves


class Pawn(Piece):

    def __init__(self, color, square, parentBoard):

        super().__init__(color, square, parentBoard)
        self.code += "P"
        self.evaluate()

        # Pawn specific attributes
        self.__playedMoves = 0
        self.__openToEnPassant = False

    def deriveMoves(self):
        self.quickDerive()
        self.validateMoves()

    def quickDerive(self):

        self.rawMoves = []

        """ Start of setup """

        currentCoordinates = self.chessToGridConversion()  # Sets the coordinates to the actual coordinates of the piece

        # Move modifier setup as to prevent code duplication when determining directions of pawn movement!

        """ The move modifier enables the same movement code to be used for both the black and white pieces
            as all that is changing is the direction of movement on the 'y' axis"""
        if self.color == "Black":
            moveModifier = -1
        else:
            moveModifier = 1
        derivedMoves = self.rawMoves  # By reference, as this updates so will the variable in the parent class
        """ End of setup """

        """     Start of Normal Movement    """
        # Simple forward movement
        nextSquare = (currentCoordinates[0], currentCoordinates[1] + (1 * moveModifier))

        if 1 < nextSquare[1] < 8:  # Bounds check

            if self.board.fetchContents()[self.chessToGridConversion(nextSquare)] is None:
                # To Check to see if the square is available to move to
                derivedMoves.append([self.chessToGridConversion(nextSquare), "Normal"])

        elif nextSquare[1] == 1 or nextSquare[1] == 8:

            if self.board.fetchContents()[self.chessToGridConversion(nextSquare)] is None:
                derivedMoves.append([self.chessToGridConversion(nextSquare), "Promotion"])

        # First move two squares
        finalDestination = (currentCoordinates[0], currentCoordinates[1] + (2 * moveModifier))
        freeSquaresBetween = 0

        nextSquare = currentCoordinates
        # Algorithm to detect free moves - This can be pushed to a function later on to make it easier to implement,
        # Rook, bishop and queen movement later on in development
        while nextSquare != finalDestination and self.__playedMoves == 0:

            nextSquare = (nextSquare[0], nextSquare[1] + (1 * moveModifier))

            if self.board.fetchContents()[self.chessToGridConversion(nextSquare)] is not None:
                break
            freeSquaresBetween += 1

        if freeSquaresBetween == 2 and self.__playedMoves == 0:
            derivedMoves.append([self.chessToGridConversion(nextSquare), "Normal"])

        """     End of Normal Movement      """

        """"    Start of  Take pieces      """

        modifiers = [(1, 1), (-1, 1)]  # Forward and to the right and forward and to the left

        for modifier in modifiers:

            nextSquare = (currentCoordinates[0] + modifier[0],
                          currentCoordinates[1] + (modifier[1] * moveModifier))

            if 0 < nextSquare[0] < 9 and 0 < nextSquare[1] < 9:
                nextSquareChessNotation = self.chessToGridConversion(nextSquare)

                if self.board.fetchContents()[nextSquareChessNotation] is not None:

                    if self.board.fetchContents()[nextSquareChessNotation].color != self.color:
                        derivedMoves.append([nextSquareChessNotation, "Take"])

    def movePiece(self, inputSquare):
        super().movePiece(inputSquare)

        if self.__playedMoves >= 1:
            self.__openToEnPassant = False
        self.__playedMoves += 1

        return True


class Knight(Piece):

    def __init__(self, color, square, parentBoard):
        super().__init__(color, square, parentBoard)
        self.code += "N"
        self.evaluate()

    def deriveMoves(self):

        self.quickDerive()
        self.validateMoves()

    def quickDerive(self):
        self.rawMoves = []

        currentCoordinates = self.chessToGridConversion()
        derivedMoves = self.rawMoves

        modifiers = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]
        # All of the translations for the knight to perform when moving

        for translation in modifiers:

            if 0 < currentCoordinates[0] + translation[0] <= 8 and 0 < currentCoordinates[1] + translation[1] <= 8:
                destination = self.chessToGridConversion(
                    (currentCoordinates[0] + translation[0], currentCoordinates[1] + translation[1]))

                if self.board.fetchContents()[destination] is None:
                    derivedMoves.append([destination, "Normal"])

                else:
                    targetPiece = self.board.fetchContents()[destination]

                    if targetPiece.color != self.color:
                        derivedMoves.append([destination, "Take"])


class Bishop(Piece):

    def __init__(self, color, square, parentBoard):
        super().__init__(color, square, parentBoard)
        self.code += "B"
        self.evaluate()

    def deriveMoves(self):
        self.quickDerive()
        self.validateMoves()

    def quickDerive(self):
        self.fetchAllPossibleMovesFromInterpolation([(1, 1), (1, -1), (-1, 1), (-1, -1)])


class Rook(Piece):

    def __init__(self, color, square, parentBoard):
        super().__init__(color, square, parentBoard)
        self.code += "R"
        self.evaluate()

    def deriveMoves(self):
        self.quickDerive()
        self.validateMoves()

    def quickDerive(self):
        self.fetchAllPossibleMovesFromInterpolation([(0, 1), (0, -1), (1, 0), (-1, 0)])


class Queen(Piece):

    def __init__(self, color, square, parentBoard):
        super().__init__(color, square, parentBoard)
        self.code += "Q"
        self.evaluate()

    def deriveMoves(self):
        self.quickDerive()

        self.validateMoves()

    def quickDerive(self):
        self.fetchAllPossibleMovesFromInterpolation([(1, 1), (1, -1), (-1, 1), (-1, -1),
                                                     (0, 1), (0, -1), (1, 0), (-1, 0)])


class King(Piece):

    def __init__(self, color, square, parentBoard):

        super().__init__(color, square, parentBoard)
        self.code += "K"
        self.evaluate()
        self.isCheck = False

    def deriveMoves(self):
        # This function is used to find moves that are possible (don't put the moving side into check)

        self.quickDerive()
        self.validateMoves()

    def quickDerive(self):

        # This function is used to find moves that are possible REGARDLESS of check

        # Normal Movement as well as Taking

        def checkCastling():

            possibleCastling = [True, True]  # First is King-side , second if Queen-side
            if self.playedMoves > 0:  # Guard Clause as to prevent the king from castling once it has moved
                return [False, False]

            castlingModifiers = [3, 4]

            # Check for KingSide Castling
            for i in range(1, castlingModifiers[0]):

                checkCoords = (currentCoordinates[0] + i, currentCoordinates[1])

                if self.board.fetchContents()[self.chessToGridConversion(checkCoords)] is not None:
                    possibleCastling[0] = False

            rookCoords = currentCoordinates[0] + castlingModifiers[0], currentCoordinates[1]
            rookSquare = self.chessToGridConversion(rookCoords)

            if self.board.fetchContents()[rookSquare] is None or type(self.board.fetchContents()[rookSquare]).__name__ \
                    is not "Rook" or self.board.fetchContents()[rookSquare].playedMoves > 0:

                possibleCastling[0] = False

            # Check for QueenSide Castling
            for i in range(1, castlingModifiers[1]):

                checkCoords = (currentCoordinates[0] - i, currentCoordinates[1])

                if self.board.fetchContents()[self.chessToGridConversion(checkCoords)] is not None:
                    possibleCastling[1] = False

            rookCoords = currentCoordinates[0] - castlingModifiers[1], currentCoordinates[1]
            rookSquare = self.chessToGridConversion(rookCoords)

            if self.board.fetchContents()[rookSquare] is None or type(self.board.fetchContents()[rookSquare]).__name__ \
                    is not "Rook" or self.board.fetchContents()[rookSquare].playedMoves > 0:

                possibleCastling[1] = False

            return possibleCastling

        self.rawMoves = []

        modifiers = [(1, 1), (1, -1), (-1, 1), (-1, -1),
                     (0, 1), (0, -1), (1, 0), (-1, 0)]

        currentCoordinates = self.chessToGridConversion()
        derivedMoves = self.rawMoves

        for modifier in modifiers:

            localCoordinates = (currentCoordinates[0] + modifier[0], currentCoordinates[1] + modifier[1])

            if 0 < localCoordinates[0] <= 8 and 0 < localCoordinates[1] <= 8:
                destination = self.chessToGridConversion(localCoordinates)

                if self.board.fetchContents()[destination] is None:
                    derivedMoves.append([destination, "Normal"])

                else:
                    targetPiece = self.board.fetchContents()[destination]

                    if targetPiece.color != self.color:
                        derivedMoves.append([destination, "Take"])

        # Now to detect castling opportunities

        castlingOpportunities = checkCastling()

        for index, answer in enumerate(castlingOpportunities):

            if answer:
                if index == 0:
                    derivedMoves.append([self.chessToGridConversion((currentCoordinates[0] + 2, currentCoordinates[1])),
                                         "Short Castling"])

                else:
                    derivedMoves.append([self.chessToGridConversion((currentCoordinates[0] - 2, currentCoordinates[1])),
                                         "Long Castling"])

    def detectInCheck(self):

        self.isCheck = False

        if self.color == "White":
            enemyPieces = self.board.blackPieces

        else:
            enemyPieces = self.board.whitePieces

        controlledSquares = []

        for piece in enemyPieces:
            piece.quickDerive()

            for square in piece.rawMoves:
                controlledSquares.append(square[0])

        if self.square in controlledSquares:
            self.isCheck = True
            return True

        else:
            return False


if __name__ == "__main__":
    """ Just For Testing    """
    test = BoardState()
    test.setupBoardFromCSV("Resources/Data/StartPositions")

    piece = test.fetchContents()["B1"]
    piece.deriveMoves()
    print(test)
    piece.movePiece(piece.returnMoves()[0])
    print(test)
