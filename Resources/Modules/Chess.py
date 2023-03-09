# Chess Engine Version 1

import csv  # Used for importing data from external files
import copy  # Used for next depth analysis, to determine if moves are check,checkmate or neither


# Logic Stuffs - (All Backend , this is for pure computation and logical analysis)

class Move(object):

    def __init__(self, prevSquare, nextSquare, pieceName, pieceColor, moveType, isCheck, isMate=False):
        """ This constructor is responsible for assigning default attributes that are responsible for
            the basic functionality of the move object. This logic will later be used to enable each
            piece to function."""

        def deriveNotation():  # A function that is responsible for deriving a notational output of the move from
            # destinational logic and piece names in line with standard chess notation.

            output = None

            if moveType == "Short-Castle":
                output = "O-O"
                return output

            if moveType == "Long-Castle":
                output = "O-O-O"
                return output

            if moveType == "En Passant":

                if pieceColor == "White":
                    output = prevSquare[0].lower() + "x" + str(nextSquare[0].lower() + str(int(nextSquare[1]) + 1))
                    return output

                else:
                    output = prevSquare[0].lower() + "x" + str(nextSquare[0].lower() + str(int(nextSquare[1]) - 1))
                    return output

            if self.__pieceName == "Pawn":  # Pawn Notation

                if moveType == "Take":
                    output = prevSquare[0].lower() + "x" + nextSquare.lower()

                else:
                    output = nextSquare.lower()

            elif self.__pieceName == "Knight":  # Knight Notation

                if moveType == "Take":
                    output = "Nx" + nextSquare.lower()

                else:
                    output = "N" + nextSquare.lower()

            else:
                if moveType == "Take":
                    output = self.__pieceName[0].upper() + "x" + nextSquare.lower()

                else:
                    output = self.__pieceName[0].upper() + nextSquare.lower()

            if isCheck:  # Detects checks

                if isMate:  # Detects Checkmate
                    output += "#"

                else:
                    output += "+"

            return output

        self.__value = None  # The comparable value of the piece compared to a pawn
        self.__prevSquare = prevSquare  # The last square that the piece was in
        self.__nextSquare = nextSquare  # the destination square that the piece moved from
        self.__pieceName = pieceName  # The name of the moving piece
        self.__pieceColor = pieceColor  # The colour of the piece
        # This will aid in notation and other mechanics centred around multiple moves like en passant and castling
        self.__moveType = moveType
        self.__notation = deriveNotation()

    def __str__(self):

        """ The commented out parts of this code were used during the development of this version. This code has been
            left in as an aid during debugging in the future. The reason it has been removed from the final version
            of the program is that is can overwhelming for the user to take in. As well as this, the information that is
            required by the user is easy to read on the board - this section is responsible for displaying updates for
            a text based version of this program."""

        output = self.__notation  # Just returns the notation as to prevent an overflow of information

        #        if self.__moveType != "En Passant":
        #            output = (f"{self.__pieceColor} {self.__pieceName}: {self.__prevSquare} to {self.__nextSquare}  |  Move Type: {self.__moveType} - |NOTATION| {self.__notation}")
        #
        #        else:
        #            if self.__pieceColor == "White":
        #                output = (f"{self.__pieceColor} {self.__pieceName}: {self.__prevSquare} to {self.__nextSquare[0] + str(int(self.__nextSquare[1]) + 1)} | Move Type: {self.__moveType} - |NOTATION| {self.__notation}")
        #
        #            else:
        #                output = (f"{self.__pieceColor} {self.__pieceName}: {self.__prevSquare} to {self.__nextSquare[0] + str(int(self.__nextSquare[1]) - 1)} | Move Type: {self.__moveType} - |NOTATION| {self.__notation}")

        return output

    def moveType(self):  # Returns the move type (the tag given to each move to distinguish against other moves)
        return self.__moveType

    def coords(self):  # Returns the previous and next square in chess notation e.g.[A4, A5]
        return [self.__prevSquare, self.__nextSquare]

    def pieceColor(self):  # Returns the colour of the piece that is attached to this move object
        return self.__pieceColor

    def notation(self):  # Returns the notation of the move that was derived in the constructor
        return self.__notation


class Piece(object):
    """ This object is responsible for the majority of the interactions in this program. Inside of it are the definitions
        to every move that can be made by every piece. This is followed by the logical checks that are available for
        each move that make sure that the move is legal. This involves checks, and checkmate along with restricted king
        moves (when potentially moving into check) and pins. Each of theses features will be clearly described when
        they are reached."""

    def __init__(self, name, color, square):

        def valuePiece():  # Returns a value for each Piece created relative to the pawn's value (being 1)

            if self.__name == "Pawn":  # The base unit of chess, all other pieces are compared to it
                return 1

            elif self.__name == "Knight" or self.__name == "Bishop":  # These 'minor pieces' are considered the strength
                # of 3 pawns
                return 3

            elif self.__name == "Rook":  # with the strength of a knight/bishop and two pawns, a rook is considered a
                # 'Major' piece
                return 5

            elif self.__name == "Queen":  # The strongest piece in the game, with the strength of the rook and the bishop
                # combined, it is worth a rook, bishop/knight and a pawn
                return 9

            else:
                return None

        # Important Attributes
        self.__name = name  # the name of the piece  | Datatype string
        self.__color = color  # the colour of the piece  | Datatype string
        self.__moves = 0  # the moves made by this object (this is useful for 'en passant' and AI analysis
        self.__square = square  # The square the piece currently resides in
        self.__possibleMoves = []  # All of the moves that are available to the piece
        self.__validMoves = []  # The moves that have been validated to check if they are Legal
        self.__timeSinceLastMove = 0  # the moves that have been played since this piece moved (useful for 'en passant')

        """ Code derivation for all of the pieces. This works by taking the first letter of the pieces name and the
            first letter of the colour that the piece belongs to. For example, a white rook will become 'W:R'. This
            rule works for every piece except the knight (as the king already has the letter K in its code). Therefore,
            the knight takes the letter N instead."""

        if self.__name != "Knight":

            self.__code = color[0] + ":" + name[0]

        else:
            self.__code = color[0] + ":" + "N"

        self.__value = valuePiece()

    def __str__(self):  # Returns the colour and the name of the piece

        return str(self.__color) + "-" + str(self.__name)

    def code(self):  # Returns Code for the piece
        return self.__code

    def promote(self):

        if self.__name == "Pawn":
            self.__name = "Queen"
            self.__code = self.__color[0] + ":" + "Q"

    def name(self):  # Returns the name of the piece
        return self.__name

    def returnMoves(self, board):  # Returns the moves available to the piece on a certain boardState
        return self.findPossibleMoves(board)

    def color(self):  # Returns Piece color
        return self.__color

    def possibleMoves(self):  # Returns the possible moves available to the piece stored in the 'self.__possibleMoves'
        # attribute.

        return self.__possibleMoves

    def value(self):  # Returns Piece Value
        return self.__value

    def square(self):  # Returns the square that the piece currently resides in
        return self.__square

    def validMoves(
            self):  # Returns the moves that have been validated and are stored in the 'self.__validMoves' attribute
        return self.__validMoves

    def setSquare(self, square):  # Updates the position of the Piece
        self.__square = square

    def move(self, square):  # Moves the piece from one square to another, updating the necessary attributes
        self.__square = square
        self.__moves += 1
        self.__timeSinceLastMove = 0

    def getMoves(self):  # Returns currently Fetched Moves
        return self.__moves

    def wait(self):  # Adds 1 to "time since last move" attribute
        self.__timeSinceLastMove += 1

    def addMove(self):  # Adds 1 to the 'self.__moves' attribute.
        self.__moves += 1

    def timeSinceLastMove(self):  # Returns the time since the piece last moves
        return self.__timeSinceLastMove

    def validate(self, board):  # This method is responsible for validating moves to make sure they are legal

        self.__validMoves = []

        #  These two functions find the squares that the kings are currently in
        def findEnemyKing():

            for entry in board.dict:  # Finds the enemy king

                if board.dict[entry] != None and board.dict[entry].color() != self.__color:

                    if board.dict[entry].name() == "King":
                        enemyKingSquare = entry

            return enemyKingSquare

        def inCheck(boardIn):  # Checks to see if the king is in check

            def findKing(boardIn):

                for entry in boardIn.dict:

                    if boardIn.dict[entry] != None and boardIn.dict[entry].color() == self.__color:

                        if boardIn.dict[entry].name() == "King":
                            return entry

            def enemyTerritory(boardIn):

                output = []

                for entry in boardIn.dict:

                    if boardIn.dict[entry] != None and boardIn.dict[entry].color() != self.__color:
                        # Finds piece's of the opposite color

                        for move in boardIn.dict[entry].findPossibleMoves(boardIn, False):
                            # Finds all of that piece's possible Moves

                            if move[1] != "Short-Castle" or move[1] != "Long-Castle" or move[1] != "En Passant":
                                output.append(move[0])

                            if move[1] == "En Passant":

                                if self.__color == "White":

                                    output.append(str(move[0][0] + str(int(move[0][1]) + 1)))

                                else:

                                    output.append(str(move[0][0] + str(int(move[0][1]) - 1)))

                return output

            king = findKing(boardIn)  # The king's Square

            for square in enemyTerritory(boardIn):  # For each square that the enemy controls

                if square == king:  # If the enemy controls the king's square, then you are in check
                    return True  # In Check

            return False  # The converse

        def determineMate(boardIn):  # This checks to see if the enemy side has moves

            if self.__color == "White":

                if len(boardIn.blackPieces.digestPossibleMoves(boardIn)) == 0:
                    # If they have no moves, they are in a state of checkmate
                    return True

                else:
                    return False

            else:

                if len(boardIn.whitePieces.digestPossibleMoves(boardIn)) == 0:
                    return True

                else:
                    return False

        def nextDepthChecks(move, king):  # finds checks one move ahead (for this piece)

            tempBoard = copy.deepcopy(board)  # Copy of the board

            for square in tempBoard.dict:  # Adds Extra Waiting To Pieces that arent moving

                if tempBoard.dict[square] != None and tempBoard.dict[square].color() == self.__color:
                    tempBoard.dict[square].wait()
                """This movement logic is done via the scheme that the 'tempBoard.dict' is a dictionary. This means that
                    by using and index, that value can be fetched. Because in this stage the move still has the tag assigned
                    to it, the first entry in the move tuple must be used."""

            if move[1] == "Normal":  # Normal Movement

                # By moving normally, the position of the piece simply needs to be updated along with any other
                # attributes that keep track of meta data (like time since last move etc).
                tempBoard.dict[move[0]] = tempBoard.dict[self.__square]
                tempBoard.dict[self.__square] = None

                tempBoard.dict[move[0]].move(move[0])

                newSquare = move[0]

            elif move[1] == "Promotion":

                tempBoard.dict[move[0]] = tempBoard.dict[self.__square]
                tempBoard.dict[self.__square] = None

                tempBoard.dict[move[0]].promote()  # Promotes the pawn into a queen

                newSquare = move[0]

            elif move[1] == "Take":  # TAKE

                # A bit more complicated here, instead of just switching the position of the piece, the piece that is
                # being taken needs to be removed from the board and then from its subsequent 'Side' object which will
                # handle the value the side has as well as the pieces associated with it. This is dealt with later

                takenPiece = tempBoard.dict[move[0]]
                tempBoard.dict[move[0]] = tempBoard.dict[self.__square]
                tempBoard.dict[self.__square] = None

                tempBoard.dict[move[0]].move(move[0])  # Makes sure the self.__square attribute is updated

                newSquare = move[0]

            elif move[1] == "En Passant":  # EN PASSANT

                takenPiece = tempBoard.dict[move[0]]

                tempBoard.dict[self.__square].move(move[0])  # Makes sure the self.__square attribute is updated

                if self.__color == "White":
                    tempBoard.dict[str(move[0][0]) + str(int(move[0][1]) + 1)] = tempBoard.dict[self.__square]
                    tempBoard.dict[self.__square] = None
                    tempBoard.dict[move[0]] = None

                    newSquare = str(move[0][0]) + str(int(move[0][1]) + 1)

                else:
                    tempBoard.dict[str(move[0][0]) + str(int(move[0][1]) - 1)] = tempBoard.dict[self.__square]
                    tempBoard.dict[self.__square] = None
                    tempBoard.dict[move[0]] = None

                    newSquare = str(move[0][0]) + str(int(move[0][1]) - 1)

                if self.__color == "White":
                    tempBoard.blackPieces.remove(takenPiece)

                else:
                    tempBoard.whitePieces.remove(takenPiece)

            elif move[1] == "Short-Castle":  # SHORT CASTLE

                if self.__color == "White":  # WHITE

                    tempBoard.dict["H1"].move("F1")  # Makes sure the self.__square attribute is updated
                    tempBoard.dict[self.__square].move("G1")  # Makes sure the self.__square attribute is updated

                    rook = tempBoard.dict["H1"]  # Position of rook
                    king = tempBoard.dict[self.__square]  # Position of king

                    tempBoard.dict["F1"] = rook  # Moves the Rook
                    tempBoard.dict["G1"] = king  # Moves the King

                    tempBoard.dict["H1"] = None
                    tempBoard.dict[self.__square] = None

                    currentPiece = rook

                else:  # BLACK

                    tempBoard.dict["H8"].move("F8")  # Makes sure the self.__square attribute is updated
                    tempBoard.dict[self.__square].move("G8")  # Makes sure the self.__square attribute is updated

                    rook = tempBoard.dict["H8"]
                    king = tempBoard.dict[self.__square]

                    tempBoard.dict["F8"] = rook
                    tempBoard.dict["G8"] = king

                    tempBoard.dict["H8"] = None
                    tempBoard.dict[self.__square] = None

                    currentPiece = rook

            elif move[1] == "Long-Castle":  # LONG CASTLE

                if self.__color == "White":  # White

                    tempBoard.dict["A1"].move("D1")  # Makes sure the self.__square attribute is updated
                    tempBoard.dict[self.__square].move("C1")  # Makes sure the self.__square attribute is updated

                    rook = tempBoard.dict["A1"]
                    king = tempBoard.dict[self.__square]

                    tempBoard.dict["D1"] = rook
                    tempBoard.dict["C1"] = king

                    tempBoard.dict["A1"] = None
                    tempBoard.dict[self.__square] = None

                    currentPiece = rook

                else:

                    tempBoard.dict["A8"].move("D8")  # Makes sure the self.__square attribute is updated
                    tempBoard.dict[self.__square].move("C8")  # Makes sure the self.__square attribute is updated

                    rook = tempBoard.dict["A8"]
                    king = tempBoard.dict[self.__square]

                    tempBoard.dict["D8"] = rook
                    tempBoard.dict["C8"] = king

                    tempBoard.dict["A8"] = None
                    tempBoard.dict[self.__square] = None

                    currentPiece = rook

            else:
                print("Exception Occurred")

            # END SETUP

            # If you are not already in check
            if inCheck(board) != True:

                #  Looks for checks - for the moving player

                if move[1] == "Short-Castle":

                    for nextMove in currentPiece.findPossibleMoves(tempBoard, False):

                        if nextMove[0] == king:

                            if inCheck(tempBoard) != True:
                                self.__validMoves.append(
                                    Move(self.__square, move[0], self.__name, self.__color, move[1], True,
                                         determineMate(tempBoard)))
                            return None

                    if inCheck(tempBoard) != True:
                        self.__validMoves.append(Move(self.__square, move[0], self.__name, self.__color, move[1],
                                                      False))  # If A check is not possible, it is a normal move

                elif move[1] == "Long-Castle":

                    for nextMove in currentPiece.findPossibleMoves(tempBoard, False):

                        if nextMove[0] == king:

                            if inCheck(tempBoard) != True:
                                self.__validMoves.append(
                                    Move(self.__square, move[0], self.__name, self.__color, move[1], True,
                                         determineMate(tempBoard)))

                            return None
                    if inCheck(tempBoard) != True:
                        self.__validMoves.append(Move(self.__square, move[0], self.__name, self.__color, move[1],
                                                      False))  ## If A check is not possible, it is a normal move

                else:
                    try:
                        currentPiece = tempBoard.dict[newSquare]

                    except:
                        print(self.possibleMoves())

                    for nextMove in currentPiece.findPossibleMoves(tempBoard, False):

                        if nextMove[0] == king:

                            if inCheck(tempBoard) != True:
                                self.__validMoves.append(
                                    Move(self.__square, move[0], self.__name, self.__color, move[1], True,
                                         determineMate(tempBoard)))

                            return None

                    if inCheck(tempBoard) != True:
                        self.__validMoves.append(
                            Move(self.__square, move[0], self.__name, self.__color, move[1], False))

            # If you are currently in check
            else:
                if inCheck(tempBoard) != True:

                    if move[1] == "Long-Castle":
                        return None

                    elif move[1] == "Short-Castle":
                        return None

                    else:
                        self.__validMoves.append(
                            Move(self.__square, move[0], self.__name, self.__color, move[1], False))

        for move in self.__possibleMoves:

            if move[1] == "Take":  # Prevents the king from being taken

                if board.dict[move[0]] != None and board.dict[move[0]].name() == "King":
                    self.__possibleMoves.remove(move)
                    break

            nextDepthChecks(move, findEnemyKing())

    def findPossibleMoves(self, board,
                          validate=True):  # Finds the possible moves for each piece and appends each one to the pieces attribute self.__possibleMoves

        self.__possibleMoves = []

        allFiles = ["A", "B", "C", "D", "E", "F", "G", "H"]  # All Files In Chess

        for index, item in enumerate(allFiles):

            if item == self.__square[0]:
                fileIndex = index
                break

        rank = int(self.__square[1])  # The number

        if self.__name == "Pawn":  # Pawn Movement
            forward = 1

            if self.__color == "White":  # White Movement
                forward = 1

                if rank < 7 and rank > 0:  ## Every square except the move towards the end of the board
                    if board.dict[self.__square[0] + str(rank + forward)] == None:  # Normal Movement
                        self.__possibleMoves.append([self.__square[0] + str(rank + forward), "Normal"])

                    if self.__moves == 0 and board.dict[self.__square[0] + str(rank + forward)] == None and board.dict[
                        self.__square[0] + str(4)] == None:  # First move Two squares movement
                        self.__possibleMoves.append([self.__square[0] + str(4), "Normal"])
                    # Taking //    Normal

                    if fileIndex + 1 <= len(allFiles) - 1:

                        if board.dict[allFiles[fileIndex + 1] + str(rank + forward)] != None and board.dict[
                            allFiles[fileIndex + 1] + str(rank + forward)].color() != self.__color:
                            self.__possibleMoves.append([allFiles[fileIndex + 1] + str(rank + forward), "Take"])

                    if fileIndex - 1 >= 0:

                        if board.dict[allFiles[fileIndex - 1] + str(rank + forward)] != None and board.dict[
                            allFiles[fileIndex - 1] + str(rank + forward)].color() != self.__color:
                            self.__possibleMoves.append([allFiles[fileIndex - 1] + str(rank + forward), "Take"])

                    # Taking // En Passant

                    if fileIndex + 1 <= len(allFiles) - 1:  # Take to the right

                        if board.dict[allFiles[fileIndex + 1] + str(rank)] != None and board.dict[
                            allFiles[fileIndex + 1] + str(rank)].color() != self.__color and board.dict[
                            allFiles[fileIndex + 1] + str(
                                    rank)].name() == "Pawn":  # If there is an object and it is of the opposite color

                            if board.dict[allFiles[fileIndex + 1] + str(rank)].timeSinceLastMove() == 0 and board.dict[
                                allFiles[fileIndex + 1] + str(
                                        rank)].getMoves() == 1:  # If the object can be taken via en passant
                                self.__possibleMoves.append([allFiles[fileIndex + 1] + str(rank), "En Passant"])

                    if fileIndex - 1 >= 0:  # Take to the left

                        if board.dict[allFiles[fileIndex - 1] + str(rank)] != None and board.dict[
                            allFiles[fileIndex - 1] + str(rank)].color() != self.__color and board.dict[
                            allFiles[fileIndex - 1] + str(
                                    rank)].name() == "Pawn":  # If there is an object and it is of the opposite color

                            if board.dict[allFiles[fileIndex - 1] + str(rank)].timeSinceLastMove() == 0 and board.dict[
                                allFiles[fileIndex - 1] + str(
                                        rank)].getMoves() == 1:  # If the object can be taken via en passant

                                self.__possibleMoves.append([allFiles[fileIndex - 1] + str(rank), "En Passant"])

                if rank == 7:
                    if board.dict[self.__square[0] + str(rank + forward)] == None:
                        self.__possibleMoves.append([self.__square[0] + str(rank + forward), "Promotion"])
            else:  # Black Movement  ## Every move except the move towards the end of the board
                forward = -1

                if rank + forward > 1 and rank <= 8:
                    if board.dict[self.__square[0] + str(rank + forward)] == None:
                        self.__possibleMoves.append([self.__square[0] + str(rank + forward), "Normal"])

                    if self.__moves == 0 and board.dict[self.__square[0] + str(rank + forward)] == None and board.dict[
                        self.__square[0] + str(5)] == None:  # First move Two squares movement
                        self.__possibleMoves.append([self.__square[0] + str(5), "Normal"])
                    # Taking //    Normal

                    if fileIndex + 1 < len(allFiles):

                        if board.dict[allFiles[fileIndex + 1] + str(rank + forward)] != None and board.dict[
                            allFiles[fileIndex + 1] + str(rank + forward)].color() != self.__color:
                            self.__possibleMoves.append([allFiles[fileIndex + 1] + str(rank + forward), "Take"])

                    if fileIndex - 1 >= 0:

                        if board.dict[allFiles[fileIndex - 1] + str(rank + forward)] != None and board.dict[
                            allFiles[fileIndex - 1] + str(rank + forward)].color() != self.__color:
                            self.__possibleMoves.append([allFiles[fileIndex - 1] + str(rank + forward), "Take"])

                    # Taking // En Passant

                    if fileIndex - 1 >= 0:

                        if board.dict[allFiles[fileIndex - 1] + str(rank)] != None and board.dict[
                            allFiles[fileIndex - 1] + str(rank)].color() != self.__color and board.dict[
                            allFiles[fileIndex - 1] + str(rank)].name() == "Pawn":

                            if board.dict[allFiles[fileIndex - 1] + str(rank)].timeSinceLastMove() == 0 and board.dict[
                                allFiles[fileIndex - 1] + str(rank)].getMoves() == 1:
                                self.__possibleMoves.append([allFiles[fileIndex - 1] + str(rank), "En Passant"])

                    if fileIndex + 1 < len(allFiles):

                        if board.dict[allFiles[fileIndex + 1] + str(rank)] != None and board.dict[
                            allFiles[fileIndex + 1] + str(rank)].color() != self.__color and board.dict[
                            allFiles[fileIndex + 1] + str(rank)].name() == "Pawn":

                            if board.dict[allFiles[fileIndex + 1] + str(rank)].timeSinceLastMove() == 0 and board.dict[
                                allFiles[fileIndex + 1] + str(rank)].getMoves() == 1:
                                self.__possibleMoves.append([allFiles[fileIndex + 1] + str(rank), "En Passant"])

        if self.__name == "Knight":

            forward = 2
            side = 1

            if rank + forward <= 8:  # Forward Movement
                newRank = str(rank + forward)

                if fileIndex + side <= len(allFiles) - 1:
                    newFile = str(allFiles[fileIndex + side])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    else:
                        if board.dict[newFile + newRank].color() != self.__color:
                            self.__possibleMoves.append([newFile + newRank, "Take"])

                if fileIndex - side >= 0:
                    newFile = str(allFiles[fileIndex - side])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    else:
                        if board.dict[newFile + newRank].color() != self.__color:
                            self.__possibleMoves.append([newFile + newRank, "Take"])

            if rank - forward > 0:  # Backwards Movement
                newRank = str(rank - forward)

                if fileIndex + side <= len(allFiles) - 1:
                    newFile = str(allFiles[fileIndex + side])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    else:
                        if board.dict[newFile + newRank].color() != self.__color:
                            self.__possibleMoves.append([newFile + newRank, "Take"])

                if fileIndex - side >= 0:
                    newFile = str(allFiles[fileIndex - side])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    else:
                        if board.dict[newFile + newRank].color() != self.__color:
                            self.__possibleMoves.append([newFile + newRank, "Take"])

            if rank + side <= 8:  # Right movement
                newRank = str(rank + side)

                if fileIndex + forward <= len(allFiles) - 1:
                    newFile = str(allFiles[fileIndex + forward])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    elif board.dict[newFile + newRank].color() != self.__color:
                        self.__possibleMoves.append([newFile + newRank, "Take"])

                if fileIndex - forward >= 0:
                    newFile = str(allFiles[fileIndex - forward])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    elif board.dict[newFile + newRank].color() != self.__color:
                        self.__possibleMoves.append([newFile + newRank, "Take"])

            if rank - side > 0:  # Left Movement
                newRank = str(rank - side)

                if fileIndex + forward <= len(allFiles) - 1:
                    newFile = str(allFiles[fileIndex + forward])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    elif board.dict[newFile + newRank].color() != self.__color:
                        self.__possibleMoves.append([newFile + newRank, "Take"])

                if fileIndex - forward >= 0:
                    newFile = str(allFiles[fileIndex - forward])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    elif board.dict[newFile + newRank].color() != self.__color:
                        self.__possibleMoves.append([newFile + newRank, "Take"])

        if self.__name == "Bishop":  ## Bishop Movement
            inc = 1

            while rank + inc <= 8 and fileIndex + inc < len(allFiles):  ## Right and Up
                newRank = str(rank + inc)
                newFile = str(allFiles[fileIndex + inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

            inc = 1

            while rank - inc > 0 and fileIndex - inc >= 0:  ## Left and Down
                newRank = str(rank - inc)
                newFile = str(allFiles[fileIndex - inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

            inc = 1

            while rank + inc <= 8 and fileIndex - inc >= 0:  ## Left and Up
                newRank = str(rank + inc)
                newFile = str(allFiles[fileIndex - inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

            inc = 1

            while rank - inc > 0 and fileIndex + inc < len(allFiles):  ## Right and Down
                newRank = str(rank - inc)
                newFile = str(allFiles[fileIndex + inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break
            inc = 1

        if self.__name == "Rook":  ## Rook Movement
            inc = 1

            ## Up
            while rank + inc <= 8:

                newRank = str(rank + inc)
                newFile = str(allFiles[fileIndex])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

            inc = 1
            ##Down
            while rank - inc > 0:
                newRank = str(rank - inc)
                newFile = str(allFiles[fileIndex])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break
            inc = 1
            ##Left
            while fileIndex - inc >= 0:
                newRank = str(rank)
                newFile = str(allFiles[fileIndex - inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

            inc = 1

            ## Right

            while fileIndex + inc < len(allFiles):
                newRank = str(rank)
                newFile = str(allFiles[fileIndex + inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

        if self.__name == "Queen":  ## Queen Movement (Copy and paste heaven)
            inc = 1

            while rank + inc <= 8 and fileIndex + inc < len(allFiles):  ## Right and Up
                newRank = str(rank + inc)
                newFile = str(allFiles[fileIndex + inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

            inc = 1

            while rank - inc > 0 and fileIndex - inc >= 0:  ## Left and Down
                newRank = str(rank - inc)
                newFile = str(allFiles[fileIndex - inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

            inc = 1

            while rank + inc <= 8 and fileIndex - inc >= 0:  ## Left and Up
                newRank = str(rank + inc)
                newFile = str(allFiles[fileIndex - inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

            inc = 1

            while rank - inc > 0 and fileIndex + inc < len(allFiles):  ## Right and Down
                newRank = str(rank - inc)
                newFile = str(allFiles[fileIndex + inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break
            inc = 1

            ## Up
            while rank + inc <= 8:

                newRank = str(rank + inc)
                newFile = str(allFiles[fileIndex])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

            inc = 1
            ##Down
            while rank - inc > 0:
                newRank = str(rank - inc)
                newFile = str(allFiles[fileIndex])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break
            inc = 1
            ##Left
            while fileIndex - inc >= 0:
                newRank = str(rank)
                newFile = str(allFiles[fileIndex - inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

            inc = 1

            ## Right

            while fileIndex + inc < len(allFiles):
                newRank = str(rank)
                newFile = str(allFiles[fileIndex + inc])

                if board.dict[newFile + newRank] == None:
                    self.__possibleMoves.append([newFile + newRank, "Normal"])
                    inc += 1

                elif board.dict[newFile + newRank].color() != self.__color:
                    self.__possibleMoves.append([newFile + newRank, "Take"])
                    break

                else:
                    break

        if self.__name == "King":
            inc = 1

            def determineCastleType(spaces):
                if spaces == 2:
                    return "Short-Castle"

                else:
                    return "Long-Castle"

            if self.__moves == 0:

                forward = 1
                spaces = 0
                done = False

                while fileIndex + forward < len(allFiles):

                    if board.dict[allFiles[fileIndex + forward] + str(rank)] != None and board.dict[
                        allFiles[fileIndex + forward] + str(rank)].name() == "Rook" and board.dict[
                        allFiles[fileIndex + forward] + str(rank)].getMoves() == 0:

                        castleType = determineCastleType(spaces)

                        if castleType == "Short-Castle":
                            offset = 1

                        else:
                            offset = 2

                        self.__possibleMoves.append([allFiles[(fileIndex + forward) - offset] + str(rank), castleType])
                        break

                    elif board.dict[allFiles[fileIndex + forward] + str(rank)] == None:
                        forward += 1
                        spaces += 1

                    else:
                        break

                forward = -1
                spaces = 0
                done = False

                while fileIndex + forward >= 0 and done == False:

                    if board.dict[allFiles[fileIndex + forward] + str(rank)] != None and board.dict[
                        allFiles[fileIndex + forward] + str(rank)].name() == "Rook" and board.dict[
                        allFiles[fileIndex + forward] + str(rank)].getMoves() == 0:

                        castleType = determineCastleType(spaces)

                        if castleType == "Short-Castle":
                            offset = 1

                        else:
                            offset = 2

                        self.__possibleMoves.append([allFiles[(fileIndex + forward) + offset] + str(rank), castleType])
                        break

                    elif board.dict[allFiles[fileIndex + forward] + str(rank)] == None:
                        forward -= 1
                        spaces += 1


                    else:
                        break

            if rank + inc <= 8:  ## All Up Moves
                newRank = str(rank + inc)

                ##Straight up
                if board.dict[str(allFiles[fileIndex]) + newRank] == None:
                    self.__possibleMoves.append([str(allFiles[fileIndex]) + newRank, "Normal"])

                elif board.dict[str(allFiles[fileIndex]) + newRank].color() != self.__color:
                    self.__possibleMoves.append([str(allFiles[fileIndex]) + newRank, "Take"])

                ##Up to Left

                if fileIndex - inc >= 0:
                    newFile = str(allFiles[fileIndex - inc])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    elif board.dict[newFile + newRank].color() != self.__color:
                        self.__possibleMoves.append([newFile + newRank, "Take"])

                ## Up to Right

                if fileIndex + inc < len(allFiles):
                    newFile = str(allFiles[fileIndex + inc])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    elif board.dict[newFile + newRank].color() != self.__color:
                        self.__possibleMoves.append([newFile + newRank, "Take"])

            if rank - inc > 0:  ## All Down Moves
                newRank = str(rank - inc)

                ##Straight down
                if board.dict[str(allFiles[fileIndex]) + newRank] == None:
                    self.__possibleMoves.append([str(allFiles[fileIndex]) + newRank, "Normal"])

                elif board.dict[str(allFiles[fileIndex]) + newRank].color() != self.__color:
                    self.__possibleMoves.append([str(allFiles[fileIndex]) + newRank, "Take"])

                ## Down to Left

                if fileIndex - inc >= 0:
                    newFile = str(allFiles[fileIndex - inc])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    elif board.dict[newFile + newRank].color() != self.__color:
                        self.__possibleMoves.append([newFile + newRank, "Take"])

                ## Down to Right

                if fileIndex + inc < len(allFiles):
                    newFile = str(allFiles[fileIndex + inc])

                    if board.dict[newFile + newRank] == None:
                        self.__possibleMoves.append([newFile + newRank, "Normal"])

                    elif board.dict[newFile + newRank].color() != self.__color:
                        self.__possibleMoves.append([newFile + newRank, "Take"])

            if fileIndex + inc < len(allFiles):  ## Right Movement
                newFile = str(allFiles[fileIndex + inc])

                if board.dict[newFile + str(rank)] == None:
                    self.__possibleMoves.append([newFile + str(rank), "Normal"])

                elif board.dict[newFile + str(rank)].color() != self.__color:
                    self.__possibleMoves.append([newFile + str(rank), "Take"])

            if fileIndex - inc >= 0:
                newFile = str(allFiles[fileIndex - inc])

                if board.dict[newFile + str(rank)] == None:
                    self.__possibleMoves.append([newFile + str(rank), "Normal"])

                elif board.dict[newFile + str(rank)].color() != self.__color:
                    self.__possibleMoves.append([newFile + str(rank), "Take"])

        if validate:
            self.validate(board)  # Validation Step to remove illegal moves

        return self.__possibleMoves


class Side(object):  # Holds the contents as well as value of the pieces inside

    def __init__(self, color):

        self.__color = color
        self.__contents = {}
        self.__material = 0
        self.__isChecked = False

        self.__possibleMoves = []  # List of Lists which contains the previous square and square to move to ["E5","E6"]

    def __str__(self):

        return self.__color

    def append(self, item):

        try:

            self.__contents[item.name()] += 1  # If it already exists, it's quantity is updated by one

        except:

            if item.name() != "King":
                self.__contents[item.name()] = 1  # If it doesn't exist , then it is created with a quantity of 1
        # Updates Material Count
        self.calculateMaterial()

    def remove(self, item):

        try:
            self.__contents[item.name()] -= 1

            if item.name() == "Pawn":
                self.__material -= 1

            elif item.name() == "Bishop" or "Knight":
                self.__material -= 3

            elif item.name() == "Rook":
                self.__material -= 5

            elif item.name() == "Queen":
                self.__material -= 9

            else:
                print("Error has occurred")

        except:
            print("No such Item Exists")
            print(item)

    def calculateMaterial(self):  # Calculates the material currently assigned to the side
        currentMaterial = 0

        for pType in self.__contents:

            if pType != "King":  # Makes sure that the king cannot be calculated as a piece

                if pType == "Pawn":

                    currentMaterial += 1 * self.__contents[pType]  # Material count += piece value * quantity

                elif pType == "Knight" or pType == "Bishop":
                    currentMaterial += 3 * self.__contents[pType]

                elif pType == "Rook":
                    currentMaterial += 5 * self.__contents[pType]

                elif pType == "Queen":
                    currentMaterial += 9 * self.__contents[pType]

                else:
                    print(f"Unknown Piece in ||{self.__color}'s Dictionary||")

        self.__material = currentMaterial  # Ends the Update by assigning the current material to the side's material

    def contents(self):  # Displays Active Pieces
        return self.__contents

    def setContents(self, inp):
        self.__contents = inp

    def color(self):
        return self.__color

    def returnCheckStatus(self):
        return self.__isChecked

    def toggleIsChecked(self):

        self.__isChecked = not self.__isChecked

    def possibleMoves(self):  ## To prevent unnecessary reruns of the taxing "find possible moves " method
        return self.__possibleMoves

    def material(self):  ## Returns Material
        return self.__material

    def locateKing(self, inp):

        for row in inp.dict:

            if inp.dict.get(row) != None and inp.dict.get(row).color() == self.__color and inp.dict.get(
                    row).name() == "King":
                return inp.dict.get(row)

        print("error")

    def digestPossibleMoves(self, boardState,
                            isRunning=False):  ## Takes all the possible moves from each piece and adds it to the possible moves attribute of this object

        self.__possibleMoves = []

        def findPieces(
                same=True):  ## Finds all the pieces in the board state which are the same color as this side(if true), converse if false

            output = []

            if same == True:

                for row in boardState.dict:

                    if boardState.dict.get(row) != None and boardState.dict.get(
                            row).color() == self.__color:  ## Finds all the pieces of the same colour to the side
                        output.append(boardState.dict[row])

            else:  ## Only using this to find the king but it might be useful later on when working with ai to determine a good branch to take

                for row in boardState.dict:

                    if boardState.dict.get(row) != None and boardState.dict.get(row).color() != self.__color:
                        output.append(boardState.dict[row])

            return output

        pieces = findPieces()
        enemyPieces = findPieces(False)

        inCheck = False
        inMate = False

        if self.__isChecked == False:  ## If not currently In Check

            for piece in pieces:
                piece.findPossibleMoves(boardState, True)

                for move in piece.validMoves():
                    self.__possibleMoves.append(move)

        else:  ## If Currently In Check

            for piece in pieces:

                piece.findPossibleMoves(boardState, True)

                for move in piece.validMoves():
                    self.__possibleMoves.append(move)

        def displayMoves():
            # A visual Representation (for debugging and development only) - there will be a method for this later
            for index, move in enumerate(self.__possibleMoves, 1):
                print(f"{index}. {move}")

        if isRunning == True:
            displayMoves()

        return self.__possibleMoves

    def move(self, move, boardState):  # All movement
        output = boardState

        if move != None:

            if self.__color == "White":
                # Finds all White Pieces
                # (that are not the piece that is moving) and adds 1 move to the time since last move attribute

                for square in output.dict:

                    if square != move.coords()[0] and output.dict[square] != None and output.dict[
                        square].color() == self.__color:
                        output.dict[square].wait()

            if self.__color == "Black":

                for square in output.dict:

                    if square != move.coords()[0] and output.dict[square] != None and output.dict[
                        square].color() == self.__color:
                        output.dict[square].wait()

            if move.moveType() == "Normal" or move.moveType() == "Promotion":
                pointA, pointB = move.coords()[0], move.coords()[1]

                pointAcontents = boardState.dict.get(pointA)  # Gets the information about the moving piece
                pointAcontents.move(pointB)

                output.dict[pointA] = None
                output.dict[pointB] = pointAcontents

                if move.moveType() == "Promotion":
                    self.remove(output.dict[pointB])  # Removes pawn from material Pool
                    output.dict[pointB].promote()
                    self.append(output.dict[pointB])  # Adds new Queen to the material pool

                    print(f"{self.__material} Material After Promotion")

            elif move.moveType() == "En Passant":

                pointA, pointB = move.coords()[0], move.coords()[1]

                if self.__color == "White":

                    pointB = pointB[0] + str(int(pointB[1]) + 1)

                else:

                    pointB = pointB[0] + str(int(pointB[1]) - 1)

                pointAcontents = boardState.dict.get(pointA)
                pointAcontents.move(pointB)

                pointBcontents = boardState.dict.get(move.coords()[1])

                output.dict[move.coords()[1]] = None

                output.dict[pointA] = None
                output.dict[pointB] = pointAcontents

                # Removing Material (Separated for readability and clarity)

                if self.__color == "White":

                    boardState.blackPieces.remove(pointBcontents)

                else:

                    boardState.whitePieces.remove(pointBcontents)

            elif move.moveType() == "Short-Castle":  # Castling Short

                if self.__color == "White":

                    # King Movement

                    kPointA, kPointB = move.coords()[0], move.coords()[1]

                    king = boardState.dict.get(kPointA)  # King
                    king.addMove()
                    king.setSquare(kPointB)

                    output.dict[kPointB] = king  # King moves to point B
                    output.dict[kPointA] = None  # The old King's square is now empty

                    # Moving the Rook

                    rPointA = "H" + "1"
                    rPointB = "F" + "1"

                    rook = boardState.dict.get(rPointA)
                    rook.addMove()
                    rook.setSquare(rPointB)

                    boardState.dict[rPointB] = rook
                    boardState.dict[rPointA] = None

                else:

                    #  King Movement

                    kPointA, kPointB = move.coords()[0], move.coords()[1]

                    king = boardState.dict.get(kPointA)  # King
                    king.addMove()
                    king.setSquare(kPointB)

                    output.dict[kPointB] = king
                    output.dict[kPointA] = None

                    #  Rook Movement

                    rPointA = "H" + "8"
                    rPointB = "F" + "8"

                    rook = boardState.dict.get(rPointA)
                    rook.addMove()
                    rook.setSquare(rPointB)

                    output.dict[rPointB] = rook
                    output.dict[rPointA] = None

            elif move.moveType() == "Long-Castle":

                if self.__color == "White":

                    # King Movement

                    kPointA, kPointB = move.coords()[0], move.coords()[1]

                    king = boardState.dict.get(kPointA)
                    king.addMove()
                    king.setSquare(kPointB)

                    output.dict[kPointB] = king
                    output.dict[kPointA] = None

                    # Rook Movement

                    rPointA = "A" + "1"
                    rPointB = "D" + "1"

                    rook = boardState.dict.get(rPointA)
                    rook.addMove()
                    rook.setSquare(rPointB)

                    output.dict[rPointB] = rook
                    output.dict[rPointA] = None

                else:

                    # King Movement

                    kPointA, kPointB = move.coords()[0], move.coords()[1]

                    king = boardState.dict.get(kPointA)
                    king.addMove()
                    king.setSquare(kPointB)

                    output.dict[kPointB] = king
                    output.dict[kPointA] = None

                    # Rook Movement

                    rPointA = "A" + "8"
                    rPointB = "D" + "8"

                    rook = boardState.dict.get(rPointA)
                    rook.addMove()
                    rook.setSquare(rPointB)

                    output.dict[rPointB] = rook
                    output.dict[rPointA] = None

            else:  # Taking

                pointA, pointB = move.coords()[0], move.coords()[1]

                pointAcontents = boardState.dict.get(pointA)
                pointAcontents.move(pointB)

                pointBcontents = boardState.dict.get(pointB)

                output.dict[pointA] = None
                output.dict[pointB] = pointAcontents

                if self.__color == "White":  # White takes Black
                    output.blackPieces.remove(pointBcontents)
                    output.blackPieces.calculateMaterial()

                else:  # Black Takes White
                    output.whitePieces.remove(pointBcontents)
                    output.whitePieces.calculateMaterial()

            return output


class BoardState(object):  # Keeps the information of piece locations

    def __init__(self, copy=False):

        self.dict = {}
        self.whitePieces = Side("White")
        self.blackPieces = Side("Black")
        self.path = "Resources/Data/StartPositions"

        def cleanImport(target):  # Useful fore multiple functions, Saves alot of time

            def openFile():
                with open(target + ".csv", "rt") as text_file:
                    step1 = csv.reader(text_file)
                    output = list(step1)
                    return output

            rawImport = openFile()

            del rawImport[0]  # Removes Headers

            return rawImport

        for row in cleanImport("Resources/Data/SquareCoords"):
            self.dict[row[0]] = None

        for row in cleanImport(self.path):

            if str(row[1]) == "White":
                self.whitePieces.append(Piece(row[0], row[1], row[2]))

            else:
                self.blackPieces.append(Piece(row[0], row[1], row[2]))

            self.dict[row[2]] = Piece(row[0], row[1], row[2])

    def displayPieces(self):  # Prints all the pieces associated with each side along with the material count
        print("WhitePieces: ")
        for piece in self.whitePieces.contents():
            print(piece, end=",")

        print("\n")
        print(self.whitePieces.material())
        print("\n")

        print("BlackPieces: ")

        for piece in self.blackPieces.contents():
            print(piece, end=",")

        print("\n")
        print(self.blackPieces.material())
        print("\n")

    def setFilePath(self, path):

        self.whitePieces = Side("White")
        self.blackPieces = Side("Black")

        def cleanImport(target):  # Useful fore multiple functions, Saves alot of time

            def openFile():
                with open(target + ".csv", "rt") as text_file:
                    step1 = csv.reader(text_file)
                    output = list(step1)
                    return output

            rawImport = openFile()

            del rawImport[0]  # Removes Headers

            return rawImport

        self.path = path

        for row in cleanImport("Resources/Data/SquareCoords"):
            self.dict[row[0]] = None

        for row in cleanImport(self.path):

            if str(row[1]) == "White":
                self.whitePieces.append(Piece(row[0], row[1], row[2]))

            else:
                self.blackPieces.append(Piece(row[0], row[1], row[2]))

            self.dict[row[2]] = Piece(row[0], row[1], row[2])

    def detectGameState(self):

        if self.whitePieces.material() == 0 and self.blackPieces.material() == 0:
            print("A stalemated Position")
            return "StaleMate"

        elif self.whitePieces.digestPossibleMoves(self) == 0 and self.blackPieces.digestPossibleMoves(self) == 0:
            return "StaleMate"

        # Check for checkmates

        elif self.whitePieces.returnCheckStatus() == True and len(self.whitePieces.digestPossibleMoves(self)) == 0:
            return "BlackMate"  # White has no moves and is in the status of check

        elif self.blackPieces.returnCheckStatus() == True and len(self.blackPieces.digestPossibleMoves(self)) == 0:
            return "WhiteMate"  # Black has no moves and is in the status of check

    def __str__(self):  # Display What Is Inside Of The boardState

        output = ""

        allFiles = ["A", "B", "C", "D", "E", "F", "G", "H"]

        for file in allFiles:
            print(f"  {file}  ", end="  ")

        print("\n")

        for i in range(1, 9):

            for file in allFiles:

                try:

                    output += " [" + str(self.dict.get(str(file) + str(i)).code()) + "] "


                except:
                    output += " [   ] "

            output += "\n \n \n"

        return output

    def findAllMoves(self, currentColor, isOutput=False):

        if currentColor == "White":
            return self.whitePieces.digestPossibleMoves(self, isOutput)

        else:
            return self.blackPieces.digestPossibleMoves(self, isOutput)

    def takeInput(self, inp, currentColor):  # Just to take the users input and communicate with the program

        if inp < 1:
            print("Invalid Input")
            return None  # Breaks out of the function when an index that is less than 0 is inputed

        if currentColor == "White":

            self = self.whitePieces.move(self.whitePieces.possibleMoves()[inp - 1], self)
            print(self)

        else:
            self = self.blackPieces.move(self.blackPieces.possibleMoves()[inp - 1], self)
            print(self)


# Main
if __name__ == "__main__":
    # Only runs if the file isn't Imported (this makes it easier to use external files for AI and front end GUI)

    running = True
    mainBoard = BoardState()
    currentColor = "White"
    while running:

        print(mainBoard)
        mainBoard.findAllMoves(currentColor, True)

        if len(mainBoard.findAllMoves(currentColor)) == 0:

            if currentColor == "White":
                print("Black Wins By Checkmate")
                break

            else:
                print("White Wins By Checkmate")
                break



        else:
            try:
                moveIndex = int(input("Please enter the number of the move you wish to perform"))
                mainBoard.takeInput(moveIndex, currentColor)

                if currentColor == "White":

                    currentColor = "Black"
                    otherColor = "White"

                else:
                    currentColor = "White"
                    otherColor = "Black"
            except:
                print("Invalid Input")
