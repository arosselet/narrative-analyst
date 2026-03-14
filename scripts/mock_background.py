from PIL import Image, ImageDraw

def generate_cinematic_bg(output_path, width=1080, height=1920):
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    
    # Deep blue to teal/black gradient
    for y in range(height):
        ratio = y / height
        r = int(10 * (1-ratio))
        g = int(20 + 30 * ratio)
        b = int(40 + 60 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add some 'glowing' circuits or light points
    import random
    for _ in range(500):
        x = random.randint(0, width)
        y = random.randint(0, height)
        # Higher density in lower 2/3
        if y > height // 3:
            size = random.randint(1, 3)
            # Use teal/white glow
            color = random.choice([(0, 255, 255), (255, 255, 255), (100, 200, 255)])
            draw.ellipse([x, y, x+size, y+size], fill=color)

    img.save(output_path)
    print(f"Generated cinematic background: {output_path}")

if __name__ == "__main__":
    generate_cinematic_bg("analysis/test-reel-data/background.png")
