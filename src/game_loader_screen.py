import pygame
import sys
from .hex_board import HexBoard

class GameLoaderScreen:
    """Main menu screen with game options"""
    
    def __init__(self, width=1200, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Game Loader")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (25, 100, 200)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72);
        self.menu_font = pygame.font.Font(None, 48);
        self.text_font = pygame.font.Font(None, 24);
        
        self.clock = pygame.time.Clock()
        
        # Menu options
        self.menu_options = [
            "1) Single Player",
            "2) Multiplayer", 
            "3) Rules",
            "4) Script"
        ]
        
        self.selected_option = 0;
        self.current_screen = "main_menu"  # main_menu, rules
        
        # Load rules text
        self.rules_text = self.load_rules()
    
    def load_rules(self):
        """Load rules from Rules.txt file"""
        try:
            with open(r"C:\Users\Denver Zuzarte\vsc folder\LoyalAndTheLawless\PDA\src\Rules.txt", 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Rules file not found. Please create Rules.txt with game rules."
        except Exception as e:
            return f"Error loading rules: {e}"
    
    def draw_main_menu(self):
        """Draw the main menu screen"""
        self.screen.fill(self.BLACK)
        
        # Draw title
        title = self.title_font.render("Game Menu", True, self.WHITE)
        title_rect = title.get_rect()
        title_rect.centerx = self.width // 2
        title_rect.y = 100
        self.screen.blit(title, title_rect)
        
        # Draw menu options
        start_y = 250
        for i, option in enumerate(self.menu_options):
            color = self.WHITE if i == self.selected_option else self.LIGHT_GRAY
            option_text = self.menu_font.render(option, True, color)
            option_rect = option_text.get_rect()
            option_rect.centerx = self.width // 2
            option_rect.y = start_y + i * 80
            self.screen.blit(option_text, option_rect)
        
        # Draw instructions
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER to select",
            "Press ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.text_font.render(instruction, True, self.WHITE)
            text_rect = text.get_rect()
            text_rect.centerx = self.width // 2
            text_rect.y = 650 + i * 30
            self.screen.blit(text, text_rect)
    
    def draw_rules_screen(self):
        """Draw the rules screen"""
        self.screen.fill(self.BLUE)
        
        # Draw title
        title = self.title_font.render("Rules", True, self.WHITE)
        title_rect = title.get_rect()
        title_rect.centerx = self.width // 2
        title_rect.y = 50
        self.screen.blit(title, title_rect)
        
        # Draw rules text
        y_offset = 150
        line_height = 25
        max_width = self.width - 100
        
        # Split rules text into lines that fit the screen
        words = self.rules_text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            text_surface = self.text_font.render(test_line, True, self.WHITE)
            if text_surface.get_width() > max_width and current_line:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line.strip())
        
        # Display lines
        for i, line in enumerate(lines):
            if y_offset + i * line_height > self.height - 100:
                break  # Don't draw beyond screen
            text = self.text_font.render(line, True, self.WHITE)
            self.screen.blit(text, (50, y_offset + i * line_height))
        
        # Draw back instruction
        back_text = self.text_font.render("Press ESC to go back", True, self.WHITE)
        back_rect = back_text.get_rect()
        back_rect.centerx = self.width // 2
        back_rect.y = self.height - 50
        self.screen.blit(back_text, back_rect)
    
    def handle_main_menu_input(self, event):
        """Handle input for main menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:  # Single Player
                    self.launch_single_player()
                elif self.selected_option == 1:  # Multiplayer
                    print("Multiplayer not implemented yet")
                elif self.selected_option == 2:  # Rules
                    self.current_screen = "rules"
                elif self.selected_option == 3:  # Script
                    print("Script not implemented yet")
            elif event.key == pygame.K_ESCAPE:
                return False
        return True
    
    def handle_rules_input(self, event):
        """Handle input for rules screen"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_screen = "main_menu"
        return True
    
    def launch_single_player(self):
        """Launch single player hex board game"""
        pygame.quit()
        board = HexBoard()
        board.run()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.current_screen == "main_menu":
                    running = self.handle_main_menu_input(event)
                elif self.current_screen == "rules":
                    running = self.handle_rules_input(event)
            
            # Draw current screen
            if self.current_screen == "main_menu":
                self.draw_main_menu()
            elif self.current_screen == "rules":
                self.draw_rules_screen()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

loader = GameLoaderScreen()
loader.run()