import numpy as np

class InvalidMove(Exception):
    pass

class ConversionError(Exception):
    pass

class Board:

    NIL = 0

    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

    WHITE = 10
    BLACK = 20

    W_PAWN = PAWN + WHITE
    W_KNIGHT = KNIGHT + WHITE
    W_BISHOP = BISHOP + WHITE
    W_ROOK = ROOK + WHITE
    W_QUEEN = QUEEN + WHITE
    W_KING = KING + WHITE

    B_PAWN = PAWN + BLACK
    B_KNIGHT = KNIGHT + BLACK
    B_BISHOP = BISHOP + BLACK
    B_ROOK = ROOK + BLACK
    B_QUEEN = QUEEN + BLACK
    B_KING = KING + BLACK

    WHITE_PIECES = (W_PAWN, W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN, W_KING)
    BLACK_PIECES = (B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING)

    j2COLUMN = 'ABCDEFGH'
    i2ROW = '87654321'
    COLUMN2j = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
    ROW2i = {'8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7}

    def __init__(self):
        self.reset_board()

    def reset_board(self):
        self.board = np.zeros((8, 8), dtype=np.uint8)

        # Place black pieces at top of board
        self.board[self.ROW2i['8']] = np.asarray([self.B_ROOK, self.B_KNIGHT, self.B_BISHOP, self.B_QUEEN, self.B_KING, self.B_BISHOP, self.B_KNIGHT, self.B_ROOK])
        self.board[self.ROW2i['7']] = np.asarray([self.B_PAWN, self.B_PAWN, self.B_PAWN, self.B_PAWN, self.B_PAWN, self.B_PAWN, self.B_PAWN, self.B_PAWN])

        # Place white pieces at bottom of board
        self.board[self.ROW2i['2']] = np.asarray([self.W_PAWN, self.W_PAWN, self.W_PAWN, self.W_PAWN, self.W_PAWN, self.W_PAWN, self.W_PAWN, self.W_PAWN])
        self.board[self.ROW2i['1']] = np.asarray([self.W_ROOK, self.W_KNIGHT, self.W_BISHOP, self.W_QUEEN, self.W_KING, self.W_BISHOP, self.W_KNIGHT, self.W_ROOK])

        self.w_captured = []
        self.b_captured = []

    def print_raw(self):
        print(self.board)

    def move_str(self, rowcolumnROWCOLUMN):
        rowcolumnROWCOLUMN = rowcolumnROWCOLUMN.strip(' ->\n')
        if len(rowcolumnROWCOLUMN) != 4:
            raise ValueError('Bad move string')
        rowcolumnROWCOLUMN = rowcolumnROWCOLUMN.upper()

        rowcolumn, ROWCOLUMN = rowcolumnROWCOLUMN[0:2], rowcolumnROWCOLUMN[2:4]
        i, j = self.to_ij(rowcolumn)
        I, J = self.to_ij(ROWCOLUMN)
        return self.move(i, j, I, J)

    def to_coord(self, i, j):
        try:
            return '{}{}'.format(self.i2ROW[i], self.j2COLUMN[j])
        except KeyError:
            raise ConversionError('Cannot convert indices {} to coordinates'.format((i, j)))
        
    def to_ij(self, columnrow):
        column, row = columnrow
        try:
            return self.ROW2i[row], self.COLUMN2j[column]
        except KeyError:
            raise ConversionError('Cannot convert coordinates {} to ij'.format(columnrow))

    def move_actual(self, i, j, I, J, actions, comments, color):
        winner = self.NIL
        comment = []
        if (i, j, I, J) in actions:
            # Ok move, execute
            tgt_color = self.get_color(I, J)
            comment.append('Moving {}: {}->{} // {}'.format(self.to_unicode(self.board[i][j]), self.to_coord(i,j), self.to_coord(I,J), comments[(i, j, I, J)]))
            if tgt_color == self.opposite(color):
                # Is a capture
                comment.append('Captured {}'.format(self.to_unicode(self.board[I][J])))   
                if tgt_color == self.WHITE:
                    self.w_captured.append(self.board[I][J])
                    if self.board[I][J] == self.W_KING:
                        winner = self.BLACK
                        comment.append('BLACK WINS')
                elif tgt_color == self.BLACK:
                    self.b_captured.append(self.board[I][J])
                    if self.board[I][J] == self.B_KING:
                        winner = self.WHITE
                        comment.append('WHITE WINS')
            elif tgt_color == color:
                raise Exception('This should never happen')     
            # Update target and clear source
            self.board[I][J] = self.board[i][j]
            self.board[i][j] = self.NIL
        else:
            comment.append('Invalid Move for {}: {}->{} // {}'.format(self.to_unicode(self.board[i][j]), self.to_coord(i,j), self.to_coord(I,J), comments.get((i, j, I, J), 'Piece cannot move that way')))
            raise InvalidMove()
        return winner, '\n'.join(comment)

    def move(self, i, j, I, J):
        # Identify piece
        actions, comments, color = self.get_actions(i, j)
        return self.move_actual(i, j, I, J, actions, comments, color)

    def opposite(self, color):
        if color == self.WHITE:
            return self.BLACK
        elif color == self.BLACK:
            return self.WHITE
        elif color == self.NIL:
            return self.NIL
        else:
            raise Exception('Opposite color only makes sense for WHITES BLACKS and NIL')

    def get_actions(self, i, j):
        '''
        EN PASSANT not implemented
        CASTLING not implemented
        '''
        # Identify piece
        actions = []
        comments = {}
        color = self.get_color(i, j)

        # Is empty cell
        if self.board[i][j] == self.NIL:
            pass  # nothing to do, no action possible
        # Is a PAWN
        elif self.board[i][j] in (self.W_PAWN, self.B_PAWN):
            fwd = -1 if color == self.WHITE else 1
            # Advance twice
            I, J = i+2*fwd, j 
            # this logic should make sense because pawns cannot move backwards
            if (color == self.WHITE and i == self.ROW2i['2']) or (color == self.BLACK and i == self.ROW2i['7']):
                actions.append((i, j, I, J))
                comments[(i, j, I, J)] = 'PAWN advances for two-squares'
            else:
                comments[(i, j, I, J)] = 'PAWN cannot advance for two-squares because it has moved before'
            # Advance once 
            I, J = i+fwd, j
            if self.in_limits(I, J):
                if self.get_color(I, J) == self.NIL:
                    actions.append((i, j, I, J))
                    comments[(i, j, I, J)] = 'PAWN advances to free space'
                else:
                    comments[(i, j, I, J)] = 'PAWN is blocked from advancing'
            # Move diagonally
            for I, J in [(i+fwd, j-1), (i+fwd, j+1)]:
                if self.in_limits(I, J):
                    tgt_color = self.get_color(I, J)
                    if tgt_color == color:
                        comments[(i, j, I, J)] = 'PAWN cannot capture own color'
                    elif tgt_color == self.NIL:
                        comments[(i, j, I, J)] = 'PAWN cannot capture empty cell'
                    else:
                        actions.append((i, j, I, J))
                        comments[(i, j, I, J)] = 'PAWN captures diagonally'
        # Is a KNIGHT
        elif self.board[i][j] in (self.W_KNIGHT, self.B_KNIGHT):
            for I, J in [(i+2, j+1), (i+2, j-1), (i-2, j+1), (i-2, j-1), (i+1, j+2), (i+1, j-2), (i-1, j+2), (i-1, j-2)]:
                if self.in_limits(I, J):
                    tgt_color = self.get_color(I, J)
                    if tgt_color == color:
                        comments[(i, j, I, J)] = 'KNIGHT cannot capture own color'
                    elif tgt_color == self.NIL:
                        actions.append((i, j, I, J))
                        comments[(i, j, I, J)] = 'KNIGHT jumps to free space'
                    else:
                        actions.append((i, j, I, J))
                        comments[(i, j, I, J)] = 'KNIGHT captures adversary'
        # Is a BISHOP
        elif self.board[i][j] in (self.W_BISHOP, self.B_BISHOP):
            # Explore each diagonal from 1 to 7 steps
            for di, dj in [(1, 1,), (1, -1), (-1, 1), (-1, -1)]:
                for steps in range(1, 8):
                    # Can step until interrupted or out of board
                    I, J = i+di*steps, j+dj*steps
                    if not self.in_limits(I, J):
                        break
                    tgt_color = self.get_color(I, J)
                    if tgt_color == color:
                        comments[(i, j, I, J)] = 'BISHOP cannot capture own color'
                        break
                    elif tgt_color == self.NIL:
                        actions.append((i, j, I, J))
                        comments[(i, j, I, J)] = 'BISHOP slides to free space'
                    else:
                        actions.append((i, j, I, J))
                        comments[(i, j, I, J)] = 'BISHOP captures adversary'
                        break
        # Is a ROOK
        elif self.board[i][j] in (self.W_ROOK, self.B_ROOK):
            # Explore each vertical and horizontal from 1 to 7 steps
            for di, dj in [(1, 0,), (-1, 0), (0, 1), (0, -1)]:
                for steps in range(1, 8):
                    # Can step until interrupted or out of board
                    I, J = i+di*steps, j+dj*steps
                    if not self.in_limits(I, J):
                        break
                    tgt_color = self.get_color(I, J)
                    if tgt_color == color:
                        comments[(i, j, I, J)] = 'ROOK cannot capture own color'
                        break
                    elif tgt_color == self.NIL:
                        actions.append((i, j, I, J))
                        comments[(i, j, I, J)] = 'ROOK slides to free space'
                    else:
                        actions.append((i, j, I, J))
                        comments[(i, j, I, J)] = 'ROOK captures adversary'  
                        break
        # Is a QUEEN     
        elif self.board[i][j] in (self.W_QUEEN, self.B_QUEEN):
            # Explore each diagonal, vertical and horizontal from 1 to 7 steps
            for di, dj in [(1, 1,), (1, -1), (-1, 1), (-1, -1), (1, 0,), (-1, 0), (0, 1), (0, -1)]:
                for steps in range(1, 8):
                    # Can step until interrupted or out of board
                    I, J = i+di*steps, j+dj*steps
                    if not self.in_limits(I, J):
                        break
                    tgt_color = self.get_color(I, J)
                    if tgt_color == color:
                        comments[(i, j, I, J)] = 'QUEEN cannot capture own color'
                        break
                    elif tgt_color == self.NIL:
                        actions.append((i, j, I, J))
                        comments[(i, j, I, J)] = 'QUEEN slides to free space'
                    else:
                        actions.append((i, j, I, J))
                        comments[(i, j, I, J)] = 'QUEEN captures adversary'  
                        break
        # Is a KING     
        elif self.board[i][j] in (self.W_KING, self.B_KING):
            # Explore each diagonal, vertical and horizontal from 1 to 7 steps
            for di, dj in [(1, 1,), (1, -1), (-1, 1), (-1, -1), (1, 0,), (-1, 0), (0, 1), (0, -1)]:
                steps = 1  # same as QUEEN but only 1 step
                # Can step until interrupted or out of board
                I, J = i+di*steps, j+dj*steps
                if not self.in_limits(I, J):
                    continue
                tgt_color = self.get_color(I, J)
                if tgt_color == color:
                    comments[(i, j, I, J)] = 'KING cannot capture own color'
                elif tgt_color == self.NIL:
                    actions.append((i, j, I, J))
                    comments[(i, j, I, J)] = 'KING slides to free space'
                else:
                    actions.append((i, j, I, J))
                    comments[(i, j, I, J)] = 'KING captures adversary'  

        return actions, comments, color

    def in_limits(self, i, j):
        return 0 <= i <= 7 and 0 <= j <= 7
    

    def get_color(self, i, j):
        if self.board[i][j] == self.NIL:
            return self.NIL
        elif self.board[i][j] in self.BLACK_PIECES:
            return self.BLACK
        elif self.board[i][j] in self.WHITE_PIECES:
            return self.WHITE
        else:
            raise Exception('Invalid value at cell ({},{}): {}'.format(i, j, self.board[i][j]))

    def __repr__(self):
        return 'Chess board:\n{}'.format(str(self))

    def pretty_actions_at_coord(self, coord):
        coord = coord.upper()
        if len(coord) != 2:
            raise ValueError('Bad move string')
        i, j = self.to_ij(coord)
        actions, comments, color = self.get_actions(i, j)
        possible_dst = set([(I, J) for i, j, I, J in actions])
        return self.__str__(src=[(i, j)],dst=possible_dst)

    def __str__(self, src=None, dst=None):
        if src is None:
            src = set()
        if dst is None:
            dst = set()
        s = []
        s.append('(blacks captured: {})\n'.format(''.join([self.to_unicode(p) for p in self.b_captured])))
        s.append('╔═A═╤═B═╤═C═╤═D═╤═E═╤═F═╤═G═╤═H═╗\n')
        for i in range(8):
            s.append('{}'.format('87654321'[i]))
            for j in range(8):
                if (i, j) in src:
                    s.append(' {}?'.format(self.to_unicode(self.board[i][j])))
                elif (i, j) in dst:
                    s.append('[{}]'.format(self.to_unicode(self.board[i][j])))
                else:
                    s.append(' {} '.format(self.to_unicode(self.board[i][j])))
                if j<7:
                    s.append('│')
            s.append('{}\n'.format('87654321'[i]))
            if i<7:
                s.append('╟───┼───┼───┼───┼───┼───┼───┼───╢\n')
        s.append('╚═A═╧═B═╧═C═╧═D═╧═E═╧═F═╧═G═╧═H═╝\n')
        s.append(' (whites captured: {})'.format(''.join([self.to_unicode(p) for p in self.w_captured])))
        return ''.join(s)

    def to_unicode(self, piece):
        # https://en.wikipedia.org/wiki/Chess_symbols_in_Unicode
        if piece == self.W_KING:
            return '\u2654'
        elif piece == self.W_QUEEN:
            return '\u2655'
        elif piece == self.W_ROOK:
            return '\u2656'
        elif piece == self.W_BISHOP:
            return '\u2657'
        elif piece == self.W_KNIGHT:
            return '\u2658'
        elif piece == self.W_PAWN:
            return '\u2659'
        #
        elif piece == self.B_KING:
            return '\u265A'
        elif piece == self.B_QUEEN:
            return '\u265B'
        elif piece == self.B_ROOK:
            return '\u265C'
        elif piece == self.B_BISHOP:
            return '\u265D'
        elif piece == self.B_KNIGHT:
            return '\u265E'
        elif piece == self.B_PAWN:
            return '\u265F'
        elif piece == self.NIL:
            return ' '
        else:
            raise Exception('Bad piece')
        
        

def play_interactive(buffer=''):
    board = Board()
    print(board)
    while True:
        # Preprocess buffer
        if buffer != '':
            buffer = buffer.strip(' \n')
            tokens = buffer.split()
            if len(tokens) == 0:
                continue
            move_or_ij, buffer = tokens[0], ' '.join(tokens[1:])
            print('\n? {}'.format(move_or_ij))
        else:
            buffer = input('(buffer) ')
            continue

        try:
            if len(move_or_ij) == 4:
                winner, comment = board.move_str(move_or_ij)
                print(comment)
                print(board)
                if winner != board.NIL:
                    break
            elif len(move_or_ij) == 2:
                print('Possible moves for {}\n{}'.format(move_or_ij, board.pretty_actions_at_coord(move_or_ij)))
            else:
                print('Please enter a move (e.g. "g2f2") or a coordinate (e.g. "h1")')
        except InvalidMove as e:
                    print('InvalidMove "{}": {}'.format(move_or_ij, e))            
        except ConversionError as e:
                    print('ConversionError: {}'.format(e))
              



if __name__ == '__main__':
    #play_interactive('a2a3 a3a4 a1a3 a3h3 b2b3 d2d3 f1f2 f2f3 f3f4 d3d4 e2e3 e3e4 e4e5 g1 c1 b1 g1 e1')  # bunch of tests
    #play_interactive('a2a3 a3 b2')  # pawn advance
    #play_interactive('e2e3 d1f3 f3f7 f7e8')  # white wins
    play_interactive('b8c6 c6d4 d4f3 f3e1')  # black wins