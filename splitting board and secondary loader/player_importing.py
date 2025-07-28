import pygame
import json

class PlayerImporting:
    def __init__(self, width, height, board_radius, hex_radius):
        self.width = width
        self.height = height
        self.board_radius = board_radius
        self.hex_radius = hex_radius
        
        # Initialize Pygame
        pygame.init()
        
        # Set up the display
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Player Importing")
        
        # Define colors
        self.SIMPLE_TERRAIN = (200, 200, 200)  # Light gray for simple terrain
        
        # Initialize player data
    
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
