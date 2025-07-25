# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

To run the main game:
```bash
cd src
python game_loader_screen.py
```

To run just the hex board (for testing):
```bash
cd src
python hex_board.py
```

## Core Architecture

This is a pygame-based tactical board game called "Loyal and The Lawless" with a hexagonal grid system.

### Game Flow
1. **Main Menu** (`game_loader_screen.py`) - Entry point with options for Single Player, Multiplayer, Rules, Script
2. **Alignment Selection** - Choose between Loyal (royal blue), Lawless (blood red), or Neutral (royal purple)
3. **Player Selection** - Pick a character from the chosen alignment using data from `players.json`
4. **Hex Board Game** (`hex_board.py`) - The main tactical gameplay

### Coordinate System
- Uses **cube coordinates** (q, r) for hexagonal positioning
- The coordinate system is **rotated 60 degrees clockwise** from standard
- Visual board is rotated 30 degrees anticlockwise for aesthetic purposes
- Movement keys: d, e, w, a, z, x correspond to the 6 hexagonal directions

### Data Files
- `terrain.json` - Stores difficult terrain coordinates and wall positions between adjacent hexes
- `players.json` (older format) and `players.json` (new format) - Character data with alignment, stats, and image paths
- `Rules.txt` - Game rules displayed in the rules screen
- Player images stored in `Images/` directory

### Key Components

**HexBoard Class** (`hex_board.py`):
- Renders hexagonal grid with terrain types (simple/difficult)
- Handles wall visualization between adjacent hexes
- Integrates player movement and ability system
- Loads terrain data from JSON

**Player Class** (`player.py`):
- Manages player stats (health, attack damage, move count)
- Handles hexagonal movement with rotated coordinate system
- Provides ability screen UI (attack/special move options)
- Renders player as numbered coin on board

**GameLoaderScreen Class** (`game_loader_screen.py`):
- Multi-screen menu system with navigation
- Loads and displays player data with images
- Shows hex board as backdrop during selection screens
- Manages game state transitions

### Important Implementation Details

- **Font Initialization**: Player class uses lazy font loading to avoid pygame initialization errors during import
- **Image Loading**: Player images are automatically scaled to 150x150 and loaded from `Images/` directory
- **Hex Rendering**: Each hexagon is individually rotated for visual presentation
- **Wall System**: Walls are drawn as thick grey lines between adjacent hex coordinates
- **Movement System**: Uses pygame key events with custom hexagonal direction mapping

### Project Structure
```
src/
├── game_loader_screen.py  # Main entry point and menu system
├── hex_board.py          # Core game board and rendering
├── player.py             # Player class and mechanics
├── terrain.json          # Board layout data
├── players.json          # Character data
└── Rules.txt            # Game rules text
```

The game is designed as a tactical board game with plans for commercial release, website hosting, and physical wooden board creation.