def generate_perlin_noise(
filename="perlin.png",
size=256,
sigma=5,
shape="circle",
fg_color=255,
bg_color=0,
):
    """
    Generate a Perlin-like smooth noise texture with a geometric shape mask.

    Parameters:
        filename (str): Output image filename.
        size (int): Output image will be size x size.
        sigma (float): Smoothing strength to simulate Perlin noise.
        shape (str): Shape mask to apply: "circle", "triangle", or "square".
        fg_color (int): Foreground color (0–255) for noise texture.
        bg_color (int): Background color (0–255) outside the shape.
    """
    # Step 1: create smoothed random noise (Perlin-like)
    noise = np.random.rand(size, size)
    smooth_noise = gaussian_filter(noise, sigma=sigma)

    # Step 2: normalize and scale to fg_color range
    normalized = (smooth_noise - smooth_noise.min()) / (smooth_noise.max() - smooth_noise.min())
    noise_img = (normalized * fg_color).astype(np.uint8)

    # Step 3: create shape mask
    shape_mask_img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(shape_mask_img)

    if shape == "circle":
        draw.ellipse((0, 0, size, size), fill=255)
    elif shape == "triangle":
        triangle = [(size//2, 0), (0, size), (size, size)]
        draw.polygon(triangle, fill=255)
    elif shape == "square":
        draw.rectangle((0, 0, size, size), fill=255)
    else:
        raise ValueError("Unsupported shape: choose 'circle', 'triangle', or 'square'.")

    # Step 4: apply mask to combine foreground noise and background
    shape_mask = np.array(shape_mask_img) // 255
    final_array = noise_img * shape_mask + bg_color * (1 - shape_mask)

    # Step 5: save image
    Image.fromarray(final_array.astype(np.uint8)).save(filename)

# Circle-shaped noise with gray FG and white BG
generate_perlin_noise("perlin_circle.png", shape="circle", fg_color=200, bg_color=255)

# Triangle-shaped noise with full contrast
generate_perlin_noise("perlin_triangle.png", shape="triangle", fg_color=255, bg_color=0)

# Square mask, low contrast noise on gray background
generate_perlin_noise("perlin_square.png", shape="square", fg_color=100, bg_color=180)




import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw

def generate_blob_texture(
filename="blob.png",
size=256,
threshold=0.5,
sigma=4,
shape="circle",
fg_color=255,
bg_color=0,
):
    """
    Generate a shape-masked blob texture with foreground and background color.

    Parameters:
        filename (str): Output file name.
        size (int): Image dimensions (square).
        threshold (float): Threshold for binarizing blobs.
        sigma (float): Gaussian smoothing factor.
        shape (str): "circle", "triangle", or "square".
        fg_color (int): Foreground (blob) color (0–255 grayscale).
        bg_color (int): Background color (0–255 grayscale).
    """
    # Generate random smooth noise
    noise = np.random.rand(size, size)
    smooth_noise = gaussian_filter(noise, sigma=sigma)
    blob_mask = smooth_noise > threshold  # binary mask of blobs

    # Convert blob to foreground color
    blob_img = (blob_mask * fg_color).astype(np.uint8)

    # Create shape mask
    shape_mask_img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(shape_mask_img)
    if shape == "circle":
        draw.ellipse((0, 0, size, size), fill=255)
    elif shape == "triangle":
        triangle = [(size//2, 0), (0, size), (size, size)]
        draw.polygon(triangle, fill=255)
    elif shape == "square":
        draw.rectangle((0, 0, size, size), fill=255)
    else:
        raise ValueError("Unsupported shape: choose 'circle', 'triangle', or 'square'.")

    # Apply shape mask to blend foreground and background
    shape_mask = np.array(shape_mask_img) // 255
    final_array = blob_img * shape_mask + bg_color * (1 - shape_mask)

    # Save image
    Image.fromarray(final_array.astype(np.uint8)).save(filename)


# Example usage
# Blue-ish blob on light gray background
generate_blob_texture("blob1.png", fg_color=180, bg_color=230, shape="circle")
# Gray blob on black
generate_blob_texture("blob3.png", fg_color=150, bg_color=0, shape="square")


import os
from PIL import Image, ImageDraw, ImageFont
# Stroke count to Unicode range mapping (inclusive)
stroke_to_unicode_range = {
    1:  (0x1B170, 0x1B170),
    2:  (0x1B171, 0x1B177),
    3:  (0x1B178, 0x1B18A),
    4:  (0x1B18B, 0x1B1A7),
    5:  (0x1B1A8, 0x1B1D5),
    6:  (0x1B1DE, 0x1B215),
    7:  (0x1B216, 0x1B243),
    8:  (0x1B244, 0x1B283),
    9:  (0x1B284, 0x1B2AF),
    10: (0x1B2B0, 0x1B2D5),
    11: (0x1B2CE, 0x1B2E0),
    12: (0x1B2E1, 0x1B2ED),
    13: (0x1B2EE, 0x1B2F3),
    14: (0x1B2F4, 0x1B2F6),
    15: (0x1B2F7, 0x1B2F9),
}

def generate_nushu_symbols(
font_path,
output_dir,
stroke,
stroke_range_dict,
bg_color="white",
fill_color="black",
img_size=100,
font_size=72
):
    """
    Generate Nüshu symbol images for a specific stroke count.

    Args:
        font_path (str): Path to the NotoSansNushu-Regular.ttf file.
        output_dir (str): Directory to save the generated images.
        stroke (int): Stroke count (1–15).
        stroke_range_dict (dict): Dict mapping stroke count → (start, end) Unicode range.
        bg_color (str or tuple): Background color (e.g., "white" or (255,255,255)).
        img_size (int): Width and height of the image in pixels.
        font_size (int): Size of the character font.
    """
    if stroke not in stroke_range_dict:
        raise ValueError(f"Stroke count {stroke} not valid. Choose from: {list(stroke_range_dict.keys())}")

    os.makedirs(output_dir, exist_ok=True)
    font = ImageFont.truetype(font_path, font_size)
    
    start, end = stroke_range_dict[stroke]
    for i, code in enumerate(range(start, end + 1)):
        char = chr(code)
        img = Image.new("RGB", (img_size, img_size), bg_color)
        draw = ImageDraw.Draw(img)

        # Center character on image
        # Center character on image using textbbox
        bbox = draw.textbbox((0, 0), char, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (img_size - w) // 2
        y = (img_size - h) // 2
        draw.text((x, y), char, font=font, fill=fill_color)

        filename = f"nushu_stroke{stroke}_{i:03d}_U{code:04X}.png"
        img.save(os.path.join(output_dir, filename))

generate_nushu_symbols(
    font_path="E:/xhmhc/TaskBeacon/PRL/font/NotoSansNushu-Regular.ttf",
    output_dir="E:/xhmhc/TaskBeacon/PRL/img",
    stroke=5,
    stroke_range_dict=stroke_to_unicode_range,
    bg_color="gray",
    img_size=128,
    font_size=90
)