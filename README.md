# Huyễn Ảnh Mê Tung (Sliding Puzzle Game)

## Overview

"Huyễn Ảnh Mê Tung" is an engaging sliding puzzle game implemented in Python using the Pygame library. The game offers traditional sliding puzzle gameplay where players rearrange scrambled tiles to match a target pattern, with multiple difficulty levels, automated solving algorithms, and the ability to use custom images.

## Features

- **Multiple Puzzle Sizes**: Play with 3×3, 4×4, or 5×5 puzzles
- **Duel Mode**: Compete against an AI solver
- **Custom Images**: Use your own images for puzzle tiles
- **Automated Solving Algorithms**:
  - Best-First Search: Guarantees an optimal solution
  - Hill Climbing: Faster but may not find the optimal solution
- **Save/Load System**: Save your progress and load it later
- **Map Management**: Create, save and load different puzzle configurations
- **Database Integration**: Store maps and high scores in a SQL Server database
- **Customizable Settings**: Adjust sound volume or toggle sound on/off

## Installation

### Prerequisites

- Python 3.7 or higher
- SQL Server (for database features)
- ODBC Driver 17 for SQL Server 

### Setup

1. Clone the repository or download the source code:
```
git clone https://github.com/JohnWickCP/HuyenAnhMeTung.git
cd huyen-anh-me-tung
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Database Setup:
   - Create a database named 'puzzle8' in SQL Server
   - The game will automatically create the necessary tables on first run

4. Run the game:
```
python main.py
```

## Game Controls

- **Mouse**: Click on tiles adjacent to the empty space to move them
- **UI Buttons**: Use on-screen buttons to navigate menus and perform actions

## Game Modes

### Standard Mode
Play the sliding puzzle game with different sizes (3×3, 4×4, or 5×5).

### Duel Mode
Race against an AI solver to see who can complete the puzzle first. You get a 3-move head start before the AI begins solving.

## Solving Algorithms

### Best-First Search
- Uses Manhattan distance as a heuristic
- Always finds the optimal (shortest) solution
- May be slower for larger puzzles

### Hill Climbing
- Faster algorithm but doesn't guarantee optimal solutions
- Uses Manhattan distance to evaluate moves
- May get stuck in local optima

## Map Management

- **Save Maps**: Create and save puzzle configurations for later
- **Load Maps**: Choose from previously saved maps
- **Delete Maps**: Remove maps you no longer want


## Technical Details

### Classes

- **Game**: Main game controller
- **Puzzle**: Handles the puzzle state and mechanics
- **MapManager**: Manages saved puzzle configurations
- **Database**: Handles database connections and operations
- **BestFirstSearch**: Implementation of Best-First Search algorithm
- **HillClimbing**: Implementation of Hill Climbing algorithm
- **Button**: UI button implementation

### Database Schema

- **PuzzleMaps**: Stores puzzle configurations
  - MapID, MapName, Size, BoardState, ImagePath, CreateDate
- **PuzzleResults**: Stores player results
  - ResultID, MapID, MoveCount, ElapsedTime, SolveDate

## Troubleshooting

### Database Connection Issues
- Ensure SQL Server is running
- Check if the ODBC Driver 17 for SQL Server is installed
- Verify that the 'puzzle8' database exists
- If problems persist, the game will still work without database functionality

### Sound Issues
- Ensure the sound files exist in the correct directory
- If sound files are missing, the game will run with sound disabled

### Font Issues
- The game tries to use 'segoeui.ttf' (Segoe UI)
- If not found, it falls back to system fonts

## License

[MIT License](LICENSE)

## Credits

- Developed by: JohnWickCP

## Acknowledgments

- Special thanks to anyone who contributed to the project
- Inspired by the classic sliding puzzle game
