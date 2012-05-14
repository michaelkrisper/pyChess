class Piece(object):
    def __init__(self, name, isBlack):
        self.name = name
        self.isBlack = isBlack
        
    def __str__(self):
        if self.isBlack:
            return "\x1b[31m%s" % self.name
        else:
            return "\x1b[34m%s" % self.name

class Tile(object):
    def __init__(self, isBlack):
        self.isBlack = isBlack
        self.piece = " "
        
    def __str__(self):
        if self.isBlack:
            return "\x1b[0m\x1b[47m %s \x1b[0m" % self.piece
        else:
            return "\x1b[0m %s " % self.piece

def main():
    board = [[Tile(((row+col) % 2 == 0)) for row in range(8)] for col in range(8)]
    startPositions(board)
    printBoard(board)
    
    
def startPositions(board):
    for cell in board[1]:
        cell.piece = Piece("B", True)

    for cell in board[-2]:
        cell.piece = Piece("B", False)
  
    color = True
    for line in (0, -1):
        board[line][0].piece = Piece("T", color)
        board[line][1].piece = Piece("S", color)
        board[line][2].piece = Piece("L", color)
        board[line][3].piece = Piece("K", color)
        board[line][4].piece = Piece("D", color)
        board[line][5].piece = Piece("L", color)
        board[line][6].piece = Piece("S", color)
        board[line][7].piece = Piece("T", color)
        color = False

def printBoard(board):
    rows = []
    borderrow = "+" + "-" * (len(board[0]) * 3) + "+"

    rows.append(borderrow)
    for row in board:
        rows.append("\x1b[0m|" + "".join(map(str, row)) + "\x1b[0m|")
    rows.append(borderrow)
    print "\n".join(rows)

if __name__ == '__main__':
    main()
