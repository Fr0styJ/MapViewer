import pygame
import sys
from PIL import Image
import os
import json
import tkinter as tk
from tkinter import filedialog

class Floor:
    def __init__(self, image_path, name, fog_texture):
        self.image_path = image_path
        self.name = name
        self.map_image = Image.open(image_path)
        self.width, self.height = self.map_image.size
        self.map_surface = pygame.image.fromstring(
            self.map_image.tobytes(),
            self.map_image.size,
            self.map_image.mode
        )
        self.fog_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.fog_texture = fog_texture
        self.create_fog_surface()
        self.explored_areas = set()
        self.pan_offset = [0, 0]
        self.zoom_factor = 1.0
    
    def create_fog_surface(self):
        """Create the fog surface using the cloud texture."""
        # Clear the surface
        self.fog_surface.fill((0, 0, 0, 0))
        
        if self.fog_texture is not None:
            # Calculate how many times we need to tile the texture
            texture_width = self.fog_texture.get_width()
            texture_height = self.fog_texture.get_height()
            
            # Create a temporary surface for the tiled texture
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Tile the texture across the surface
            for x in range(0, self.width, texture_width):
                for y in range(0, self.height, texture_height):
                    temp_surface.blit(self.fog_texture, (x, y))
            
            # Apply a dark overlay to make it more opaque
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Increased opacity for better visibility
            
            # Combine the texture and overlay
            self.fog_surface.blit(temp_surface, (0, 0))
            self.fog_surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            # If no texture is available, use solid black fog
            self.fog_surface.fill((0, 0, 0, 255))

class MapViewer:
    def __init__(self):
        pygame.init()
        self.screen = None
        self.floors = []
        self.current_floor_index = -1
        self.brush_size = 20
        self.running = True
        self.is_revealing = True
        self.scale_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 3.0
        self.show_controls = True
        self.panning = False
        self.last_pan_pos = None
        self.tab_height = 40
        self.tab_width = 150
        self.fog_texture = None  # Will be loaded when needed
        
    def select_map_file(self):
        """Open a file dialog to select a map image."""
        root = tk.Tk()
        root.withdraw()
        
        filetypes = (
            ('Image files', '*.jpg;*.jpeg;*.png;*.bmp'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Select a map image',
            filetypes=filetypes
        )
        
        return filename if filename else None
    
    def add_floor(self, image_path):
        """Add a new floor to the viewer."""
        try:
            # Get floor name from the file name
            name = os.path.splitext(os.path.basename(image_path))[0]
            
            # Create new floor
            floor = Floor(image_path, name, self.fog_texture)
            self.floors.append(floor)
            
            # Set as current floor if it's the first one
            if self.current_floor_index == -1:
                self.current_floor_index = 0
                self.initialize_screen(floor)
            
            # Load explored areas if they exist
            self.load_explored_areas(floor)
            
        except Exception as e:
            print(f"Error adding floor: {e}")
            return False
        return True
    
    def remove_floor(self, index):
        """Remove a floor from the viewer."""
        if 0 <= index < len(self.floors):
            self.floors.pop(index)
            if self.current_floor_index >= len(self.floors):
                self.current_floor_index = len(self.floors) - 1
            if self.current_floor_index >= 0:
                self.initialize_screen(self.floors[self.current_floor_index])
            else:
                self.screen = None
    
    def initialize_screen(self, floor):
        """Initialize the pygame screen for a floor."""
        if not self.screen:
            self.screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
            pygame.display.set_caption("D&D Map Viewer")
            # Load fog texture after display is initialized
            self.load_fog_texture()
        
        # Calculate initial scale factor
        self.scale_factor = min(800 / floor.width, 600 / floor.height)
    
    def load_explored_areas(self, floor):
        """Load previously explored areas from a .map file."""
        map_file = f"{os.path.splitext(floor.image_path)[0]}.map"
        try:
            with open(map_file, 'r') as f:
                data = json.load(f)
                floor.explored_areas = set(tuple(area) for area in data['explored_areas'])
                floor.pan_offset = data.get('pan_offset', [0, 0])
                floor.zoom_factor = data.get('zoom_factor', 1.0)
                # Apply explored areas to fog surface
                for x, y in floor.explored_areas:
                    pygame.draw.circle(floor.fog_surface, (0, 0, 0, 0), (x, y), self.brush_size)
        except FileNotFoundError:
            pass
    
    def save_explored_areas(self, floor):
        """Save explored areas to a .map file."""
        map_file = f"{os.path.splitext(floor.image_path)[0]}.map"
        data = {
            'explored_areas': list(floor.explored_areas),
            'pan_offset': floor.pan_offset,
            'zoom_factor': floor.zoom_factor
        }
        with open(map_file, 'w') as f:
            json.dump(data, f)
    
    def load_fog_texture(self):
        """Load the fog texture after display is initialized."""
        try:
            current_dir = os.getcwd()
            texture_path = os.path.join(current_dir, "cloud_fog.png")
            print(f"Looking for fog texture at: {texture_path}")
            print(f"File exists: {os.path.exists(texture_path)}")
            self.fog_texture = pygame.image.load(texture_path).convert_alpha()
            print("Successfully loaded fog texture")
            return True
        except Exception as e:
            print(f"Warning: Failed to load cloud_fog.png: {str(e)}")
            print("Using solid black fog instead.")
            return False
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_s:
                    if self.current_floor_index >= 0:
                        self.save_explored_areas(self.floors[self.current_floor_index])
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    self.brush_size = min(50, self.brush_size + 5)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    self.brush_size = max(5, self.brush_size - 5)
                elif event.key == pygame.K_o:
                    self.add_floor(self.select_map_file())
                elif event.key == pygame.K_SPACE:
                    self.is_revealing = not self.is_revealing
                elif event.key == pygame.K_h:
                    self.show_controls = not self.show_controls
                elif event.key == pygame.K_DELETE and self.current_floor_index >= 0:
                    self.remove_floor(self.current_floor_index)
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                if self.current_floor_index >= 0:
                    floor = self.floors[self.current_floor_index]
                    self.scale_factor = min(width / floor.width, height / floor.height)
                self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEWHEEL:
                if self.current_floor_index >= 0:
                    floor = self.floors[self.current_floor_index]
                    if event.y > 0:
                        floor.zoom_factor = min(self.max_zoom, floor.zoom_factor * 1.1)
                    else:
                        floor.zoom_factor = max(self.min_zoom, floor.zoom_factor / 1.1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:  # Middle mouse button
                    self.panning = True
                    self.last_pan_pos = event.pos
                elif event.button == 1:  # Left click
                    # Check if clicked on a tab
                    if event.pos[1] < self.tab_height:
                        tab_index = event.pos[0] // self.tab_width
                        if tab_index < len(self.floors):
                            self.current_floor_index = tab_index
                            self.initialize_screen(self.floors[self.current_floor_index])
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:  # Middle mouse button
                    self.panning = False
                    self.last_pan_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if self.current_floor_index >= 0:
                    floor = self.floors[self.current_floor_index]
                    if self.panning and self.last_pan_pos:
                        dx = event.pos[0] - self.last_pan_pos[0]
                        dy = event.pos[1] - self.last_pan_pos[1]
                        floor.pan_offset[0] += dx
                        floor.pan_offset[1] += dy
                        self.last_pan_pos = event.pos
                    elif event.buttons[0]:  # Left click for revealing
                        self.is_revealing = True
                        self.handle_mouse_draw(event.pos, floor)
                    elif event.buttons[2]:  # Right click for adding fog
                        self.is_revealing = False
                        self.handle_mouse_draw(event.pos, floor)
    
    def handle_mouse_draw(self, pos, floor):
        """Handle drawing with the mouse."""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        scaled_width = int(floor.width * self.scale_factor * floor.zoom_factor)
        scaled_height = int(floor.height * self.scale_factor * floor.zoom_factor)
        
        x_offset = (screen_width - scaled_width) // 2 + floor.pan_offset[0]
        y_offset = (screen_height - scaled_height) // 2 + floor.pan_offset[1] + self.tab_height
        
        x = int((pos[0] - x_offset) / (self.scale_factor * floor.zoom_factor))
        y = int((pos[1] - y_offset) / (self.scale_factor * floor.zoom_factor))
        
        if 0 <= x < floor.width and 0 <= y < floor.height:
            if self.is_revealing:
                # Create a smooth circle for revealing
                radius = self.brush_size
                # Create a temporary surface for the reveal effect
                temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                # Draw a circle with a gradient
                for r in range(radius, 0, -1):
                    alpha = int(255 * (1 - r/radius))  # Fade out towards edges
                    pygame.draw.circle(temp_surface, (255, 255, 255, alpha), (radius, radius), r)
                
                # Apply the reveal effect
                floor.fog_surface.blit(temp_surface, (x - radius, y - radius), special_flags=pygame.BLEND_RGBA_SUB)
                floor.explored_areas.add((x, y))
            else:
                # Create a smooth circle for adding fog
                radius = self.brush_size
                # Create a temporary surface for the fog effect
                temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                # Draw a circle with a gradient
                for r in range(radius, 0, -1):
                    alpha = int(255 * (r/radius))  # Fade in towards edges
                    pygame.draw.circle(temp_surface, (0, 0, 0, alpha), (radius, radius), r)
                
                # Apply the fog effect
                floor.fog_surface.blit(temp_surface, (x - radius, y - radius), special_flags=pygame.BLEND_RGBA_ADD)
                floor.explored_areas.discard((x, y))
    
    def run(self):
        """Main game loop."""
        if not self.screen:
            print("Please load a map first!")
            return
        
        while self.running:
            self.handle_events()
            
            # Clear screen
            self.screen.fill((0, 0, 0))
            
            # Draw tabs
            for i, floor in enumerate(self.floors):
                tab_color = (100, 100, 100) if i == self.current_floor_index else (50, 50, 50)
                pygame.draw.rect(self.screen, tab_color, 
                               (i * self.tab_width, 0, self.tab_width, self.tab_height))
                pygame.draw.rect(self.screen, (200, 200, 200),
                               (i * self.tab_width, 0, self.tab_width, self.tab_height), 1)
                
                # Draw floor name
                font = pygame.font.Font(None, 24)
                text = font.render(floor.name, True, (255, 255, 255))
                text_rect = text.get_rect(center=(i * self.tab_width + self.tab_width/2, self.tab_height/2))
                self.screen.blit(text, text_rect)
            
            if self.current_floor_index >= 0:
                floor = self.floors[self.current_floor_index]
                
                # Calculate scaled dimensions
                scaled_width = int(floor.width * self.scale_factor * floor.zoom_factor)
                scaled_height = int(floor.height * self.scale_factor * floor.zoom_factor)
                
                # Calculate position to center the map
                x_offset = (self.screen.get_width() - scaled_width) // 2 + floor.pan_offset[0]
                y_offset = (self.screen.get_height() - scaled_height) // 2 + floor.pan_offset[1] + self.tab_height
                
                # Draw everything scaled
                scaled_map = pygame.transform.scale(floor.map_surface, (scaled_width, scaled_height))
                scaled_fog = pygame.transform.scale(floor.fog_surface, (scaled_width, scaled_height))
                
                self.screen.blit(scaled_map, (x_offset, y_offset))
                self.screen.blit(scaled_fog, (x_offset, y_offset))
                
                if self.show_controls:
                    # Draw brush size indicator and controls
                    font = pygame.font.Font(None, 36)
                    text = font.render(f"Brush Size: {self.brush_size}", True, (255, 255, 255))
                    self.screen.blit(text, (10, self.tab_height + 10))
                    
                    # Draw mode indicator
                    mode_text = "Mode: Reveal" if self.is_revealing else "Mode: Fog"
                    text = font.render(mode_text, True, (255, 255, 255))
                    self.screen.blit(text, (10, self.tab_height + 50))
                    
                    # Draw zoom level
                    zoom_text = f"Zoom: {int(floor.zoom_factor * 100)}%"
                    text = font.render(zoom_text, True, (255, 255, 255))
                    self.screen.blit(text, (10, self.tab_height + 90))
                    
                    # Draw controls help
                    controls_font = pygame.font.Font(None, 24)
                    controls = [
                        "Controls:",
                        "Left Mouse: Reveal areas",
                        "Right Mouse: Add fog",
                        "Middle Mouse: Pan map",
                        "Space: Toggle mode",
                        "+/-: Adjust brush size",
                        "Mouse Wheel: Zoom in/out",
                        "H: Toggle controls",
                        "O: Add new floor",
                        "Delete: Remove current floor",
                        "S: Save progress",
                        "ESC: Exit"
                    ]
                    
                    for i, text in enumerate(controls):
                        text_surface = controls_font.render(text, True, (255, 255, 255))
                        self.screen.blit(text_surface, (10, self.tab_height + 140 + i * 25))
            
            pygame.display.flip()
        
        # Save all floors before exiting
        for floor in self.floors:
            self.save_explored_areas(floor)
        
        pygame.quit()
        sys.exit()

def main():
    viewer = MapViewer()
    
    # Get map file from command line or file dialog
    if len(sys.argv) > 1:
        map_path = sys.argv[1]
    else:
        map_path = viewer.select_map_file()
    
    if not map_path:
        print("No map selected. Exiting...")
        return
    
    if viewer.add_floor(map_path):
        viewer.run()
    else:
        print("Failed to load map. Please check the file path and try again.")

if __name__ == "__main__":
    main() 