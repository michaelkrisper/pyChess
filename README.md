# pyChess

Two-player chess for the terminal, written in plain Python with no dependencies.

[![CI](https://github.com/michaelkrisper/pyChess/actions/workflows/ci.yml/badge.svg)](https://github.com/michaelkrisper/pyChess/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

```
     A  B  C  D  E  F  G  H
   ┌────────────────────────┐
 8 │ ♜  ♞  ♝  ♛  ♚  ♝  ♞  ♜ │
 7 │ ♟  ♟  ♟  ♟  ♟  ♟  ♟  ♟ │
 6 │                        │
 5 │                        │
 4 │             ♟          │
 3 │                        │
 2 │ ♟  ♟  ♟  ♟     ♟  ♟  ♟ │
 1 │ ♜  ♞  ♝  ♛  ♚  ♝  ♞  ♜ │
   └────────────────────────┘

chess (Player 2)>
```

In the terminal the board is drawn with a checkered background; Player 1 (red)
plays from rank 1 and moves first, Player 2 (blue) plays from rank 8.

## Features

- Full piece movement rules, including castling, en passant and pawn promotion
- Check, checkmate and stalemate detection
- Draws by threefold repetition, the 50-move rule and insufficient material
- Save and load games
- Single file (`pyChess.py`), standard library only

## Usage

Requires Python 3.9 or newer and a terminal with Unicode and ANSI color support.

```bash
git clone https://github.com/michaelkrisper/pyChess.git
cd pyChess
python3 pyChess.py
```

### Commands

| Command | Description |
|---|---|
| `move FROM TO`, `mv FROM TO` | Move a piece, e.g. `mv e2 e4`; castle by moving the king two squares (`mv e1 g1`) |
| `setname NAME`, `sn NAME` | Set the name of the current player |
| `save FILE` | Save the game |
| `load FILE` | Load a saved game |
| `help`, `h` | Show the command list |
| `quit`, `q` | Quit (Ctrl-D works too) |

When a pawn reaches the last rank you are asked for the promotion piece
(`Q`, `R`, `B` or `N`).

Save files use Python's `pickle` format; only load files you created yourself.

## Development

```bash
pip install pytest ruff
pytest
ruff check .
```

## License

MIT - see [LICENSE](LICENSE).
