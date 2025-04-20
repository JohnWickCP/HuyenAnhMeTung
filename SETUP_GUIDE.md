# Setup Guide for Huyễn Ảnh Mê Tung

This guide provides detailed instructions for setting up and running the "Huyễn Ảnh Mê Tung" sliding puzzle game.

## System Requirements

- Windows 10 or 11 (recommended for full compatibility with SQL Server)
- Python 3.7 or higher
- 100MB free disk space
- Graphics card with basic 2D capabilities
- Sound card (optional, for audio features)

## Database Setup

The game uses Microsoft SQL Server for storing puzzle maps and results. Follow these steps to set up the database:

1. **Install SQL Server**
   - Download and install [SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
   - During installation, enable "SQL Server Authentication Mode"
   - Create a password for the 'sa' account

2. **Install SQL Server Management Studio (SSMS)**
   - Download and install [SSMS](https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)

3. **Create the Database**
   - Open SSMS and connect to your local SQL Server instance
   - Right-click on "Databases" and select "New Database"
   - Enter "puzzle8" as the database name and click OK

4. **Install ODBC Driver**
   - Download and install [ODBC Driver 17 for SQL Server](https://www.microsoft.com/en-us/download/details.aspx?id=56567)

## Python Environment Setup

1. **Install Python**
   - Download and install [Python 3.7 or higher](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Create a Virtual Environment (recommended)**
   ```
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install Required Packages**
   ```
   pip install -r requirements.txt
   ```


## Sound Files

The game requires several sound files. You can use your own audio files and rename them to match the expected filenames:

1. Place the following sound files in the `Game2/sounds/` directory:
   - `welcome_music.mp3` - Music for the welcome screen
   - `game_music.mp3` - Background music during gameplay
   - `victory.wav` - Sound effect when completing a puzzle

## Font File

The game uses the Segoe UI font for displaying Vietnamese text:

1. Locate the font file `segoeui.ttf` on your system (typically in `C:\Windows\Fonts\` on Windows)
2. Copy it to your game directory

## Running the Game

1. Make sure the virtual environment is activated
2. Navigate to the game directory
3. Run the game:
   ```
   python main.py
   ```

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Verify SQL Server is running:
   - Open Services (services.msc)
   - Ensure "SQL Server (SQLEXPRESS)" is running

2. Check connection string in the code:
   - Open main.py
   - Find the `Database.__init__` method
   - Modify the connection string if needed:
     ```python
     self.conn = pyodbc.connect(
         'DRIVER={ODBC Driver 17 for SQL Server};'
         'SERVER=localhost\\SQLEXPRESS;'  # Adjust if your instance name is different
         'DATABASE=puzzle8;'
         'Trusted_Connection=yes;'
     )
     ```

3. If you still have issues, you can modify the code to work without a database:
   - Look for error handling in the Database class
   - The game should continue to work, but without saving maps or results

### Sound Issues

If sound doesn't work:

1. Check that pygame.mixer is properly initialized
2. Verify that sound files exist in the correct location
3. Test with different audio formats if needed

### Display Issues

If you encounter display problems:

1. Adjust the SCREEN_WIDTH and SCREEN_HEIGHT constants at the top of the code
2. Lower the resolution if the game runs slowly
3. Make sure you have the latest graphics drivers

## Extending the Game

### Adding Custom Images

You can use your own images for puzzles:

1. Prepare square images (recommended sizes: 480×480, 640×640, or 800×800)
2. Use the "Load Image" button in the game to select your image

### Modifying Difficulty Levels

To adjust puzzle difficulty:

1. Open main.py
2. Find the `Puzzle.shuffle` method
3. Adjust the default `moves` parameter (higher = more difficult)

### Adding New Features

The modular architecture allows for easy addition of new features:

- Add new game modes by extending the Game class
- Create new solving algorithms by creating new classes similar to BestFirstSearch
- Extend the UI by adding new Button instances to Game.create_buttons