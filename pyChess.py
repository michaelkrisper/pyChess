#! /usr/local/bin python
# -*- coding: UTF-8 -*-
__author__ = "Michael Krisper
__date__ = "2012-05-14"
__python__ = "2.7.3"


def singleton(cls):
    return cls()

@singleton
class ChessSymbols(object):
    def __init__(self):
        if True:
            self.QUEEN = "♛"
            self.KING = "♚"
            self.BISHOP = "♝"
            self.KNIGHT = "♞"
            self.PAWN = "♟"
            self.ROOK = "♜"
        else:
            self.QUEEN = "D"
            self.KING = "K"
            self.BISHOP = "L"
            self.KNIGHT = "S"
            self.PAWN = "B"
            self.ROOK = "T"
        
class Piece(object):
    def __init__(self, name, isBlack):
        self.name = name
        self.isBlack = isBlack

    def __str__(self):
        if self.isBlack:
            return "\x1b[31m%s" % self.name
        else:
            return "\x1b[34m%s" % self.name
    
    def isMoveAllowed(self, fromTile, toTile):
        raise NotImplementedError("Method not implemented: Piece.isMoveAllowed")
    
    def move(self, fromTile, toTile):
        if self.isMoveAllowed(fromTile, toTile):
            toTile.piece = self
            fromTile.piece = None
        else:
            print "move not allowed"

class Bauer(Piece):
    def __init__(self, isBlack):
        Piece.__init__(self, ChessSymbols.PAWN, isBlack)

    def isMoveAllowed(self, fromTile, toTile):
        if self.isBlack:
            if (fromTile.getTile(0, 1) == toTile and toTile.piece == None) \
            or ((fromTile.getTile(1, -1) == toTile or fromTile.getTile(1, 1) == toTile) and toTile.piece != None and not toTile.piece.isBlack):
                return True
        else:
            if (fromTile.getTile(0, -1) == toTile and toTile.piece == None) \
            or ((fromTile.getTile(-1, -1) == toTile or fromTile.getTile(-1, 1) == toTile) and toTile.piece != None and toTile.piece.isBlack):
                return True
        return False

class Laufer(Piece):
    def __init__(self, isBlack):
        Piece.__init__(self, ChessSymbols.BISHOP, isBlack)
    
    def isMoveAllowed(self, fromTile, toTile):
        for i in range(1, 8):
            if fromTile.getTile(i, i) == toTile:
                return True
            elif fromTile.getTile(i, i).piece != None:
                break

        for i in range(1, 8):
            if fromTile.getTile(-i, i) == toTile:
                return True
            elif fromTile.getTile(-i, i).piece != None:
                break

        for i in range(1, 8):
            if fromTile.getTile(i, -i) == toTile:
                return True
            elif fromTile.getTile(i, -i).piece != None:
                break

        for i in range(1, 8):
            if fromTile.getTile(-i, -i) == toTile:
                return True
            elif fromTile.getTile(-i, -i).piece != None:
                break
        return False

class Tile(object):
    def __init__(self, isBlack, board, col, row):
        self.isBlack = isBlack
        self.board = board
        self.col = col
        self.row = row
        self.piece = None
        
    def __str__(self):
        if self.isBlack:
            return "\x1b[0m\x1b[47m %s \x1b[0m" % (self.piece if self.piece else " ")
        else:
            return "\x1b[0m %s \x1b[0m" % (self.piece if self.piece else " ")
        
    def movePieceTo(self, toTile):
        self.piece.move(self, toTile)
        
    def getTile(self, col, row):
        if (0 <= (self.row + row) < len(self.board)) and (0 <= (self.col + col) < len(self.board[0])):
            return self.board[self.row + row][self.col + col]
        else:
            return None

class Game(object):

    
    def __init__(self):
        self.board = []
        self._init_board()
        self._set_start_positions()

    def _init_board(self):
        self.board.extend(([Tile(((row + col) % 2 == 0), self.board, col, row) for col in range(8)] for row in range(8))) 
    
    def _set_start_positions(self):
        for cell in self.board[1]:
            cell.piece = Bauer(True)
    
        for cell in self.board[-2]:
            cell.piece = Bauer(False)
      
        color = True
        for line in [0, -1]:
            self.board[line][0].piece = Piece(ChessSymbols.ROOK, color)
            self.board[line][1].piece = Piece(ChessSymbols.KNIGHT, color)
            self.board[line][2].piece = Laufer(color)
            self.board[line][3].piece = Piece(ChessSymbols.KING, color)
            self.board[line][4].piece = Piece(ChessSymbols.QUEEN, color)
            self.board[line][5].piece = Laufer(color)
            self.board[line][6].piece = Piece(ChessSymbols.KNIGHT, color)
            self.board[line][7].piece = Piece(ChessSymbols.ROOK, color)
            color = False
    
    def printBoard(self):
        rows = []
        
        rows.append("     A  B  C  D  E  F  G  H ")
        rows.append("   ┌────────────────────────┐")  
        for i, row in enumerate(self.board, start=1):
            rows.append(" " + str(i) + " │" + "".join(map(str, row)) + "│")
        rows.append("   └────────────────────────┘")
        print "\n".join(rows)
          
        print ""
        
    def move(self, fromPosition, toPosition):
        fromTile = self.board[int(fromPosition[1]) - 1][self._col(fromPosition[0])]
        toTile = self.board[int(toPosition[1]) - 1][self._col(toPosition[0])]
        fromTile.movePieceTo(toTile)
        
    def _col(self, letter):
        return ord(letter) - ord("A")
        

def main():
    game = Game()
    game.printBoard()

    print "\x1b[31mplayer A\x1b[0m from B2 to B3:"
    game.move("B2", "B3")
    game.printBoard()
    
    print "\x1b[34mplayer B\x1b[0m from G7 to G6:"
    game.move("G7", "G6")
    game.printBoard()
    
    print "\x1b[31mplayer A\x1b[0m from C1 to A3:"
    game.move("C1", "A3")
    game.printBoard()

if __name__ == '__main__':
    main()

