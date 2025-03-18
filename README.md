# D&D Map Viewer

A simple and intuitive map viewer application for Dungeons & Dragons games, featuring a fog of war system and multi-floor support.

## Features

- **Fog of War System**: Reveal and hide map areas with smooth transitions
- **Multi-Floor Support**: Add and switch between multiple map floors using tabs
- **Interactive Controls**: 
  - Pan, zoom, and reveal/hide map areas
  - Adjustable brush size for revealing/hiding areas
  - Automatic saving of explored areas
- **Customizable**: Support for custom fog textures (optional)

## Installation

1. Download the latest release from the releases page
2. Extract the contents to your desired location
3. (Optional) Place a `cloud_fog.png` file in the same directory as the executable to use a custom fog texture

## Usage

### Basic Controls

- **Left Mouse Button**: Reveal areas
- **Right Mouse Button**: Add fog back
- **Middle Mouse Button**: Pan the map
- **Mouse Wheel**: Zoom in/out
- **+/- Keys**: Adjust brush size
- **Space**: Toggle between reveal and fog mode
- **H**: Toggle controls display
- **O**: Add new floor
- **Delete**: Remove current floor
- **S**: Save progress
- **ESC**: Exit

### Adding Maps

1. Launch the application
2. Click 'O' or use the file dialog to select a map image
3. The map will be loaded and displayed with fog covering it
4. Repeat to add more floors

### Saving Progress

- Progress is automatically saved when:
  - Pressing 'S'
  - Switching floors
  - Closing the application
- Each map's progress is saved in a `.map` file with the same name as the image

## Requirements

- Windows 10 or later
- No additional software required (standalone executable)

## Custom Fog Texture

To use a custom fog texture:
1. Create a PNG image named `cloud_fog.png`
2. Place it in the same directory as the executable
3. The texture should be:
   - Grayscale
   - PNG format with transparency
   - Ideally 256x256 or 512x512 pixels
   - Seamless/tileable

## Troubleshooting

If you encounter any issues:
1. Make sure the executable and any map files are in the same directory
2. Check that map files are in a supported format (JPG, PNG, BMP)
3. Verify that you have write permissions in the directory for saving progress

## Support

For issues or feature requests, please create an issue in the repository.

## License

This project is open source and available under the MIT License. 
