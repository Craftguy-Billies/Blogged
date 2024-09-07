import os
from PIL import Image

def compress_images(directory, quality=65, size_threshold_kb=200):
    """
    Compress all JPEG/PNG images in the given directory that are over a specified size threshold.
    
    :param directory: Directory containing images to compress.
    :param quality: Quality setting for image compression (1-100). Default is 85.
    :param size_threshold_kb: Compress images only if they are larger than this size in KB. Default is 200 KB.
    """
    # Check if directory exists
    if not os.path.isdir(directory):
        print(f"Directory {directory} does not exist.")
        return
    
    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(directory, filename)
            file_size_kb = os.path.getsize(file_path) / 1024  # File size in KB
            
            # Check if the file is larger than the size threshold
            if file_size_kb > size_threshold_kb:
                print(f"Compressing {filename} ({file_size_kb:.2f} KB)...")
                
                # Open an image file
                with Image.open(file_path) as img:
                    # Compress and save the image
                    img.save(file_path, optimize=True, quality=quality)
                    new_size_kb = os.path.getsize(file_path) / 1024
                    print(f"{filename} compressed successfully to {new_size_kb:.2f} KB!")
            else:
                print(f"Skipping {filename} ({file_size_kb:.2f} KB) - under threshold.")

    print("Image compression completed.")

# Example usage
compress_images('./images/')
