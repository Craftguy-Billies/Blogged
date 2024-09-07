import os
from PIL import Image

def compress_images(directory, target_size_kb=220, initial_quality=85):
    """
    Compress all JPEG/PNG images in the given directory to ensure they are below the specified target size.

    :param directory: Directory containing images to compress.
    :param target_size_kb: Target size for the images in KB. Default is 220 KB.
    :param initial_quality: Starting quality for image compression (1-100). Default is 85.
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
            
            # Only compress if the file is larger than the target size
            if file_size_kb > target_size_kb:
                print(f"Compressing {filename} ({file_size_kb:.2f} KB)...")
                
                # Open an image file
                try:
                    with Image.open(file_path) as img:
                        # Handle PNG images differently (convert to JPEG if needed)
                        if filename.lower().endswith('.png'):
                            img = img.convert("RGB")  # Convert PNG to RGB for JPEG compression
                            output_filename = filename.rsplit('.', 1)[0] + ".jpg"
                        else:
                            output_filename = filename
                        
                        output_path = os.path.join(directory, output_filename)
                        
                        # Try compressing with progressively lower quality until the file is under the target size
                        quality = initial_quality
                        while True:
                            # Compress and save the image
                            img.save(output_path, optimize=True, quality=quality)
                            new_size_kb = os.path.getsize(output_path) / 1024
                            
                            # If the image is below the target size, break out of the loop
                            if new_size_kb <= target_size_kb or quality <= 10:
                                reduction_percentage = ((file_size_kb - new_size_kb) / file_size_kb) * 100
                                print(f"{filename} compressed successfully to {new_size_kb:.2f} KB ({reduction_percentage:.2f}% reduction)!")
                                break
                            else:
                                # Reduce quality by 5 for the next iteration
                                quality -= 5
                        
                        # Optionally delete the original PNG if converted to JPEG
                        if filename.lower().endswith('.png') and output_filename != filename:
                            os.remove(file_path)  # Remove the original .png file after conversion
                            print(f"Original PNG {filename} deleted after conversion.")
                            
                except Exception as e:
                    print(f"Error compressing {filename}: {e}")
            else:
                print(f"Skipping {filename} ({file_size_kb:.2f} KB) - already below target size.")
    
    print("Image compression completed.")

# Example usage
compress_images('./images/', target_size_kb=220, initial_quality=85)
