import pygame
import sys
import os
from tkinter import Tk, filedialog

# Initialize pygame
pygame.init()

# Open file dialog to select image for the first floor
root = Tk()
root.withdraw()  # Hide the main Tkinter window
IMAGE_PATH = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.bmp")])
root.destroy()

if not IMAGE_PATH:
    sys.exit("No image selected")

# Set initial window size
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("DnD Map Fog Tool")

# Load the first image
image_original = pygame.image.load(IMAGE_PATH).convert()
image_width, image_height = image_original.get_size()

# Zoom variables
zoom_factor = 1.0
zoom_increment = 0.1
min_zoom = 0.5
max_zoom = 3.0

# Pan variables
offset_x, offset_y = 0, 0
pan_active = False

# Brush size
brush_size = 30

# Save and Load functions for fog layer
def save_fog_layer(floor, filename):
    pygame.image.save(floor['fog'], filename)

def load_fog_layer(floor, filename):
    floor['fog'] = pygame.image.load(filename).convert_alpha()

# Create a dictionary to store floor data
floors = {}
current_floor = 0  # Track the current floor
floors[current_floor] = {
    'image': pygame.image.load(IMAGE_PATH).convert(),
    'fog': pygame.Surface((image_width, image_height), pygame.SRCALPHA),
}

# Fill fog with fully opaque (black) initially
floors[current_floor]['fog'].fill((0, 0, 0, 255))

# Main loop variables
running = True
left_clicking = False  # Tracks if left mouse button is held down
right_clicking = False  # Tracks if right mouse button is held down

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                left_clicking = True
            elif event.button == 3:  # Right click
                right_clicking = True
            elif event.button == 2:  # Middle click for panning
                pan_active = True
            elif event.button == 4:  # Scroll up (zoom in)
                zoom_factor = min(zoom_factor + zoom_increment, max_zoom)
            elif event.button == 5:  # Scroll down (zoom out)
                zoom_factor = max(zoom_factor - zoom_increment, min_zoom)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                left_clicking = False
            elif event.button == 3:
                right_clicking = False
            elif event.button == 2:
                pan_active = False
        elif event.type == pygame.MOUSEMOTION:
            if pan_active:
                dx, dy = event.rel
                offset_x += dx
                offset_y += dy
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Save fog layer with 'S' key
                save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
                if save_path:
                    save_fog_layer(floors[current_floor], save_path)
            elif event.key == pygame.K_l:  # Load fog layer with 'L' key
                load_path = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
                if load_path:
                    load_fog_layer(floors[current_floor], load_path)
            elif event.key == pygame.K_TAB:  # Switch between floors using Tab
                current_floor = (current_floor + 1) % len(floors)
        
        # Create a new floor when 'N' is pressed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            # Prompt for a new image for the new floor
            root = Tk()
            root.withdraw()  # Hide the main Tkinter window
            new_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.bmp")])
            root.destroy()

            if not new_image_path:
                continue  # If no image is selected, don't create a new floor

            current_floor += 1
            new_image = pygame.image.load(new_image_path).convert()
            floors[current_floor] = {
                'image': new_image,
                'fog': pygame.Surface((new_image.get_width(), new_image.get_height()), pygame.SRCALPHA),
            }
            floors[current_floor]['fog'].fill((0, 0, 0, 255))

    # Apply zoom
    new_width = int(floors[current_floor]['image'].get_width() * zoom_factor)
    new_height = int(floors[current_floor]['image'].get_height() * zoom_factor)
    image = pygame.transform.scale(floors[current_floor]['image'], (new_width, new_height))

    # Center the image with offset
    image_rect = image.get_rect(center=(WINDOW_WIDTH // 2 + offset_x, WINDOW_HEIGHT // 2 + offset_y))

    # Adjust brush size based on zoom (inversely proportional to zoom factor)
    adjusted_brush_size = int(brush_size / zoom_factor)

    # Get mouse position relative to the window
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate the original position in the fog layer
    relative_x = (mouse_x - image_rect.left) / zoom_factor
    relative_y = (mouse_y - image_rect.top) / zoom_factor

    # Draw on the fog layer at original resolution
    if left_clicking and 0 <= relative_x < floors[current_floor]['image'].get_width() and 0 <= relative_y < floors[current_floor]['image'].get_height():
        pygame.draw.circle(floors[current_floor]['fog'], (0, 0, 0, 0), (int(relative_x), int(relative_y)), adjusted_brush_size)  # Erase fog
    elif right_clicking and 0 <= relative_x < floors[current_floor]['image'].get_width() and 0 <= relative_y < floors[current_floor]['image'].get_height():
        pygame.draw.circle(floors[current_floor]['fog'], (0, 0, 0, 255), (int(relative_x), int(relative_y)), adjusted_brush_size)  # Restore fog

    # Draw everything
    screen.fill((0, 0, 0))  # Clear screen
    screen.blit(image, image_rect.topleft)  # Draw the image
    # Draw fog layer at original position relative to the image
    fog_scaled = pygame.transform.scale(floors[current_floor]['fog'], (new_width, new_height))
    screen.blit(fog_scaled, image_rect.topleft)  # Draw the fog
    pygame.display.flip()

pygame.quit()
sys.exit()
