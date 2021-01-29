from chess import Board
import numpy as np

WHITE_VALUES = {Board.W_PAWN: 1, Board.W_KNIGHT: 3, Board.W_BISHOP: 3, Board.W_ROOK: 4, Board.W_QUEEN: 8, Board.W_KING: 100}
BLACK_VALUES = {Board.B_PAWN: 1, Board.B_KNIGHT: 3, Board.B_BISHOP: 3, Board.B_ROOK: 4, Board.B_QUEEN: 8, Board.B_KING: 100}
def value_heuristic1(board, self_color):
    assert self_color in (Board.WHITE, Board.BLACK)
    assert isinstance(board, Board)
    total_value = 0
    # Count pieces
    for i in range(8):
        for j in range(8):
            piece = board.board[i][j]
            color = board.get_color(i, j)
            multiplier = 1 if color == self_color else -1
            if color == Board.WHITE:
                total_value += multiplier * WHITE_VALUES[piece] 
            elif color == Board.BLACK:
                total_value += multiplier * BLACK_VALUES[piece] 
    return total_value

cached_boards = [Board() for i in range(10)]  # predefine boards
def value_minimax(board, self_color, heuristic, recursion=2, noise=0):
    '''
    Assumes that all heuristics are zero-sum (symmetrical)
    '''
    assert self_color in (Board.WHITE, Board.BLACK)
    assert isinstance(board, Board)
    # Gather all moves
    if recursion == 0:
        # Run heuristic
        v = value_heuristic1(board, self_color)
        if noise > 0:
            v += np.random.uniform(low=-noise, high=noise)
        return v, None, 1
    else:
        # Get all possible actions
        actions = board.get_all_actions(self_color, enable_comments=False)
        # For each action, get minimax estimate
        estimates = []
        heuristic_evaluations = 0
        for (i, j, I, J) in actions:
            new_board = board.clone(cached_boards[recursion])
            new_board.move_actual(i, j, I, J, actions)
            other_minimax_estimate, __, other_heuristic_evaluations = value_minimax(new_board, board.opposite(self_color), heuristic, recursion=recursion-1, noise=noise)
            self_minimax_estimate = -other_minimax_estimate

            estimates.append((self_minimax_estimate, (i, j, I, J)))
            heuristic_evaluations += other_heuristic_evaluations
        estimates = list(sorted(estimates, reverse=True))
        if recursion == 3:
            print('estimates')
            for score, (i,j,I,J) in estimates:
                print('{}: {}'.format(score, board.pretty_action(i, j, I, J)))
                break
        # returns: best score, best action, number of heuristic evals
        return estimates[0][0], estimates[0][1], heuristic_evaluations


def print_value_heuristic1(board):
    v = value_heuristic1(board, Board.WHITE)
    print('Heuristic 1: White={:.3f}'.format(v))

def print_value_minimax2(board):
    v, evals = value_minimax(board, Board.WHITE, value_heuristic1, recursion=2)
    print('Heuristic 1: White={:.3f} ({} evals)'.format(v, evals))

def closure_value_minimax(board, self_color):
    score, action, n_evals = value_minimax(board, self_color, value_heuristic1, recursion=3, noise=0.1)
    return score, action, n_evals


if __name__ == '__main__':
    #board = Board().play_interactive('c2c3 d1a4 a4a7 a7b8 b8c8 c8d8 d8e8', hooks=[print_value_heuristic1])
    #board = Board().play_interactive('c2c3 d1a4 a4a7 a7b8 b8c8 d8c8 a8a2 a2a1', hooks=[print_value_heuristic1])
    #board = Board().play_interactive('c2c3 d1a4 a4a7 a7b8 b8c8 d8c8 a8a2 a2a1', hooks=[print_value_minimax2])

    board = Board()
    board.self_play(closure_value_minimax)
