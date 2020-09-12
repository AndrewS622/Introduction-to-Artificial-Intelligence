"""
Tic Tac Toe Player
"""

import math

from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    numX = 0
    numO = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                numX += 1
            elif board[i][j] == O:
                numO += 1
    if numX > numO:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                moves.add((i, j))
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    newboard = deepcopy(board)
    i = action[0]
    j = action[1]
    if board[i][j] == EMPTY:
        newboard[i][j] = player(board)
        return newboard
    else:
        raise ValueError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        if board[i][0] == board[i][1] and board[i][1] == board[i][2] and board[i][0] is not None:
            return board[i][0]
        elif board[0][i] == board[1][i] and board[1][i] == board[2][i] and board[0][i] is not None:
            return board[0][i]
    if board[0][0] == board[1][1] and board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    elif board[2][0] == board[1][1] and board[1][1] == board[0][2] and board[2][0] is not None:
        return board[2][0]
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False
    else:
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if player(board) == X:
        # choose action that produces highest value of Min-Value(Result(s,a))
        v = -2
        acts = actions(board)
        for act in acts:
            v_act = Min_Value(result(board, act), v)
            if v_act > v:
                act_opt = act
                v = v_act

        return act_opt

    else:
        # choose action that produces the smallest value of Max-Value(Result(s,a))
        v = 2
        acts = actions(board)
        for act in acts:
            v_act = Max_Value(result(board, act), v)
            if v_act < v:
                act_opt = act
                v = v_act

        return act_opt


def Min_Value(board, v):
    if terminal(board):
        return utility(board)
    v_list = list()
    for action in actions(board):
        v_list.append(Max_Value(result(board, action), v))
        if v_list[-1] < v:
            return v_list[-1]
    return min(v_list)



def Max_Value(board, v):
    if terminal(board):
        return utility(board)
    v_list = list()
    for action in actions(board):
        v_list.append(Min_Value(result(board, action), v))
        if v_list[-1] > v:
            return v_list[-1]
    return max(v_list)

