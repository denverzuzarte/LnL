import pygame
import PIL

pygame.init()
screen_width = 500
screen_height = 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Image Display Example")
# Replace 'your_image.png' with the actual path to your image file
image_path = r"Images\\9.png" 
# Load the image
image = pygame.image.load(image_path).convert_alpha() # .convert_alpha() for transparency
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Clear the screen (optional, but good practice for updates)
    screen.fill((0, 0, 0)) # Fills the screen with white
    
    # Blit (draw) the image onto the screen
    # (x, y) are the top-left coordinates where the image will be drawn
    image_x = 0
    image_y = 0
    screen.blit(image, (image_x, image_y))
    
    # Update the display to show the changes
    pygame.display.flip() # or pygame.display.update()