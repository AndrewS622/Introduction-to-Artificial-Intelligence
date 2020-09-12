from tictactoe import initial_state, player, actions, result, winner, terminal, utility

X = "X"
O = "O"
EMPTY = None


print('Initial State:')
board = initial_state()
print(board)

print(player(board))

print(actions(board))

print(result(board, (1, 1)))

print(winner(board))

print(terminal(board))

print('Second Move:')
board = result(board, (1, 1))
print(player(board))

print(actions(board))

print(winner(board))

print('Ending Scenarios:')
board = [[X, X, X], [O, EMPTY, O], [O, X, EMPTY]]
print(winner(board))
print(terminal(board))
print(utility(board))

board = [[X, O, X], [X, EMPTY, O], [X, O, EMPTY]]
print(winner(board))
print(terminal(board))
print(utility(board))

board = [[O, O, X], [X, O, EMPTY], [X, X, O]]
print(winner(board))
print(terminal(board))
print(utility(board))

board = [[O, O, X], [O, EMPTY, O], [X, X, X]]
print(winner(board))
print(terminal(board))
print(utility(board))

board = [[X, O, X], [X, X, O], [O, O, O]]
print(winner(board))
print(terminal(board))
print(utility(board))

board = [[X, EMPTY, O], [X, O, O], [O, X, X]]
print(winner(board))
print(terminal(board))
print(utility(board))

board = [[O, X, X], [X, X, O], [O, O, X]]
print(winner(board))
print(terminal(board))
print(utility(board))

board = [[EMPTY, X, X], [EMPTY, O, X], [EMPTY, O, X]]
print(winner(board))
print(terminal(board))
print(utility(board))