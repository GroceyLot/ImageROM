import os
import struct
from PIL import Image
import argparse

def encode_color(r, g, b, a):
    """Encodes RGBA color into a 9-bit format stored as an integer.
       If alpha is 0 (transparent), return 0.
    """
    if a == 0:
        return 0
    return (r // 32) * 64 + (g // 32) * 8 + (b // 32) + 1

def decode_color(value):
    """Decodes a 9-bit encoded color value back to an RGBA tuple.
       If the value is 0, return a transparent color (0, 0, 0, 0).
    """
    if value == 0:
        return (0, 0, 0, 0)
    
    value -= 1
    r = (value // 64) * 32
    g = ((value % 64) // 8) * 32
    b = (value % 8) * 32
    return (r, g, b, 255)

def process_image(image_path):
    """Processes a single image into the custom format."""
    with Image.open(image_path) as img:
        img = img.convert('RGBA')
        width, height = img.size
        pixels = list(img.getdata())
        encoded_pixels = [encode_color(r, g, b, a) for r, g, b, a in pixels]
        return width, height, encoded_pixels

def write_custom_format(output_path, images_data):
    """Writes all images data into a single custom format file."""
    with open(output_path, 'wb') as f:
        # Write the header
        f.write(b'imag')  # 4 bytes 'imag'
        f.write(struct.pack('<B', len(images_data)))  # 1 byte for the number of images
        
        for image_name, width, height, encoded_pixels in images_data:
            # Prepare image descriptor
            num_pixels = width * height
            short_name = image_name[:4].ljust(4)[:4]  # First 4 letters, padded if necessary
            image_data = struct.pack('<I4sII', num_pixels, short_name.encode('ascii'), width, height)
            
            # Add the encoded pixel data
            packed_pixels = b''.join(struct.pack('<H', pixel) for pixel in encoded_pixels)
            
            # Write image descriptor and pixel data to file
            f.write(image_data)
            f.write(packed_pixels)

def convert_folder_to_custom_format(folder_path, output_path):
    """Converts all PNG and JPEG images in a folder to the custom format."""
    images_data = []
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            image_name = os.path.splitext(filename)[0]
            width, height, encoded_pixels = process_image(image_path)
            images_data.append((image_name, width, height, encoded_pixels))
    
    write_custom_format(output_path, images_data)

def decode_rom_to_images(rom_path, output_folder):
    """Decodes a ROM file and saves the images as PNGs in the specified folder."""
    with open(rom_path, 'rb') as f:
        header = f.read(4)
        if header != b'imag':
            raise ValueError("Invalid ROM file")
        
        num_images = struct.unpack('<B', f.read(1))[0]
        
        for _ in range(num_images):
            # Read exactly 16 bytes for the image descriptor
            image_descriptor = f.read(16)
            if len(image_descriptor) < 16:
                raise ValueError("Corrupted ROM file: Incomplete image descriptor")
            
            num_pixels, short_name, width, height = struct.unpack('<I4sII', image_descriptor)
            short_name = short_name.decode('ascii').rstrip('\x00')
            pixels = []
            
            for _ in range(num_pixels):
                encoded_pixel = struct.unpack('<H', f.read(2))[0]
                pixels.append(decode_color(encoded_pixel))
            
            img = Image.new('RGBA', (width, height))
            img.putdata(pixels)
            output_path = os.path.join(output_folder, f"{short_name}.png")
            img.save(output_path)

def main():
    parser = argparse.ArgumentParser(description="Encode or decode a custom ROM format.")
    parser.add_argument('action', type=str, choices=['encode', 'decode'], help='Action to perform: encode or decode.')
    parser.add_argument('input', type=str, help='Input folder (for encode) or ROM file (for decode).')
    parser.add_argument('output', type=str, help='Output ROM file (for encode) or output folder (for decode).')

    args = parser.parse_args()

    if args.action == 'encode':
        convert_folder_to_custom_format(args.input, args.output)
    elif args.action == 'decode':
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        decode_rom_to_images(args.input, args.output)

if __name__ == '__main__':
    main()
