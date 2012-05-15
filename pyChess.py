#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import readline

# backward compatibility for python 2 and python 3
try:
    input = raw_input
except NameError:
    pass



# TODO:
# * win/loose/draw/patt logic
# * additional rules
#   * distance of 2 kings at least 1 field
#   * strike en pasante
#   * rochade
#   * piece-change for pawn
#   * king must not move into chess
#
# Suggestions:
# * fast chess start position
# * command history
# * Better Color Coding for players
# * load and save game status
# * chess warning for king
# * network mode
# * AI player
# * make "move" command the default (pre-fill the stdin, or simply when no other command applies, take move cmd)

__author__ = "Michael Krisper"
__date__ = "2012-05-15"
__python__ = "2.7.3"
        
class Piece(object):
    """Base Class for all Pieces"""
    def __init__(self, name, player):
        self.name = name
        self.player = player

    def __str__(self):
        return self.player.get_color() + self.name
    
    def is_move_allowed(self, fromTile, toTile):
        raise NotImplementedError("Method not implemented: Piece.is_move_allowed")
    
    def move(self, fromTile, toTile):
        if self.is_move_allowed(fromTile, toTile):
            toTile.piece = self
            fromTile.piece = None
            return True
        else:
            print("Error: This move not allowed due to chess rules")
            return False

class Knight(Piece):
    def __init__(self, player, use_symbols=True):
        Piece.__init__(self, "♞" if use_symbols else "N", player)
    
    def is_move_allowed(self, fromTile, toTile):
        if (toTile in (fromTile.get_tile(x, y) for x, y in ((-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1)))
            and (toTile.piece == None or toTile.piece.player != fromTile.piece.player)):
            #jump 2 fields and 1 field to the side, strike enemy piece if needed 
            return True
        return False

class Pawn(Piece):
    def __init__(self, player, use_symbols=True):
        Piece.__init__(self, "♟" if use_symbols else "P", player)
        self._firstmove = True

    def is_move_allowed(self, fromTile, toTile):
        d = self.player.direction
        
        if toTile.piece == None and (fromTile.get_tile(0, d) == toTile or (self._firstmove and fromTile.get_tile(0, 2 * d) == toTile)):
            # straight forward move
            self._firstmove = False
            return True
        
        if (toTile.piece != None and toTile.piece.player != fromTile.piece.player
            and toTile in (fromTile.get_tile(-1, d), fromTile.get_tile(1, d))):
            # diagonal forward strike enemy piece
            self._firstmove = False
            return True
        return False

class Rook(Piece):
    def __init__(self, player, use_symbols=True):
        Piece.__init__(self, "♜" if use_symbols else "R", player)
        
    def is_move_allowed(self, fromTile, toTile):
        for x, y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, 8):
                if fromTile.get_tile(i * x, i * y) == toTile and (toTile.piece == None or fromTile.piece.player != toTile.piece.player):
                    # go in diagonal direction, strike enemy piece if needed
                    return True
                else:
                    tile = fromTile.get_tile(i * x, i * y)
                    if tile != None and tile.piece != None:
                    # if a piece blocks the way: not allowed
                        break
                
        return False

class Bishop(Piece):
    def __init__(self, player, use_symbols=True):
        Piece.__init__(self, "♝" if use_symbols else "B", player)
    
    def is_move_allowed(self, fromTile, toTile):
        for x, y in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            for i in range(1, 8):
                if fromTile.get_tile(i * x, i * y) == toTile and (toTile.piece == None or fromTile.piece.player != toTile.piece.player):
                    # go in diagonal direction, strike enemy piece if needed
                    return True
                else:
                    tile = fromTile.get_tile(i * x, i * y)
                    if tile != None and tile.piece != None:
                    # if a piece blocks the way: not allowed
                        break

        return False

class Queen(Rook, Bishop):
    def __init__(self, player, use_symbols=True):
        Piece.__init__(self, "♛" if use_symbols else "Q", player)
        
    def is_move_allowed(self, fromTile, toTile):
        return Rook.is_move_allowed(self, fromTile, toTile) or Bishop.is_move_allowed(self, fromTile, toTile)

class King(Piece):
    def __init__(self, player, useSymbols=True):
        Piece.__init__(self, "♚" if useSymbols else "K", player)

    def is_move_allowed(self, fromTile, toTile):
        if (toTile in (fromTile.get_tile(-1, -1), fromTile.get_tile(-1, 0), fromTile.get_tile(-1, 1),
                       fromTile.get_tile(0, -1), fromTile.get_tile(0, 1),
                       fromTile.get_tile(1, -1), fromTile.get_tile(1, 0), fromTile.get_tile(1, 1))
            and ((toTile.piece == None) or (toTile.piece.player != self.player))):
            return True
        else:
            return False

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
    names = ["move", "mv"]
    
    def execute(self, params):
        if len(params) != 2:
            print("Error: Wrong Usage (expected: move FROM TO)")
        
        fromPosition = params[0]
        toPosition = params[1]
        
        fromTile = self._game.board[int(fromPosition[1]) - 1][ord(fromPosition[0].lower()) - ord("a")]
        toTile = self._game.board[int(toPosition[1]) - 1][ord(toPosition[0].lower()) - ord("a")]
        
        if fromTile.piece == None:
            print("Error: No piece found to move.")
        
        if fromTile.piece.player != self._game.current_player():
            print("Error: Only own pieces can be moved.")

        if fromTile.move_piece_to(toTile):
            self._game.switch_player()

class CommandSetName(Command):
    names = ["setname", "sn"]
    
    def execute(self, params):
        if len(params) != 1:
            print("Error: Wrong Usage (expected: setname NAME)")
        
        self._game.current_player().set_name(params[0])
    
class CommandHelp(Command):
    names = ["help", "h"]
    
    def execute(self, params):
        print("Following commands are available:"
              "  move, mv FROM TO   Moves a Piece (example: mv b2 b3)"
              "  setname, sn NAME   Set the current player name (example: setname Kasparov)"
              "  help, h            Display this help (example: h)"
              "  quit, q            Quits the Game (example: q)\n")

class CommandFactory:
    def __init__(self, controller):
        self._game = controller
    
    def get_command(self, name):
        for cls in Command.__subclasses__():
            if name in cls.names:
                return cls(self._game)
        return None

class StartPositionBuilder(object):
    def __init__(self, game):
        self._game = game
        
    def set_default_position(self):
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
        
    def move_piece_to(self, toTile):
        return self.piece.move(self, toTile)
        
    def get_tile(self, col, row):
        if (0 <= (self.row + row) < len(self.board)) and (0 <= (self.col + col) < len(self.board[0])):
            return self.board[self.row + row][self.col + col]
        else:
            return None

class Player(object):
    def __init__(self, name, color, direction):
        self._name = name
        self._color = color
        self.direction = direction

    def set_name(self, name):
        self._name = name
        
    def __str__(self):
        return self._color + self._name + "\x1b[0m"
    
    def get_color(self):
        return self._color

class Game(object):
    def __init__(self):
        self.board = []
        self._init_board()
        self._currentPlayer = 0
        self.players = [Player("Player 1", "\x1b[31m", 1), Player("Player 2", "\x1b[34m", -1)] # TODO: farbkodierung anders implementieren!
        self._run = False
        self._factory = CommandFactory(self)
        StartPositionBuilder(self).set_default_position()

    def _init_board(self):
        self.board.extend(([Tile(((row + col) % 2 == 0), self.board, col, row) for col in range(8)] for row in range(8)))
    
    def print_board(self):
        rows = []
        
        rows.append("     A  B  C  D  E  F  G  H ")
        rows.append("   ┌────────────────────────┐")
        for i, row in enumerate(self.board, start=1):
            rows.append(" " + str(i) + " │" + "".join(map(str, row)) + "│")
        rows.append("   └────────────────────────┘")
        
        
        print("\n".join(rows) + "\n")
        
    def run(self):
        self._run = True
        #print '\x1b[H\x1b[2J' # delete whole console screen
        while self._run:
            self.print_board()
            splitText = input("chess (%s)> " % self.current_player()).split()
            #print '\x1b[H\x1b[2J' # delete whole console screen
            if len(splitText) > 0:
                cmd = self._factory.get_command(splitText[0])
                if (cmd):
                    try:
                        cmd.execute(splitText[1:])
                    except Exception as err:
                        print(err.message)
                else:
                    print("Error: Command not recognized.")
            
    def switch_player(self):
        self._currentPlayer = (self._currentPlayer + 1) % 2

    def current_player(self):
        return self.players[self._currentPlayer]

    def stop(self):
        self._run = False

if __name__ == '__main__':
    game = Game()
    game.run()
