import pygame
import math
import random
import json
import os
from .player import Player

class HexBoard:
    """A hexagonal board with simple and difficult terrain"""
    
    def __init__(self, width=1200, height=800, hex_radius=40):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Hexagonal Board - Simple & Difficult Terrain")
        
        self.hex_radius = hex_radius
        
        # Terrain colors - made more contrasting
        self.SIMPLE_TERRAIN = (255, 255, 200)   # Very light yellow/ochre
        self.DIFFICULT_TERRAIN = (100, 50, 0)   # Dark brown
        self.WATER_COLOR = (25, 100, 200)       # Blue for surrounding
        self.BLACK = (0, 0, 0)                  # Border color
        self.WHITE = (255, 255, 255)            # Text color
        self.GRAY = (127,127,127) 
        
        # Generate hexagonal board (6 hexes per side)
        self.board_radius = 6
        self.hexagons = self.generate_hexagonal_board()
        
        # Data storage
        self.difficult_terrain = set()  # Set of (q, r) coordinates
        self.walls = set()  # Set of ((q1, r1), (q2, r2)) coordinate pairs
        
        # JSON file path
        self.terrain_file = r"D:\vsc folder\LoyalAndTheLawless\src\terrain.json"
        
        # Player selection state
        self.game_state = "alignment_selection"  # alignment_selection, player_selection, playing
        self.selected_alignment = 0
        self.selected_player_index = 0
        self.available_players = []
        self.player_images = {}
        self.player = None
        
        # Load player data
        self.load_player_data()
        
        # Load existing data
        self.load_terrain_data()
        
        # Apply loaded terrain data to hexagons
        self.apply_terrain_data()
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 18)
        self.coord_font = pygame.font.Font(None, 16)
        self.title_font = pygame.font.Font(None, 48)
        self.menu_font = pygame.font.Font(None, 36)
        
        # Alignment options
        self.alignments = [
            ("Loyal", (65, 105, 225)),    # Royal Blue
            ("Lawless", (139, 0, 0))      # Blood Red
        ]
    
    def generate_hexagonal_board(self):
        """Generate hexagonal board with terrain types"""
        hexagons = []
        center_x = self.width // 2
        center_y = self.height // 2
        
        for q in range(-self.board_radius + 1, self.board_radius):
            r1 = max(-self.board_radius + 1, -q - self.board_radius + 1)
            r2 = min(self.board_radius - 1, -q + self.board_radius - 1)
            for r in range(r1, r2 + 1):
                # Convert cube coordinates to pixel coordinates
                # Standard coordinates
                standard_x = self.hex_radius * 1.5 * q
                standard_y = self.hex_radius * math.sqrt(3) * (r + q / 2)
                
                # Rotate by 30 degrees anticlockwise
                cos30 = math.cos(math.pi / 6)  # cos(30°) = √3/2
                sin30 = math.sin(math.pi / 6)  # sin(30°) = 0.5
                
                rotated_x = standard_x * cos30 - standard_y * sin30
                rotated_y = standard_x * sin30 + standard_y * cos30
                
                x = center_x + rotated_x
                y = center_y + rotated_y
                
                # All hexes are now land terrain (simple by default)
                #if :
                terrain_type = 'simple'
                color = self.SIMPLE_TERRAIN
                
                hexagons.append({
                    'q': q, 'r': r,
                    'x': x, 'y': y,
                    'terrain_type': terrain_type,
                    'color': color
                })
        
        return hexagons
    
    def load_terrain_data(self):
        """Load terrain data from unified JSON file"""
        try:
            if os.path.exists(self.terrain_file):
                with open(self.terrain_file, 'r') as f:
                    data = json.load(f)
                    
                    # Handle different data structures
                    if isinstance(data, dict):
                        # If it's a dictionary with separate sections
                        terrain_list = data.get('difficult terrain', [])
                        print(terrain_list)
                        walls_list = data.get('walls', [])
                    elif isinstance(data, list):
                        # If it's just a list of difficult terrain coordinates
                        terrain_list = data
                        walls_list = []
                    else:
                        terrain_list = []
                        walls_list = []
                    
                    self.difficult_terrain = set(tuple(coord) for coord in terrain_list)
                    self.walls = set(tuple(tuple(coord) for coord in wall) for wall in walls_list)
                    
                    # Add perimeter walls
                    self.add_perimeter_walls()
                    
                    print(f"Loaded {len(self.difficult_terrain)} difficult terrain coordinates")
                    for coord in self.difficult_terrain:
                        print(f"  Difficult terrain at: {coord}")
                    print(f"Loaded {len(self.walls)} walls")
            else:
                print(f"Terrain file {self.terrain_file} not found, starting with empty terrain")
                self.difficult_terrain = set()
                self.walls = set()
                # Add perimeter walls even when no terrain file exists
                self.add_perimeter_walls()
        except Exception as e:
            print(f"Error loading terrain data: {e}")
            self.difficult_terrain = set()
            self.walls = set()
            # Add perimeter walls even when there's an error
            self.add_perimeter_walls()
    
    def load_player_data(self):
        try:
            with open(r"D:\\vsc folder\\LoyalAndTheLawless\\src\\player.json", 'r') as f:
                players_data = json.load(f)
                
            # Convert to list format for easier handling
            self.all_players = []
            for player_key, player_data in players_data.items():
                player_data['key'] = player_key
                self.all_players.append(player_data)
                
            # Load player images
            for player_data in self.all_players:
                image_path = player_data.get('Photo', '')
                if image_path:
                    try:
                        image = pygame.image.load(image_path)
                        image = pygame.transform.scale(image, (120, 120))
                        self.player_images[player_data['name']] = image
                    except Exception as e:
                        print(f"Could not load image for {player_data['name']}: {e}")
                        self.player_images[player_data['name']] = None
                        
        except Exception as e:
            print(f"Error loading player data: {e}")
            self.all_players = []
    
    def filter_players_by_alignment(self):
        """Filter players by selected alignment + neutral characters"""
        alignment_name = self.alignments[self.selected_alignment][0].lower()
        
        # Include both the selected alignment and neutral characters
        self.available_players = [p for p in self.all_players 
                                if p.get('alignment', '').lower() == alignment_name 
                                or p.get('alignment', '').lower() == 'neutral']
        
        print(f"Available players for {alignment_name}: {[p['name'] for p in self.available_players]}")
        self.selected_player_index = 0
    
    def draw_alignment_selection(self):
        self.screen.fill(self.BLACK)
        
        # Draw title
        title = self.title_font.render("Choose Your Alignment", True, self.WHITE)
        title_rect = title.get_rect()
        title_rect.centerx = self.width // 2
        title_rect.y = 200
        self.screen.blit(title, title_rect)
        
        # Draw alignment options
        for i, (name, color) in enumerate(self.alignments):
            y_pos = 300 + i * 100
            
            # Highlight selected alignment
            if i == self.selected_alignment:
                highlight_rect = pygame.Rect(self.width//2 - 150, y_pos - 10, 300, 80)
                pygame.draw.rect(self.screen, self.WHITE, highlight_rect, 3)
            
            # Draw alignment name
            alignment_text = self.menu_font.render(name, True, color)
            alignment_rect = alignment_text.get_rect()
            alignment_rect.centerx = self.width // 2
            alignment_rect.y = y_pos
            self.screen.blit(alignment_text, alignment_rect)
            
            # Draw color preview
            color_rect = pygame.Rect(self.width//2 - 50, y_pos + 40, 100, 20)
            pygame.draw.rect(self.screen, color, color_rect)
            pygame.draw.rect(self.screen, self.WHITE, color_rect, 2)
        
        # Draw instructions
        instructions = [
            "Use UP/DOWN arrows to select alignment",
            "Press ENTER to continue"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, self.WHITE)
            text_rect = text.get_rect()
            text_rect.centerx = self.width // 2
            text_rect.y = 600 + i * 25
            self.screen.blit(text, text_rect)
    
    def draw_player_selection(self):
        self.screen.fill(self.BLACK)
        
        alignment_name, alignment_color = self.alignments[self.selected_alignment]
        
        # Draw title
        title = self.title_font.render(f"Choose Your Player ({alignment_name} + Neutral)", True, alignment_color)
        title_rect = title.get_rect()
        title_rect.centerx = self.width // 2
        title_rect.y = 30
        self.screen.blit(title, title_rect)
        
        if not self.available_players:
            no_players_text = self.menu_font.render("No players available for this alignment", True, self.WHITE)
            text_rect = no_players_text.get_rect()
            text_rect.centerx = self.width // 2
            text_rect.centery = self.height // 2
            self.screen.blit(no_players_text, text_rect)
            return
        
        # Display high-quality character images in a grid
        start_x = 80
        start_y = 120
        image_width = 160   # 1:1.5 ratio - width (20% smaller)
        image_height = 240  # 1:1.5 ratio - height (20% smaller)
        spacing = 50
        
        for i, player_data in enumerate(self.available_players):
            x = start_x + (i % 4) * (image_width + spacing)  # 4 columns
            y = start_y + (i // 4) * (image_height + spacing + 60)  # Extra space for name
            
            # Highlight selected player with a border
            if i == self.selected_player_index:
                highlight_rect = pygame.Rect(x - 5, y - 5, image_width + 10, image_height + 50)
                pygame.draw.rect(self.screen, alignment_color, highlight_rect, 4)
            
            # Draw high-quality player image
            if player_data['name'] in self.player_images and self.player_images[player_data['name']]:
                # Scale image with smooth scaling for clarity and maintain 1:1.5 ratio
                original_image = self.player_images[player_data['name']]
                scaled_image = pygame.transform.smoothscale(original_image, (image_width, image_height))
                self.screen.blit(scaled_image, (x, y))
            else:
                # Placeholder for missing images
                placeholder_rect = pygame.Rect(x, y, image_width, image_height)
                pygame.draw.rect(self.screen, self.GRAY, placeholder_rect)
                pygame.draw.rect(self.screen, self.WHITE, placeholder_rect, 2)
                no_img_text = self.menu_font.render("No Image", True, self.WHITE)
                text_rect = no_img_text.get_rect()
                text_rect.center = placeholder_rect.center
                self.screen.blit(no_img_text, text_rect)
            
            # Draw player name below the image
            name_text = self.menu_font.render(player_data['name'].title(), True, self.WHITE)
            name_rect = name_text.get_rect()
            name_rect.centerx = x + image_width // 2
            name_rect.y = y + image_height + 5
            self.screen.blit(name_text, name_rect)
        
        # Draw instructions at the bottom
        instructions = [
            "Use ARROW KEYS to navigate",
            "Press ENTER to select player",
            "Press ESC to go back"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, self.WHITE)
            text_rect = text.get_rect()
            text_rect.centerx = self.width // 2
            text_rect.y = 720 + i * 20
            self.screen.blit(text, text_rect)
    
    def add_perimeter_walls(self):
        """Add walls to all perimeter edges of the hexagonal board"""
        # Create a set of all existing hex coordinates
        hex_coords = set((hex_tile['q'], hex_tile['r']) for hex_tile in self.hexagons)
        
        # For each hex, check its 6 neighbors
        # Hexagonal directions: (1,0), (1,-1), (0,-1), (-1,0), (-1,1), (0,1)
        hex_directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        
        for hex_tile in self.hexagons:
            q, r = hex_tile['q'], hex_tile['r']
            
            for dq, dr in hex_directions:
                neighbor_q = q + dq
                neighbor_r = r + dr
                neighbor_coord = (neighbor_q, neighbor_r)
                
                # If neighbor doesn't exist, this is a perimeter edge
                if neighbor_coord not in hex_coords:
                    # Add wall between current hex and the non-existent neighbor
                    wall = ((q, r), neighbor_coord)
                    self.walls.add(wall)
        
        print(f"Added perimeter walls. Total walls now: {len(self.walls)}")
    
    def save_terrain_data(self):
        """Save difficult terrain coordinates to JSON file"""
        try:
            terrain_list = list(self.difficult_terrain)
            with open(self.terrain_file, 'w') as f:
                json.dump(terrain_list, f, indent=2)
            print(f"Saved {len(self.difficult_terrain)} difficult terrain coordinates")
        except Exception as e:
            print(f"Error saving terrain data: {e}")
    
    
    def apply_terrain_data(self):
        """Apply loaded terrain data to hexagon objects"""
        for hex_tile in self.hexagons:
            coord = (hex_tile['q'], hex_tile['r'])
            if coord in self.difficult_terrain:
                hex_tile['terrain_type'] = 'difficult'
                hex_tile['color'] = self.DIFFICULT_TERRAIN
    
    def hex_corners(self, center_x, center_y):
        """Calculate the 6 corners of a hexagon"""
        corners = []
        for i in range(6):
            # Rotate each corner by 30 degrees (π/6 radians)
            angle = i * math.pi / 3 + math.pi / 6
            x = center_x + self.hex_radius * math.cos(angle)
            y = center_y + self.hex_radius * math.sin(angle)
            corners.append((x, y))
        return corners
    
    def draw_hexagon(self, hex_tile):
        """Draw a single hexagon with coordinates"""
        corners = self.hex_corners(hex_tile['x'], hex_tile['y'])
        
        # Fill hexagon with terrain color
        pygame.draw.polygon(self.screen, hex_tile['color'], corners)
        
        # Draw black border
        pygame.draw.polygon(self.screen, self.BLACK, corners, 3)
        
        # Draw coordinates on all hexes
        coord_text = f"({hex_tile['q']},{hex_tile['r']})"
        text_surface = self.coord_font.render(coord_text, True, self.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.center = (int(hex_tile['x']), int(hex_tile['y'] - 5))
        self.screen.blit(text_surface, text_rect)
        
        # Add "D" marker for difficult terrain
        if hex_tile['terrain_type'] == 'difficult':
            d_text = self.font.render("D", True, self.WHITE)
            d_rect = d_text.get_rect()
            d_rect.center = (int(hex_tile['x']), int(hex_tile['y'] + 10))
            self.screen.blit(d_text, d_rect)
    
    def has_wall_between(self, coord1, coord2):
        """Check if there's a wall between two coordinates (order independent)"""
        wall1 = (coord1, coord2)
        wall2 = (coord2, coord1)
        return wall1 in self.walls or wall2 in self.walls
    
    def draw_walls(self):
        """Draw all walls as thick grey lines between hexes"""
        for wall in self.walls:
            coord1, coord2 = wall
            
            # Find the hex tiles for these coordinates
            hex1 = None
            hex2 = None
            
            for hex_tile in self.hexagons:
                if (hex_tile['q'], hex_tile['r']) == coord1:
                    hex1 = hex_tile
                elif (hex_tile['q'], hex_tile['r']) == coord2:
                    hex2 = hex_tile
            
            # If both hexes exist, draw wall between them
            if hex1 and hex2:
                # Calculate midpoint between hex centers
                mid_x = (hex1['x'] + hex2['x']) / 2
                mid_y = (hex1['y'] + hex2['y']) / 2
                
                # Calculate direction vector from hex1 to hex2
                dx = hex2['x'] - hex1['x']
                dy = hex2['y'] - hex1['y']
                
                # Calculate perpendicular vector for wall thickness
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    # Normalize and rotate 90 degrees
                    perp_x = -dy / length * self.hex_radius * 0.6
                    perp_y = dx / length * self.hex_radius * 0.6
                    
                    # Wall endpoints
                    wall_start = (mid_x + perp_x, mid_y + perp_y)
                    wall_end = (mid_x - perp_x, mid_y - perp_y)
                    
                    # Draw thick grey wall
                    pygame.draw.line(self.screen, (128, 128, 128), wall_start, wall_end, 8)
    
    def draw_player_card(self):
        """Draw selected player card at bottom right"""
        if not self.player:
            return
            
        # Card dimensions
        card_width = 250
        card_height = 150
        card_x = self.width - card_width - 20
        card_y = self.height - card_height - 20
        
        # Draw card background
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, self.GRAY, card_rect)
        pygame.draw.rect(self.screen, self.WHITE, card_rect, 2)
        
        # Draw player image
        if self.player.name in self.player_images and self.player_images[self.player.name]:
            image = pygame.transform.scale(self.player_images[self.player.name], (80, 80))
            self.screen.blit(image, (card_x + 10, card_y + 10))
        
        # Draw player stats
        info_x = card_x + 100
        name_text = self.font.render(self.player.name, True, self.BLACK)
        self.screen.blit(name_text, (info_x, card_y + 10))
        
        health_text = self.font.render(f"Health: {self.player.current_health}/{self.player.max_health}", True, self.BLACK)
        self.screen.blit(health_text, (info_x, card_y + 30))
        
        damage_text = self.font.render(f"Damage: {self.player.damage}", True, self.BLACK)
        self.screen.blit(damage_text, (info_x, card_y + 50))
        
        moves_text = self.font.render(f"Moves: {self.player.current_moves}/{self.player.max_moves}", True, self.BLACK)
        self.screen.blit(moves_text, (info_x, card_y + 70))
        
        range_text = self.font.render(f"Range: {self.player.range}", True, self.BLACK)
        self.screen.blit(range_text, (info_x, card_y + 90))
        
        # Draw turn instructions
        turn_text = self.font.render("Press N for new turn", True, self.BLACK)
        self.screen.blit(turn_text, (info_x, card_y + 120))
    
    def draw_board(self):
        """Draw the complete hexagonal board"""
        # Clear screen with dark background
        self.screen.fill(self.WATER_COLOR)
        
        # Draw all hexagons
        for hex_tile in self.hexagons:
            self.draw_hexagon(hex_tile)
        
        # Draw walls on top of hexagons
        self.draw_walls()
        
        # Draw player if exists
        if self.player:
            self.player.draw_player(self.screen, self.width // 2, self.height // 2)
            
            # Draw ability screen if open
            self.player.draw_ability_screen(self.screen, self.width, self.height)
            
            # Draw player card
            self.draw_player_card()
        
        # Draw title
        title = self.font.render("Hexagonal Board - Simple & Difficult Terrain", True, self.WHITE)
        title_rect = title.get_rect()
        title_rect.centerx = self.width // 2
        title_rect.y = 20
        self.screen.blit(title, title_rect)
        
        # Draw legend
        legend_items = [
            ("Simple Terrain (Light Ochre)", self.SIMPLE_TERRAIN),
            ("Difficult Terrain (Brown)", self.DIFFICULT_TERRAIN)
        ]
        
        for i, (name, color) in enumerate(legend_items):
            y_pos = 60 + i * 25
            # Draw colored square
            pygame.draw.rect(self.screen, color, (20, y_pos, 20, 20))
            pygame.draw.rect(self.screen, self.BLACK, (20, y_pos, 20, 20), 1)
            # Draw text
            text = self.font.render(name, True, self.WHITE)
            self.screen.blit(text, (50, y_pos))
        
        # Draw move counter in top right (only during playing)
        if self.player:
            move_counter_text = f"Total Moves: {self.player.total_moves}"
            counter_surface = self.font.render(move_counter_text, True, self.WHITE)
            counter_rect = counter_surface.get_rect()
            counter_rect.topright = (self.width - 20, 20)
            self.screen.blit(counter_surface, counter_rect)
        
        # Draw instructions
        instructions = [
            "Terrain loaded from difficult_terrain.json",
            "Press ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, self.WHITE)
            self.screen.blit(text, (20, 160 + i * 25))
    
    def handle_alignment_input(self, event):
        """Handle input for alignment selection"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_alignment = (self.selected_alignment - 1) % len(self.alignments)
            elif event.key == pygame.K_DOWN:
                self.selected_alignment = (self.selected_alignment + 1) % len(self.alignments)
            elif event.key == pygame.K_RETURN:
                self.filter_players_by_alignment()
                self.game_state = "player_selection"
            elif event.key == pygame.K_ESCAPE:
                return False
        return True
    
    def handle_player_input(self, event):
        """Handle input for player selection"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_player_index = max(0, self.selected_player_index - 1)
            elif event.key == pygame.K_RIGHT:
                self.selected_player_index = min(len(self.available_players) - 1, self.selected_player_index + 1)
            elif event.key == pygame.K_UP:
                self.selected_player_index = max(0, self.selected_player_index - 3)
            elif event.key == pygame.K_DOWN:
                self.selected_player_index = min(len(self.available_players) - 1, self.selected_player_index + 3)
            elif event.key == pygame.K_RETURN:
                # Create player from selected data
                player_data = self.available_players[self.selected_player_index]
                self.player = Player(player_data)
                self.game_state = "playing"
            elif event.key == pygame.K_ESCAPE:
                self.game_state = "alignment_selection"
        return True
    
    def handle_game_input(self, event):
        """Handle input during gameplay"""
        if event.type == pygame.KEYDOWN:
            # Handle ability screen input first
            if self.player and self.player.handle_ability_input(event):
                return True
            
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_n:
                # New turn - reset moves
                if self.player:
                    self.player.new_turn()
            elif event.key == pygame.K_s:
                if self.player:
                    self.player.toggle_ability_screen()
            # Handle player movement
            elif self.player and event.key in self.player.movement_keys:
                self.player.move(event.key, self.difficult_terrain, self.walls)
        return True
    
    def run(self):
        """Main display loop"""
        print("Hexagonal Board - Simple & Difficult Terrain")
        print("Terrain loaded from difficult_terrain.json")
        print("Press ESC to quit")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                else:
                    if self.game_state == "alignment_selection":
                        running = self.handle_alignment_input(event)
                    elif self.game_state == "player_selection":
                        running = self.handle_player_input(event)
                    elif self.game_state == "playing":
                        running = self.handle_game_input(event)
            
            # Draw appropriate screen
            if self.game_state == "alignment_selection":
                self.draw_alignment_selection()
            elif self.game_state == "player_selection":
                self.draw_player_selection()
            elif self.game_state == "playing":
                self.draw_board()
                
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    board = HexBoard()
    board.run()