#!/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    import readline
except ImportError:
    pass

class Color:
    """A simple class for handling ANSI color codes."""
    RED = '\x1b[31m'
    BLUE = '\x1b[34m'
    BG_WHITE = '\x1b[47m'
    END = '\x1b[0m'
    ENABLED = True

    @staticmethod
    def colorize(text, color_code):
        if not Color.ENABLED or not color_code:
            return text
        return color_code + text + Color.END

__author__ = "Michael Krisper"
__date__ = "2012-05-15"
__python__ = "3.x" # Updated to Python 3

class Piece(object):
    """Base class for all chess pieces."""
    def __init__(self, name, player):
        """
        Initializes a Piece.

        Args:
            name (str): The name of the piece (e.g., 'K' for King).
            player (Player): The player who owns the piece.
        """
        self.name = name
        self.player = player

    def __str__(self):
        """Returns the string representation of the piece, with color."""
        return Color.colorize(self.name, self.player.get_color())
    
    def is_move_allowed(self, fromTile, toTile, simulate=False):
        """
        Checks if a move is allowed for this piece.

        This method must be implemented by subclasses.

        Args:
            fromTile (Tile): The starting tile of the move.
            toTile (Tile): The destination tile of the move.
            simulate (bool): If True, the move is a simulation and should not
                             trigger certain actions (like printing errors).

        Returns:
            bool: True if the move is allowed, False otherwise.
        """
        raise NotImplementedError("Method not implemented: Piece.is_move_allowed")
    
    def move(self, fromTile, toTile, game):
        """
        Executes a move from one tile to another.

        This method checks if the move is allowed, performs the move,
        and ensures the king is not left in check.

        Args:
            fromTile (Tile): The starting tile.
            toTile (Tile): The destination tile.
            game (Game): The current game instance.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if self.is_move_allowed(fromTile, toTile):
            original_piece = toTile.piece
            toTile.piece = self
            fromTile.piece = None
            if game.is_king_in_check(self.player):
                fromTile.piece = self
                toTile.piece = original_piece
                print("Error: This move is not allowed as it would put your king in check.")
                return False
            self.post_move_action(fromTile, toTile)
            return True
        else:
            print("Error: This move not allowed due to chess rules")
            return False

    def post_move_action(self, fromTile, toTile):
        """
        Performs any actions required after a move is completed.

        This can be overridden by subclasses for special moves like castling
        or pawn promotion.
        """
        pass

class Knight(Piece):
    """Represents a Knight piece."""
    def __init__(self, player, use_symbols=True):
        """Initializes a Knight."""
        super().__init__("♞" if use_symbols else "N", player)
    
    def is_move_allowed(self, fromTile, toTile, simulate=False):
        """Checks if the Knight's L-shaped move is valid."""
        if (toTile in (fromTile.get_tile(x, y) for x, y in ((-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1)))
            and (toTile.piece == None or toTile.piece.player != fromTile.piece.player)):
            return True
        return False

class Pawn(Piece):
    """Represents a Pawn piece."""
    def __init__(self, player, use_symbols=True):
        """Initializes a Pawn."""
        super().__init__("♟" if use_symbols else "P", player)
        self._firstmove = True

    def is_move_allowed(self, fromTile, toTile, simulate=False):
        """Checks if the Pawn's move is valid, including initial double move, captures, and en passant."""
        d = self.player.direction
        if toTile.piece == None and fromTile.get_tile(0, d) == toTile:
            return True
        if self._firstmove and toTile.piece == None and fromTile.get_tile(0, 2 * d) == toTile:
            return True
        if (toTile.piece != None and toTile.piece.player != fromTile.piece.player
            and toTile in (fromTile.get_tile(-1, d), fromTile.get_tile(1, d))):
            return True
        if toTile == fromTile.game._en_passant_target_tile and toTile.piece is None \
           and toTile in (fromTile.get_tile(-1, d), fromTile.get_tile(1, d)):
            return True
        return False

    def post_move_action(self, fromTile, toTile):
        """Handles post-move logic for a Pawn, including setting first move flag and en passant captures."""
        self._firstmove = False
        game = fromTile.game
        if toTile == game._en_passant_target_tile:
            captured_pawn_tile = game.board[toTile.row - self.player.direction][toTile.col]
            captured_pawn_tile.piece = None

class Rook(Piece):
    """Represents a Rook piece."""
    def __init__(self, player, use_symbols=True):
        """Initializes a Rook."""
        super().__init__("♜" if use_symbols else "R", player)
        self._has_moved = False
        
    def is_move_allowed(self, fromTile, toTile, simulate=False):
        """Checks if the Rook's straight-line move is valid."""
        for x, y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, 8):
                if fromTile.get_tile(i * x, i * y) == toTile and (toTile.piece == None or fromTile.piece.player != toTile.piece.player):
                    return True
                else:
                    tile = fromTile.get_tile(i * x, i * y)
                    if tile != None and tile.piece != None:
                        break
        return False

    def post_move_action(self, fromTile, toTile):
        """Sets the _has_moved flag to True after the Rook moves."""
        self._has_moved = True

class Bishop(Piece):
    """Represents a Bishop piece."""
    def __init__(self, player, use_symbols=True):
        """Initializes a Bishop."""
        super().__init__("♝" if use_symbols else "B", player)
    
    def is_move_allowed(self, fromTile, toTile, simulate=False):
        """Checks if the Bishop's diagonal move is valid."""
        for x, y in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            for i in range(1, 8):
                if fromTile.get_tile(i * x, i * y) == toTile and (toTile.piece == None or fromTile.piece.player != toTile.piece.player):
                    return True
                else:
                    tile = fromTile.get_tile(i * x, i * y)
                    if tile != None and tile.piece != None:
                        break
        return False

class Queen(Rook, Bishop):
    """Represents a Queen piece."""
    def __init__(self, player, use_symbols=True):
        """Initializes a Queen."""
        Piece.__init__(self, "♛" if use_symbols else "Q", player)
        
    def is_move_allowed(self, fromTile, toTile, simulate=False):
        """Checks if the Queen's move (Rook or Bishop move) is valid."""
        return Rook.is_move_allowed(self, fromTile, toTile, simulate) or Bishop.is_move_allowed(self, fromTile, toTile, simulate)

class King(Piece):
    """Represents a King piece."""
    def __init__(self, player, useSymbols=True):
        """Initializes a King."""
        super().__init__("♚" if useSymbols else "K", player)
        self._has_moved = False

    def is_move_allowed(self, fromTile, toTile, simulate=False):
        # Basic king move
        is_basic_move = (toTile in (fromTile.get_tile(-1, -1), fromTile.get_tile(-1, 0), fromTile.get_tile(-1, 1),
                           fromTile.get_tile(0, -1), fromTile.get_tile(0, 1),
                           fromTile.get_tile(1, -1), fromTile.get_tile(1, 0), fromTile.get_tile(1, 1))
                and ((toTile.piece == None) or (toTile.piece.player != self.player)))

        # Castling
        is_castling = False
        if not simulate and not self._has_moved and fromTile.row == toTile.row and abs(fromTile.col - toTile.col) == 2:
            game = fromTile.game
            if not game.is_king_in_check(self.player):
                # Kingside
                if toTile.col > fromTile.col:
                    rook_tile = fromTile.get_tile(3, 0)
                    path_clear = fromTile.get_tile(1, 0).piece is None and fromTile.get_tile(2, 0).piece is None
                    square_to_pass = fromTile.get_tile(1, 0)
                # Queenside
                else:
                    rook_tile = fromTile.get_tile(-4, 0)
                    path_clear = fromTile.get_tile(-1, 0).piece is None and fromTile.get_tile(-2, 0).piece is None and fromTile.get_tile(-3, 0).piece is None
                    square_to_pass = fromTile.get_tile(-1, 0)

                if path_clear and rook_tile and isinstance(rook_tile.piece, Rook) and not rook_tile.piece._has_moved:
                    if not game.is_square_attacked(square_to_pass, game.get_opponent(self.player)) and \
                       not game.is_square_attacked(toTile, game.get_opponent(self.player)):
                        is_castling = True

        if not is_basic_move and not is_castling:
            return False

        # Check for distance to other king
        game = fromTile.game
        opponent = game.get_opponent(self.player)
        opponent_king_tile = game.get_king_tile(opponent)

        if opponent_king_tile:
            if abs(toTile.col - opponent_king_tile.row) <= 1 and abs(toTile.row - opponent_king_tile.row) <= 1:
                print("Error: Kings cannot be adjacent.")
                return False

        return True


    def post_move_action(self, fromTile, toTile):
        self._has_moved = True
        if abs(fromTile.col - toTile.col) == 2:
            if toTile.col > fromTile.col:
                rook_from = toTile.get_tile(1, 0)
                rook_to = toTile.get_tile(-1, 0)
            else:
                rook_from = toTile.get_tile(-2, 0)
                rook_to = toTile.get_tile(1, 0)
            rook_to.piece = rook_from.piece
            rook_from.piece = None
            rook_to.piece._has_moved = True

class Command(object):
    """Base class for all game commands."""
    def __init__(self, game):
        """Initializes a command."""
        self._game = game
            
    def execute(self, params):
        """
        Executes the command.

        This method must be implemented by subclasses.

        Args:
            params (list): A list of parameters for the command.
        """
        raise NotImplementedError

class CommandQuit(Command):
    """Command to quit the game."""
    names = ["quit", "q"]
    
    def execute(self, params):
        """Stops the game loop."""
        self._game.stop()

class CommandMove(Command):
    """Command to move a piece."""
    names = ["move", "mv"]
    
    def execute(self, params):
        """
        Executes the move command.

        Parses the 'from' and 'to' positions, validates the move,
        and updates the game state.
        """
        if len(params) != 2:
            print("Error: Wrong Usage (expected: move FROM TO)")
            return
        
        fromPosition = params[0]
        toPosition = params[1]
        
        fromTile = self._game.board[int(fromPosition[1]) - 1][ord(fromPosition[0].lower()) - ord("a")]
        toTile = self._game.board[int(toPosition[1]) - 1][ord(toPosition[0].lower()) - ord("a")]
        
        self._game._en_passant_target_tile = None

        if fromTile.piece == None:
            print("Error: No piece found to move.")
            return
        
        if fromTile.piece.player != self._game.current_player():
            print("Error: Only own pieces can be moved.")
            return

        is_pawn_move = isinstance(fromTile.piece, Pawn)
        is_capture = toTile.piece is not None

        if fromTile.move_piece_to(toTile, self._game):
            if is_pawn_move or is_capture:
                self._game._halfmove_clock = 0
            else:
                self._game._halfmove_clock += 1
            piece = toTile.piece
            if isinstance(piece, Pawn):
                if abs(fromTile.row - toTile.row) == 2:
                    self._game._en_passant_target_tile = fromTile.get_tile(0, piece.player.direction)
                if (piece.player.direction == 1 and toTile.row == 7) or \
                   (piece.player.direction == -1 and toTile.row == 0):
                    self._game.promote_pawn(toTile)
            opponent = self._game.get_opponent(piece.player)
            if self._game.is_king_in_check(opponent):
                print("Check!")
            self._game.switch_player()

class CommandSetName(Command):
    """Command to set the current player's name."""
    names = ["setname", "sn"]
    
    def execute(self, params):
        """Sets the name for the current player."""
        if len(params) != 1:
            print("Error: Wrong Usage (expected: setname NAME)")
        
        self._game.current_player().set_name(params[0])
    
import pickle

class CommandSave(Command):
    """Command to save the game to a file."""
    names = ["save"]

    def execute(self, params):
        """Saves the current game state to a file using pickle."""
        if len(params) != 1:
            print("Error: Wrong Usage (expected: save FILENAME)")
            return
        filename = params[0]
        try:
            with open(filename, 'wb') as f:
                pickle.dump(self._game, f)
            print("Game saved to %s" % filename)
        except Exception as e:
            print("Error saving game: %s" % e)

class CommandLoad(Command):
    """Command to load a game from a file."""
    names = ["load"]

    def execute(self, params):
        """Loads a game state from a file using pickle."""
        if len(params) != 1:
            print("Error: Wrong Usage (expected: load FILENAME)")
            return
        filename = params[0]
        try:
            with open(filename, 'rb') as f:
                loaded_game = pickle.load(f)
            self._game.board = loaded_game.board
            self._game.players = loaded_game.players
            self._game._currentPlayer = loaded_game._currentPlayer
            self._game._en_passant_target_tile = loaded_game._en_passant_target_tile
            print("Game loaded from %s" % filename)
        except Exception as e:
            print("Error loading game: %s" % e)

class CommandHelp(Command):
    """Command to display help information."""
    names = ["help", "h"]
    
    def execute(self, params):
        """Prints a list of available commands and their usage."""
        print("Following commands are available:"
              "  move, mv FROM TO   Moves a Piece (example: mv b2 b3)"
              "  setname, sn NAME   Set the current player name (example: setname Kasparov)"
              "  save FILENAME      Save the current game to a file (example: save mygame.sav)"
              "  load FILENAME      Load a game from a file (example: load mygame.sav)"
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
    def __init__(self, isBlack, board, col, row, game):
        self.isBlack = isBlack
        self.board = board
        self.col = col
        self.row = row
        self.piece = None
        self.game = game
        
    def __str__(self):
        piece_str = " %s " % self.piece if self.piece else "   "
        if self.isBlack:
            return Color.BG_WHITE + piece_str + Color.END
        else:
            return piece_str
        
    def move_piece_to(self, toTile, game):
        return self.piece.move(self, toTile, game)
        
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
        return Color.colorize(self._name, self._color)
    
    def get_color(self):
        return self._color

class Game(object):
    def __init__(self):
        self.board = []
        self._init_board()
        self._currentPlayer = 0
        self.players = [Player("Player 1", Color.RED, 1), Player("Player 2", Color.BLUE, -1)]
        self._run = False
        self._factory = CommandFactory(self)
        self._en_passant_target_tile = None
        self._halfmove_clock = 0
        self._position_history = {}
        StartPositionBuilder(self).set_default_position()

    def _init_board(self):
        self.board.extend(([Tile(((row + col) % 2 == 0), self.board, col, row, self) for col in range(8)] for row in range(8)))
    
    def print_board(self):
        rows = []
        
        rows.append("     A  B  C  D  E  F  G  H ")
        rows.append("   ┌────────────────────────┐")
        for i, row in enumerate(self.board, start=1):
            rows.append(" " + str(i) + " │" + "".join(map(str, row)) + "│")
        rows.append("   └────────────────────────┘")
        
        
        print("\n".join(rows) + "\n")
        
    def _get_position_hash(self):
        board_tuple = tuple(
            (tile.piece.name, tile.piece.player) if tile.piece else None
            for row in self.board for tile in row
        )
        en_passant_pos = (self._en_passant_target_tile.row, self._en_passant_target_tile.col) if self._en_passant_target_tile else None
        return (board_tuple, self._currentPlayer, en_passant_pos)

    def _has_sufficient_material(self):
        pieces = [tile.piece for row in self.board for tile in row if tile.piece]
        for p in pieces:
            if isinstance(p, (Pawn, Rook, Queen)):
                return True
        knights = [p for p in pieces if isinstance(p, Knight)]
        bishops = [p for p in pieces if isinstance(p, Bishop)]
        if len(knights) + len(bishops) > 1:
            return True
        return False

    def run(self):
        self._run = True
        while self._run:
            self.print_board()
            current_hash = self._get_position_hash()
            self._position_history[current_hash] = self._position_history.get(current_hash, 0) + 1
            if self._position_history[current_hash] >= 3:
                print("Draw by threefold repetition.")
                self.stop()
                continue
            if self._halfmove_clock >= 100:
                print("Draw by 50-move rule.")
                self.stop()
                continue
            if not self._has_sufficient_material():
                print("Draw by insufficient mating material.")
                self.stop()
                continue
            if not self.has_legal_moves(self.current_player()):
                if self.is_king_in_check(self.current_player()):
                    print("Checkmate! %s wins." % self.get_opponent(self.current_player()))
                else:
                    print("Stalemate! The game is a draw.")
                self.stop()
                continue
            splitText = input("chess (%s)> " % self.current_player()).split()
            if len(splitText) > 0:
                cmd = self._factory.get_command(splitText[0])
                if (cmd):
                    try:
                        cmd.execute(splitText[1:])
                    except Exception as err:
                        print(str(err))
                else:
                    print("Error: Command not recognized.")
            
    def switch_player(self):
        self._currentPlayer = (self._currentPlayer + 1) % 2

    def current_player(self):
        return self.players[self._currentPlayer]

    def promote_pawn(self, tile):
        player = tile.piece.player
        self.print_board()
        print("Player %s can promote a pawn!" % player)
        choice = ""
        while choice.upper() not in ['Q', 'R', 'B', 'N']:
            choice = input("Choose piece for promotion (Q=Queen, R=Rook, B=Bishop, N=Knight): ")
        use_symbols = True
        if choice.upper() == 'Q':
            new_piece = Queen(player, use_symbols)
        elif choice.upper() == 'R':
            new_piece = Rook(player, use_symbols)
        elif choice.upper() == 'B':
            new_piece = Bishop(player, use_symbols)
        else:
            new_piece = Knight(player, use_symbols)
        tile.piece = new_piece

    def has_legal_moves(self, player):
        for row in self.board:
            for fromTile in row:
                if fromTile.piece and fromTile.piece.player == player:
                    for r in self.board:
                        for toTile in r:
                            if fromTile.piece.is_move_allowed(fromTile, toTile, simulate=True):
                                original_piece = toTile.piece
                                toTile.piece = fromTile.piece
                                fromTile.piece = None
                                is_legal = not self.is_king_in_check(player)
                                fromTile.piece = toTile.piece
                                toTile.piece = original_piece
                                if is_legal:
                                    return True
        return False

    def stop(self):
        self._run = False

    def get_king_tile(self, player):
        for row in self.board:
            for tile in row:
                if isinstance(tile.piece, King) and tile.piece.player == player:
                    return tile
        return None

    def get_opponent(self, player):
        return self.players[(self.players.index(player) + 1) % 2]

    def is_king_in_check(self, player):
        king_tile = self.get_king_tile(player)
        if not king_tile:
            return False
        return self.is_square_attacked(king_tile, self.get_opponent(player))

    def is_square_attacked(self, square, by_player):
        for row in self.board:
            for tile in row:
                if tile.piece and tile.piece.player == by_player:
                    if tile.piece.is_move_allowed(tile, square, simulate=True):
                        return True
        return False

if __name__ == '__main__':
    game = Game()
    game.run()
