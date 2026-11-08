# CLAUDE.md

Two-player chess for the terminal in a single file, `pyChess.py`. Python 3.9+,
standard library only (plus `readline` if available). No packaging, nothing to deploy.

## Commands

```bash
python3 pyChess.py               # play
pip install pytest ruff
pytest                           # test_pychess.py, 44 tests, < 1 s
ruff check .                     # config in pyproject.toml (E, F, W, I; 140 cols)
```

CI (`.github/workflows/ci.yml`) runs ruff on 3.14 and pytest on 3.9 and 3.14.

## Architecture

- `Game` owns `board[row][col]` of `Tile`s; row 0 is rank 1, col 0 is file A.
  `get_tile_by_name("e2")` maps squares. `Game.run()` is the REPL loop and checks
  threefold repetition, 50-move rule, insufficient material, mate and stalemate
  before each prompt.
- `Piece` subclasses implement `is_move_allowed(fromTile, toTile, simulate=False)`;
  `Piece.move()` applies the move, undoes it if it leaves the own king in check,
  then calls `post_move_action()` (castling rook, `_has_moved` flags).
- `Player.direction` is `+1` for Player 1 (rank 1, moves first) and `-1` for Player 2;
  pawn moves, en passant and promotion use it instead of colors.
- Commands are `Command` subclasses created by `CommandFactory` (`mv`, `sn`, `save`,
  `load`, `help`, `quit`). En passant and promotion are handled in `CommandMove`.
- `images/` and the screenshots are legacy assets; the game never loads them.

## Rules and pitfalls

- `simulate=True` must stay side-effect free: `has_legal_moves()` and
  `is_square_attacked()` call it for every square pair. No prints, no state changes;
  castling is only evaluated with `simulate=False`.
- `is_square_attacked()` special-cases pawns (diagonal attacks only) and kings
  (adjacency); never route those through `is_move_allowed`.
- `save`/`load` pickle the whole `Game` object. Renaming classes or attributes breaks
  old save files; never unpickle untrusted files.
- Tests drive the game through `CommandMove(game).execute(["e2", "e4"])` and check
  that the current player switched; keep that contract when changing move handling.
- Keep it one file and standard library only; mixed camelCase/snake_case is legacy,
  match the surrounding code instead of mass-renaming.

## Workflow

- Every change starts with a GitHub issue. Branch `<issue>-<slug>` from `main`,
  open a PR with `Closes #<issue>`. Never push to `main` directly.
- PRs auto-merge (squash) once CI and the "Linked ticket" check pass; drafts are not merged.
- Versions exist only as git tags `vX.Y.Z`. Every merge to `main` tags the next patch;
  never edit version numbers in files. Minor/major releases: Actions -> Release.
- Nothing is deployed; a merge to `main` only creates the patch tag.
- Details: CONTRIBUTING.md.
