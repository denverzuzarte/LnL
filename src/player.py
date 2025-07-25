import pygame
import math

class Player:
    """Player class using data from player.json"""
    
    def __init__(self, player_data, hex_radius=40):
        # Player data from JSON
        self.name = player_data['name']
        self.alignment = player_data['alignment']
        self.max_health = player_data['Health']
        self.current_health = player_data['Health']
        self.damage = player_data['Damage']
        self.range = player_data['range']
        self.max_moves = player_data['moves']
        self.current_moves = player_data['moves']
        self.special = player_data['Special']
        self.photo_path = player_data['Photo']
        
        # Game state
        self.q = 0  # Starting hex coordinate q
        self.r = 0  # Starting hex coordinate r
        self.hex_radius = hex_radius
        self.total_moves = 0  # Total moves made in game
        
        # UI state
        self.ability_screen_open = False
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.BLUE = (25, 100, 200)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        
        # Font for player number (will be initialized when needed)
        self.font = None
        self.ui_font = None
        
        # Hexagonal movement directions (rotated 60 degrees clockwise)
        self.movement_keys = {
            pygame.K_d: (1, -1),   # d: was e
            pygame.K_e: (0, -1),   # e: was w  
            pygame.K_w: (-1, 0),   # w: was a
            pygame.K_a: (-1, 1),   # a: was z
            pygame.K_z: (0, 1),    # z: was x
            pygame.K_x: (1, 0)     # x: was d
        }
    
    def new_turn(self):
        """Reset moves for new turn"""
        self.current_moves = self.max_moves
        print(f"{self.name} starts new turn with {self.max_moves} moves")
    
    def move(self, direction_key, difficult_terrain_coords=None, walls=None):
        """Move player in hexagonal direction"""
        if self.current_moves <= 0:
            print(f"{self.name} has no moves left this turn!")
            return False
            
        if direction_key in self.movement_keys:
            dq, dr = self.movement_keys[direction_key]
            new_q = self.q + dq
            new_r = self.r + dr
            
            # Check if there's a wall blocking this movement
            if walls:
                current_pos = (self.q, self.r)
                new_pos = (new_q, new_r)
                
                # Check both directions since walls can be stored either way
                wall1 = (current_pos, new_pos)
                wall2 = (new_pos, current_pos)
                
                if wall1 in walls or wall2 in walls:
                    print(f"Movement blocked by wall between {current_pos} and {new_pos}")
                    return False  # Movement blocked by wall
            
            # Check if destination is difficult terrain
            move_cost = 1
            if difficult_terrain_coords and (new_q, new_r) in difficult_terrain_coords:
                move_cost = 2
            
            # Check if player has enough moves
            if self.current_moves < move_cost:
                print(f"{self.name} needs {move_cost} moves but only has {self.current_moves} left!")
                return False
            
            self.q = new_q
            self.r = new_r
            self.current_moves -= move_cost
            self.total_moves += move_cost
            return True
        return False
    
    def toggle_ability_screen(self):
        """Toggle the ability screen on/off"""
        self.ability_screen_open = not self.ability_screen_open
    
    def close_ability_screen(self):
        """Close the ability screen"""
        self.ability_screen_open = False
    
    def use_attack(self):
        """Use basic attack ability"""
        print(f"{self.name} uses attack for {self.damage} damage!")
        self.close_ability_screen()
    
    def use_special_move(self):
        """Use special move ability"""
        print(f"{self.name} uses special move: {self.special}")
        self.close_ability_screen()
    
    def take_damage(self, damage):
        """Take damage and reduce health"""
        self.current_health = max(0, self.current_health - damage)
        return self.current_health <= 0  # Return True if player died
    
    def heal(self, amount):
        """Heal player"""
        self.current_health = min(self.max_health, self.current_health + amount)
    
    def get_pixel_position(self, center_x, center_y):
        """Convert hex coordinates to pixel coordinates"""
        # Standard coordinates
        standard_x = self.hex_radius * 1.5 * self.q
        standard_y = self.hex_radius * math.sqrt(3) * (self.r + self.q / 2)
        
        # Rotate by 30 degrees anticlockwise
        cos30 = math.cos(math.pi / 6)  # cos(30°) = √3/2
        sin30 = math.sin(math.pi / 6)  # sin(30°) = 0.5
        
        rotated_x = standard_x * cos30 - standard_y * sin30
        rotated_y = standard_x * sin30 + standard_y * cos30
        
        x = center_x + rotated_x
        y = center_y + rotated_y
        return x, y
    
    def _ensure_fonts(self):
        """Initialize fonts if not already done"""
        if self.font is None:
            self.font = pygame.font.Font(None, 24)
        if self.ui_font is None:
            self.ui_font = pygame.font.Font(None, 36)
    
    def draw_player(self, screen, center_x, center_y):
        """Draw the player as a small black coin with player number"""
        self._ensure_fonts()
        x, y = self.get_pixel_position(center_x, center_y)
        
        # Draw player coin (smaller than hex radius)
        coin_radius = self.hex_radius // 3
        pygame.draw.circle(screen, self.BLACK, (int(x), int(y)), coin_radius)
        pygame.draw.circle(screen, self.WHITE, (int(x), int(y)), coin_radius, 2)
        
        # Draw player initial
        player_text = self.font.render(self.name[0].upper(), True, self.WHITE)
        text_rect = player_text.get_rect()
        text_rect.center = (int(x), int(y))
        screen.blit(player_text, text_rect)
    
    def draw_ability_screen(self, screen, screen_width, screen_height):
        """Draw the ability screen overlay"""
        if not self.ability_screen_open:
            return
        
        self._ensure_fonts()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(128)
        overlay.fill(self.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Ability screen background
        screen_rect = pygame.Rect(screen_width//4, screen_height//4, 
                                screen_width//2, screen_height//2)
        pygame.draw.rect(screen, self.BLUE, screen_rect)
        pygame.draw.rect(screen, self.WHITE, screen_rect, 3)
        
        # Title
        title_text = self.ui_font.render(f"{self.name} Abilities", True, self.WHITE)
        title_rect = title_text.get_rect()
        title_rect.centerx = screen_width // 2
        title_rect.y = screen_height//4 + 30
        screen.blit(title_text, title_rect)
        
        # Player stats
        stats_y = screen_height//4 + 80
        health_text = self.ui_font.render(f"Health: {self.current_health}/{self.max_health}", True, self.WHITE)
        screen.blit(health_text, (screen_width//4 + 20, stats_y))
        
        damage_text = self.ui_font.render(f"Attack Damage: {self.damage}", True, self.WHITE)
        screen.blit(damage_text, (screen_width//4 + 20, stats_y + 40))
        
        moves_text = self.ui_font.render(f"Moves: {self.current_moves}/{self.max_moves}", True, self.WHITE)
        screen.blit(moves_text, (screen_width//4 + 20, stats_y + 80))
        
        range_text = self.ui_font.render(f"Range: {self.range}", True, self.WHITE)
        screen.blit(range_text, (screen_width//4 + 20, stats_y + 120))
        
        # Ability options
        options_y = screen_height//4 + 250
        attack_text = self.ui_font.render("1) Attack", True, self.WHITE)
        screen.blit(attack_text, (screen_width//4 + 20, options_y))
        
        special_text = self.ui_font.render("2) Special Move", True, self.WHITE)
        screen.blit(special_text, (screen_width//4 + 20, options_y + 50))
        
        # Instructions
        instructions_y = screen_height//4 + screen_height//2 - 80
        instruction_texts = [
            "Press 1 for Attack, 2 for Special Move",
            "Press S or ESC to close"
        ]
        
        for i, instruction in enumerate(instruction_texts):
            text = self.ui_font.render(instruction, True, self.WHITE)
            text_rect = text.get_rect()
            text_rect.centerx = screen_width // 2
            text_rect.y = instructions_y + i * 30
            screen.blit(text, text_rect)
    
    def handle_ability_input(self, event):
        """Handle input when ability screen is open"""
        if not self.ability_screen_open:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.use_attack()
                return True
            elif event.key == pygame.K_2:
                self.use_special_move()
                return True
            elif event.key == pygame.K_s or event.key == pygame.K_ESCAPE:
                self.close_ability_screen()
                return True
        
        return False