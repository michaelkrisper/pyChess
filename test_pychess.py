import builtins

import pytest

from pyChess import (
    Bishop,
    CommandHelp,
    CommandLoad,
    CommandMove,
    CommandSave,
    CommandSetName,
    Game,
    King,
    Knight,
    Pawn,
    Queen,
    Rook,
)


def play(game, *moves):
    """Plays moves like 'e2e4' and asserts that each one was accepted."""
    for move in moves:
        player = game.current_player()
        CommandMove(game).execute([move[:2], move[2:]])
        assert game.current_player() is not player, "move %s was rejected" % move


def rejected(game, move):
    player = game.current_player()
    CommandMove(game).execute([move[:2], move[2:]])
    return game.current_player() is player


def piece(game, square):
    return game.get_tile_by_name(square).piece


def empty_game():
    game = Game()
    for row in game.board:
        for tile in row:
            tile.piece = None
    return game


def place(game, square, cls, player_index):
    game.get_tile_by_name(square).piece = cls(game.players[player_index])


def test_start_position():
    game = Game()
    white, black = game.players
    expected = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
    for col, cls in enumerate(expected):
        assert type(game.board[0][col].piece) is cls
        assert game.board[0][col].piece.player is white
        assert type(game.board[7][col].piece) is cls
        assert game.board[7][col].piece.player is black
        assert isinstance(game.board[1][col].piece, Pawn)
        assert isinstance(game.board[6][col].piece, Pawn)


@pytest.mark.parametrize("name, row, col", [("a1", 0, 0), ("h8", 7, 7), ("E4", 3, 4)])
def test_get_tile_by_name(name, row, col):
    tile = Game().get_tile_by_name(name)
    assert (tile.row, tile.col) == (row, col)


@pytest.mark.parametrize("name", ["a0", "a9", "i1", "z9", "e", "e44", ""])
def test_get_tile_by_name_invalid(name):
    assert Game().get_tile_by_name(name) is None


def test_invalid_square_is_rejected_without_wrapping(capsys):
    game = Game()
    assert rejected(game, "a0a3")
    assert "a1 ... h8" in capsys.readouterr().out


def test_pawn_single_and_double_step():
    game = Game()
    play(game, "e2e4", "d7d6")
    assert isinstance(piece(game, "e4"), Pawn)
    assert isinstance(piece(game, "d6"), Pawn)
    assert rejected(game, "e4e6")


def test_pawn_cannot_jump_over_piece():
    game = Game()
    play(game, "g1f3", "e7e5")
    assert rejected(game, "f2f4")


def test_pawn_cannot_capture_straight_ahead():
    game = Game()
    play(game, "e2e4", "e7e5")
    assert rejected(game, "e4e5")


def test_cannot_move_opponent_piece():
    assert rejected(Game(), "e7e5")


def test_knight_moves_and_blocked_rook():
    game = Game()
    play(game, "b1c3")
    assert isinstance(piece(game, "c3"), Knight)
    game.switch_player()
    assert rejected(game, "a1a3")


def test_en_passant():
    game = Game()
    play(game, "e2e4", "a7a6", "e4e5", "d7d5", "e5d6")
    assert isinstance(piece(game, "d6"), Pawn)
    assert piece(game, "d5") is None


def test_en_passant_only_immediately():
    game = Game()
    play(game, "e2e4", "a7a6", "e4e5", "d7d5", "h2h3", "a6a5")
    assert rejected(game, "e5d6")


def test_failed_move_keeps_en_passant_right():
    game = Game()
    play(game, "e2e4", "a7a6", "e4e5", "d7d5")
    assert rejected(game, "e5e7")
    play(game, "e5d6")
    assert piece(game, "d5") is None


def test_kingside_castling():
    game = Game()
    play(game, "e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6", "e1g1")
    assert isinstance(piece(game, "g1"), King)
    assert isinstance(piece(game, "f1"), Rook)
    assert piece(game, "h1") is None


def test_queenside_castling():
    game = Game()
    play(game, "d2d4", "d7d5", "b1c3", "b8c6", "c1f4", "c8f5", "d1d2", "d8d7", "e1c1")
    assert isinstance(piece(game, "c1"), King)
    assert isinstance(piece(game, "d1"), Rook)
    assert piece(game, "a1") is None


def test_no_castling_through_attacked_square():
    game = empty_game()
    place(game, "e1", King, 0)
    place(game, "h1", Rook, 0)
    place(game, "a8", King, 1)
    place(game, "f8", Rook, 1)
    assert rejected(game, "e1g1")


def test_no_castling_with_queen_in_corner():
    game = empty_game()
    place(game, "e1", King, 0)
    place(game, "h1", Queen, 0)
    place(game, "a8", King, 1)
    assert rejected(game, "e1g1")


def test_pawn_attack_blocks_castling_only_diagonally():
    game = empty_game()
    place(game, "e1", King, 0)
    place(game, "h1", Rook, 0)
    place(game, "a8", King, 1)
    place(game, "f3", Pawn, 1)  # attacks e2 and g2, not f1/g1
    play(game, "e1g1")
    assert isinstance(piece(game, "g1"), King)


def test_cannot_leave_king_in_check():
    game = empty_game()
    place(game, "e1", King, 0)
    place(game, "e2", Bishop, 0)
    place(game, "e8", Rook, 1)
    place(game, "a8", King, 1)
    assert rejected(game, "e2d3")


def test_kings_cannot_be_adjacent():
    game = empty_game()
    place(game, "e1", King, 0)
    place(game, "e3", King, 1)
    assert rejected(game, "e1e2")
    play(game, "e1d1")


def test_fools_mate_is_checkmate():
    game = Game()
    play(game, "f2f3", "e7e5", "g2g4", "d8h4")
    white = game.current_player()
    assert game.is_king_in_check(white)
    assert not game.has_legal_moves(white)


def test_stalemate():
    game = empty_game()
    place(game, "a8", King, 1)
    place(game, "c7", Queen, 0)
    place(game, "e1", King, 0)
    game.switch_player()
    black = game.current_player()
    assert not game.is_king_in_check(black)
    assert not game.has_legal_moves(black)


def test_pawn_promotion(monkeypatch):
    game = empty_game()
    place(game, "e1", King, 0)
    place(game, "a8", King, 1)
    place(game, "g7", Pawn, 0)
    monkeypatch.setattr(builtins, "input", lambda prompt="": "n")
    play(game, "g7g8")
    assert isinstance(piece(game, "g8"), Knight)


def test_halfmove_clock():
    game = Game()
    play(game, "g1f3", "g8f6")
    assert game._halfmove_clock == 2
    play(game, "e2e4")
    assert game._halfmove_clock == 0


@pytest.mark.parametrize(
    "pieces, sufficient",
    [
        ([], False),
        ([Knight], False),
        ([Bishop], False),
        ([Knight, Bishop], True),
        ([Pawn], True),
        ([Rook], True),
        ([Queen], True),
    ],
)
def test_sufficient_material(pieces, sufficient):
    game = empty_game()
    place(game, "e1", King, 0)
    place(game, "e8", King, 1)
    for square, cls in zip(["a3", "b3"], pieces):
        place(game, square, cls, 0)
    assert game._has_sufficient_material() is sufficient


def _run(game, monkeypatch, commands):
    inputs = iter(commands)
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(inputs))
    game.run()


def test_threefold_repetition(monkeypatch, capsys):
    game = Game()
    moves = ["mv g1 f3", "mv g8 f6", "mv f3 g1", "mv f6 g8"] * 2
    _run(game, monkeypatch, moves)
    assert "threefold repetition" in capsys.readouterr().out


def test_invalid_commands_do_not_count_as_repetition(monkeypatch, capsys):
    game = Game()
    _run(game, monkeypatch, ["foo", "foo", "foo", "q"])
    out = capsys.readouterr().out
    assert "threefold repetition" not in out
    assert out.count("Command not recognized") == 3


def test_eof_ends_game(monkeypatch):
    game = Game()

    def eof(prompt=""):
        raise EOFError

    monkeypatch.setattr(builtins, "input", eof)
    game.run()
    assert not game._run


def test_setname_without_argument(capsys):
    game = Game()
    CommandSetName(game).execute([])
    assert "Wrong Usage" in capsys.readouterr().out
    CommandSetName(game).execute(["Kasparov"])
    assert "Kasparov" in str(game.current_player())


def test_help_lists_commands_on_separate_lines(capsys):
    CommandHelp(Game()).execute([])
    lines = capsys.readouterr().out.splitlines()
    assert any(line.strip().startswith("move, mv") for line in lines)
    assert any(line.strip().startswith("quit, q") for line in lines)


def test_save_and_load_roundtrip(tmp_path):
    game = Game()
    play(game, "e2e4", "d7d5")
    path = str(tmp_path / "game.sav")
    CommandSave(game).execute([path])

    other = Game()
    CommandLoad(other).execute([path])
    assert isinstance(piece(other, "e4"), Pawn)
    assert piece(other, "e2") is None
    assert other.current_player() is other.players[0]
    # Tiles must refer to the game they were loaded into.
    assert all(tile.game is other for row in other.board for tile in row)
    play(other, "e4d5")
    assert piece(other, "d5").player is other.players[0]
