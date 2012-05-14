#! /usr/local/bin python
# -*- coding: UTF-8 -*-

__author__ = "Michael Krisper"
__date__ = "2012-05-15"
__python__ = "2.7.3"

def singleton(cls):
    """Singleton Decorator"""
    return cls()

@singleton
class ChessSymbols(object):
    """Class for defining the chess symbols"""
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
    """Base Class for all Pieces"""
    def __init__(self, name, player):
        self.name = name
        self.player = player

    def __str__(self):
        return self.player.getColor() + self.name
    
    def isMoveAllowed(self, fromTile, toTile):
        raise NotImplementedError("Method not implemented: Piece.isMoveAllowed")
    
    def move(self, fromTile, toTile):
        if self.isMoveAllowed(fromTile, toTile):
            toTile.piece = self
            fromTile.piece = None
            return True
        else:
            print "Error: This move not allowed due to chess rules"
            return False

class King(Piece):
    def __init__(self, player):
        Piece.__init__(self, ChessSymbols.KING, player)

    def isMoveAllowed(self, fromTile, toTile):
        if (toTile in (fromTile.getTile(-1, -1), fromTile.getTile(-1, 0), fromTile.getTile(-1, 1),
                       fromTile.getTile(0, -1), fromTile.getTile(0, 1),
                       fromTile.getTile(1, -1), fromTile.getTile(1, 0), fromTile.getTile(1, 1))
            and ((toTile.piece == None) or (toTile.piece.player != self.player))):
            return True
        else:
            return False


class Knight(Piece):
    def __init__(self, player):
        Piece.__init__(self, ChessSymbols.KNIGHT, player)
    
    def isMoveAllowed(self, fromTile, toTile):
        if (toTile in (fromTile.getTile(x, y) for x, y in ((-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1)))
            and (toTile.piece == None or toTile.piece.player != fromTile.piece.player)):
            #jump 2 fields and 1 field to the side, strike enemy piece if needed 
            return True
        
        return False

class Pawn(Piece):
    def __init__(self, player):
        Piece.__init__(self, ChessSymbols.PAWN, player)

    def isMoveAllowed(self, fromTile, toTile):
        d = self.player.direction
        
        if toTile.piece == None and fromTile.getTile(0, d) == toTile:
            # straight forward move
            return True
        
        if (toTile.piece != None and toTile.piece.player != fromTile.piece.player
            and toTile in (fromTile.getTile(-1, d), fromTile.getTile(1, d))):
            # diagonal forward strike enemy piece
            return True
        
        return False

class Rook(Piece):
    def __init__(self, player):
        Piece.__init__(self, ChessSymbols.ROOK, player)
        
    def isMoveAllowed(self, fromTile, toTile):
        for x, y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, 8):
                if fromTile.getTile(i * x, i * y) == toTile and (toTile.piece == None or fromTile.piece.player != toTile.piece.player):
                    # go in diagonal direction, strike enemy piece if needed
                    return True
                else:
                    tile = fromTile.getTile(i * x, i * y)
                    if tile != None and tile.piece != None:
                    # if a piece blocks the way: not allowed
                        break
                
        return False

class Bishop(Piece):
    def __init__(self, player):
        Piece.__init__(self, ChessSymbols.BISHOP, player)
    
    def isMoveAllowed(self, fromTile, toTile):
        for x, y in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            for i in range(1, 8):
                if fromTile.getTile(i * x, i * y) == toTile and (toTile.piece == None or fromTile.piece.player != toTile.piece.player):
                    # go in diagonal direction, strike enemy piece if needed
                    return True
                else:
                    tile = fromTile.getTile(i * x, i * y)
                    if tile != None and tile.piece != None:
                    # if a piece blocks the way: not allowed
                        break

        return False

class Queen(Rook, Bishop):
    def __init__(self, player):
        Piece.__init__(self, ChessSymbols.QUEEN, player)
        
    def isMoveAllowed(self, fromTile, toTile):
        return Rook.isMoveAllowed(self, fromTile, toTile) or Bishop.isMoveAllowed(self, fromTile, toTile)

class Tile(object):
    def __init__(self, isBlack, board, col, row):
        self.isBlack = isBlack
        self.board = board
        self.col = col
        self.row = row
        self.piece = None
        
    def __str__(self):
        if self.isBlack:
            return "\x1b[47m %s \x1b[0m" % (self.piece if self.piece else " ")
        else:
            return " %s \x1b[0m" % (self.piece if self.piece else " ")
        
    def movePieceTo(self, toTile):
        return self.piece.move(self, toTile)
        
    def getTile(self, col, row):
        if (0 <= (self.row + row) < len(self.board)) and (0 <= (self.col + col) < len(self.board[0])):
            return self.board[self.row + row][self.col + col]
        else:
            return None

class Command(object):
    def __init__(self, game):
        self._game = game
            
    def execute(self, params):
        raise NotImplementedError

class CommandQuit(Command):
    names = ["quit", "q"]
    
    def execute(self, params):
        self._game.stop()

class CommandMove(Command):
    names = ["move", "mv", "m"]
    
    def execute(self, params):
        if len(params) != 2:
            print "Error: Wrong Usage (expected: move FROM TO)"
            return False
        
        fromPosition = params[0]
        toPosition = params[1]
        
        fromTile = self._game.board[int(fromPosition[1]) - 1][ord(fromPosition[0].lower()) - ord("a")]
        toTile = self._game.board[int(toPosition[1]) - 1][ord(toPosition[0].lower()) - ord("a")]
        
        if fromTile.piece == None:
            print "Error: No piece found to move."
            return False
        
        if fromTile.piece.player != self._game.currentPlayer():
            print "Error: Only own pieces can be moved."
            return False

        return fromTile.movePieceTo(toTile)

class CommandSetName(Command):
    names = ["setname"]
    
    def execute(self, params):
        if len(params) != 1:
            print "Error: Wrong Usage (expected: setname NAME)"
            return False
        
        self._game.currentPlayer().setName(params[0])
        return False

class CommandFactory:
    def __init__(self, controller):
        self._game = controller
    
    def getCommand(self, name):
        for cls in Command.__subclasses__():
            if name in cls.names:
                return cls(self._game)
        return None

class StartPositionBuilder(object):
    def __init__(self, game):
        self._game = game
        
    def setDefaultPosition(self):
        player1 = self._game.players[0]
        player2 = self._game.players[1]
        
        for cell in self._game.board[1]:
            cell.piece = Pawn(player1)
    
        for cell in self._game.board[-2]:
            cell.piece = Pawn(player2)
      
        player = player1
        for line in [0, -1]:
            self._game.board[line][0].piece = Rook(player)
            self._game.board[line][1].piece = Knight(player)
            self._game.board[line][2].piece = Bishop(player)
            self._game.board[line][3].piece = King(player)
            self._game.board[line][4].piece = Queen(player)
            self._game.board[line][5].piece = Bishop(player)
            self._game.board[line][6].piece = Knight(player)
            self._game.board[line][7].piece = Rook(player)
            player = player2

class Player(object):
    def __init__(self, name, color, direction):
        self._name = name
        self._color = color
        self.direction = direction

    def setName(self, name):
        self._name = name
        
    def __str__(self):
        return self._color + self._name + "\x1b[0m"
    
    def getColor(self):
        return self._color

class Game(object):
    def __init__(self):
        self.board = []
        self._init_board()
        self._currentPlayer = 0
        self.players = [Player("Player 1", "\x1b[31m", 1), Player("Player 2", "\x1b[34m", -1)] # TODO: farbkodierung anders implementieren!
        self._run = False
        self._factory = CommandFactory(self)
        StartPositionBuilder(self).setDefaultPosition()

    def _init_board(self):
        self.board.extend(([Tile(((row + col) % 2 == 0), self.board, col, row) for col in range(8)] for row in range(8)))
    
    def printBoard(self):
        rows = []
        
        rows.append("     A  B  C  D  E  F  G  H ")
        rows.append("   ┌────────────────────────┐")
        for i, row in enumerate(self.board, start=1):
            rows.append(" " + str(i) + " │" + "".join(map(str, row)) + "│")
        rows.append("   └────────────────────────┘")
        
        
        print "\n".join(rows)
        print ""
        
    def run(self):
        self._run = True
        #print '\x1b[H\x1b[2J' # delete whole console screen
        self.printBoard()
        while self._run:
            prompt = "(%s)> " % self.currentPlayer()
            input_text = raw_input(prompt)
            splitText = input_text.split()
            #print '\x1b[H\x1b[2J' # delete whole console screen
            if len(splitText)>0:
                cmd = self._factory.getCommand(splitText[0])
                if (cmd):
                    try:
                        if cmd.execute(splitText[1:]):
                            self.switchPlayer()
                    except Exception:
                        print "Error: Wrong Params or Wrong Values"
                else:
                    print "Error: Command not recognized."
            self.printBoard()
            #print prompt + input_text # reprint previous command

    def switchPlayer(self):
        self._currentPlayer = (self._currentPlayer + 1) % 2

    def currentPlayer(self):
        return self.players[self._currentPlayer]

    def stop(self):
        self._run = False

if __name__ == '__main__':
    game = Game()
    game.run()

