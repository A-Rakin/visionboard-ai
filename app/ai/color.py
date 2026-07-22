import cv2
import numpy as np

def extract_dominant_colors(image_path, num_colors=5):
    """
    Extract dominant colors from an image using OpenCV and K-Means Clustering.
    Returns list of dicts: [{'hex_code': '#0057FF', 'rgb_value': 'rgb(0, 87, 255)', 'percentage': 45.2}, ...]
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return _default_colors()

        # Convert BGR to RGB and resize for speed
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        resized_image = cv2.resize(image, (150, 150), interpolation=cv2.INTER_AREA)

        # Reshape to pixel array
        pixels = resized_image.reshape(-1, 3).astype(np.float32)

        # K-Means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        flags = cv2.KMEANS_RANDOM_CENTERS
        compactness, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, flags)

        # Calculate percentages
        counts = np.bincount(labels.flatten())
        total_pixels = len(labels)
        percentages = (counts / total_pixels) * 100.0

        # Sort by percentage descending
        sorted_indices = np.argsort(percentages)[::-1]

        results = []
        for idx in sorted_indices:
            r, g, b = [int(c) for c in centers[idx]]
            hex_code = f"#{r:02x}{g:02x}{b:02x}".upper()
            rgb_val = f"rgb({r}, {g}, {b})"
            pct = float(percentages[idx])
            results.append({
                'hex_code': hex_code,
                'rgb_value': rgb_val,
                'percentage': round(pct, 2)
            })

        return results
    except Exception as e:
        print(f"[Color Analysis Error] {e}")
        return _default_colors()

def _default_colors():
    return [
        {'hex_code': '#3A86FF', 'rgb_value': 'rgb(58, 134, 255)', 'percentage': 40.0},
        {'hex_code': '#8338EC', 'rgb_value': 'rgb(131, 56, 236)', 'percentage': 30.0},
        {'hex_code': '#FF006E', 'rgb_value': 'rgb(255, 0, 110)', 'percentage': 30.0}
    ]
