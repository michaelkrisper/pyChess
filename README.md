# pyChess

A python script which implements classic chess on the terminal.

![Screenshot of pyChess](Screenshot%202012-05-14.png)

## Description

pyChess is a command-line based chess game written in Python. It allows two players to play a game of chess in the terminal, using text-based commands to move pieces. The board is rendered with unicode characters for a classic feel.

## Features

The game implements the following standard chess rules and features:

*   Standard piece movement
*   Castling
*   En passant
*   Pawn promotion
*   Check and checkmate detection
*   Stalemate detection
*   Draw by threefold repetition
*   Draw by the 50-move rule
*   Draw by insufficient mating material
*   Save and load games

## Requirements

*   Python 3.x

## How to Run

To run the game, simply execute the following command in your terminal:

```bash
python3 pyChess.py
```

## How to Play

The game is controlled through a simple command-line interface. The following commands are available:

*   `move <FROM> <TO>` (or `mv <FROM> <TO>`): Moves a piece from one square to another. For example: `mv e2 e4`.
*   `setname <NAME>` (or `sn <NAME>`): Sets the name for the current player.
*   `save <FILENAME>`: Saves the current game state to a file.
*   `load <FILENAME>`: Loads a game state from a file.
*   `help` (or `h`): Displays a list of available commands.
*   `quit` (or `q`): Quits the game.

## Author

*   **Michael Krisper**
