import os
from PIL import Image

def analyze_image(path):
    print(f"Analyzing image at {path}...")
    if not os.path.exists(path):
        print("File does not exist!")
        return
        
    try:
        img = Image.open(path)
        print("Dimensions:", img.size)
        print("Mode:", img.mode)
        
        # Get pixel data
        pixels = list(img.getdata())
        total_pixels = len(pixels)
        
        # Count black pixels
        black_pixels = 0
        for px in pixels:
            # handle different pixel structures (RGB, RGBA, Grayscale, etc.)
            if isinstance(px, tuple):
                if all(c < 10 for c in px[:3]): # very close to black
                    black_pixels += 1
            else:
                if px < 10:
                    black_pixels += 1
                    
        black_percentage = (black_pixels / total_pixels) * 100
        print(f"Total pixels: {total_pixels}")
        print(f"Black pixels: {black_pixels} ({black_percentage:.2f}%)")
        
        # Print a small sample of unique colors
        unique_colors = set(pixels)
        print(f"Unique colors count: {len(unique_colors)}")
        print(f"Sample of colors (first 10): {list(unique_colors)[:10]}")
        
    except Exception as e:
        print("Error analyzing image:", e)

if __name__ == "__main__":
    analyze_image(r"C:\Users\user\.gemini\antigravity\brain\0a83d257-ab78-4f4b-907f-a50aff0d0275\emulator_preview5.png")
