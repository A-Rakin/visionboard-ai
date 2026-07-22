import cv2
import numpy as np
import json
from PIL import Image as PILImage
from PIL.ExifTags import TAGS, GPSTAGS

def extract_exif(image_path):
    """
    Extract EXIF metadata from image file (Camera, ISO, F-number, Exposure, Date).
    Returns dict / JSON readable structure.
    """
    metadata = {}
    try:
        image = PILImage.open(image_path)
        exif = image._getexif()
        if exif:
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'GPSInfo':
                    gps_data = {}
                    for g_tag in value:
                        g_name = GPSTAGS.get(g_tag, g_tag)
                        gps_data[g_name] = str(value[g_tag])
                    metadata['GPSInfo'] = gps_data
                else:
                    metadata[str(tag)] = str(value)
    except Exception:
        pass
    return metadata

def calculate_quality_score(image_path):
    """
    Calculates image quality score (0.0 to 100.0) using OpenCV.
    Uses Laplacian variance for blur/sharpness, average brightness, and contrast.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return 75.0
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Blur / Sharpness via Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(100.0, (laplacian_var / 500.0) * 100.0)

        # Brightness balance (ideal ~ 128)
        mean_brightness = np.mean(gray)
        brightness_score = 100.0 - abs(mean_brightness - 128) * 0.7

        # Contrast via standard deviation
        std_contrast = np.std(gray)
        contrast_score = min(100.0, (std_contrast / 64.0) * 100.0)

        quality = (sharpness_score * 0.5) + (brightness_score * 0.3) + (contrast_score * 0.2)
        return round(float(np.clip(quality, 10.0, 99.9)), 1)
    except Exception as e:
        print(f"[Quality Calculation Error] {e}")
        return 80.0

def compute_perceptual_hash(image_path):
    """
    Computes a 64-bit difference hash (dHash) for duplicate image detection.
    """
    try:
        img = PILImage.open(image_path).convert('L').resize((9, 8), PILImage.Resampling.LANCZOS)
        pixels = list(img.getdata())
        difference = []
        for row in range(8):
            for col in range(8):
                pixel_left = pixels[row * 9 + col]
                pixel_right = pixels[row * 9 + col + 1]
                difference.append(pixel_left > pixel_right)
        
        decimal_value = 0
        for bit in difference:
            decimal_value = (decimal_value << 1) | bit
        return hex(decimal_value)[2:].zfill(16)
    except Exception as e:
        print(f"[Perceptual Hash Error] {e}")
        return None

def is_duplicate_hash(hash1, hash2, max_hamming_distance=4):
    """
    Compare two 16-char hex perceptual hashes using Hamming distance.
    Returns True if images are near-duplicates.
    """
    if not hash1 or not hash2:
        return False
    try:
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        xor_val = val1 ^ val2
        hamming_dist = bin(xor_val).count('1')
        return hamming_dist <= max_hamming_distance
    except Exception:
        return False
