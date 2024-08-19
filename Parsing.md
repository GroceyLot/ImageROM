# File Structure

#### Header
- **Signature (4 bytes)**: The file starts with a signature, which is always the ASCII string `'imag'`. This signature is used to verify that the file being read conforms to the ImageROM format.
- **Number of Images (1 byte)**: A single byte that indicates the number of images stored in the ROM file.

#### Image Entries
Each image entry consists of the following components:

- **Number of Pixels (4 bytes)**: An unsigned integer representing the total number of pixels in the image.
- **Image Name (4 bytes)**: A 4-byte ASCII string providing the name of the image. This is usually a truncated or abbreviated version of the original filename.
- **Image Width (4 bytes)**: An unsigned integer specifying the image width.
- **Image Height (4 bytes)**: An unsigned integer specifying the image height.
- **Pixel Data**: Sequence of 16-bit integers, each representing one pixel in a compressed 9-bit color format.

### Color Encoding and Decoding

#### Encoding Colors
Colors are encoded in a 9-bit format, allowing for a reduced color palette:
- If the alpha value of a pixel is 0 (transparent), the pixel value is stored as 0.
- For non-transparent pixels, the RGB values are each divided by 32, reducing the granularity. The encoded value is calculated as follows:
```lua
  encoded_value = (r // 32) * 64 + (g // 32) * 8 + (b // 32) + 1
```

#### Decoding Colors
The decoding process reverses the encoding steps:
- A value of 0 represents a transparent pixel.
- Non-zero values are decomposed to extract the reduced RGB values, which are then scaled back to their original range by multiplying by 32.
