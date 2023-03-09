# This will hold the Artificial computation
import random  # For when the AI has multiple best moves
import csv  # For data importing from external files
import copy  # For creating copies of board states for analysis

currentMoves = []  # A simple global variable that stores played moves


def updateMoveOrder(moveOrder):  # Pulls the moveOrder from the GUI to allow opening Identification, Purely a public
    # Function.
    global currentMoves
    currentMoves = moveOrder


def convertMoveOrder(moveOrderIn):  # This function will convert the move order from a list of lists into a single list

    output = []

    for entry in moveOrderIn:  # For each set of moves in the input parameter

        for move in entry:  # For each move that has been played in that move index
            output.append(move)

    return output


def returnAiResponse(board):  # Reads In Possible Moves and chooses from them
    global currentMoves # Basic input from main program
    moves = board.blackPieces.digestPossibleMoves(board) # Moves that are available to the ai
    colour = "Black"
    """ This is the important move list as this is in a digestible format for the computer to read"""
    playedMoves = convertMoveOrder(currentMoves)  # Single list format
    if len(moves) != 0:
        return random.choice(moves)

    else:
        print("No Moves for the AI to play")

