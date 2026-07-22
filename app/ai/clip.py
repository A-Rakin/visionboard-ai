import torch
import numpy as np
import os
from PIL import Image as PILImage

_clip_processor = None
_clip_model = None
_clip_tokenizer = None

def get_clip_engine():
    global _clip_processor, _clip_model, _clip_tokenizer
    if _clip_model is None:
        try:
            from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
            print("[CLIP Engine] Loading openai/clip-vit-base-patch32 model...")
            _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            _clip_tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
            _clip_model.eval()
        except Exception as e:
            print(f"[CLIP Engine Warning] Could not load CLIP model ({e}). Using Heuristic Normalized Feature Extractor.")
            _clip_model = 'FALLBACK'
    return _clip_processor, _clip_model, _clip_tokenizer

def generate_image_embedding(image_path):
    """
    Generate a 512-dimensional normalized floating-point embedding vector for an image.
    Returns 1D numpy array.
    """
    processor, model, _ = get_clip_engine()

    try:
        if model != 'FALLBACK' and processor is not None:
            raw_image = PILImage.open(image_path).convert('RGB')
            inputs = processor(images=raw_image, return_tensors="pt")
            with torch.no_grad():
                image_features = model.get_image_features(**inputs)
            # L2 Normalize vector
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            return image_features.squeeze().cpu().numpy()
    except Exception as e:
        print(f"[CLIP Image Embedding Error] {e}")

    # Fallback 512-d feature vector using color histogram and spatial features
    return _heuristic_image_vector(image_path)

def generate_text_embedding(text_query):
    """
    Generate a 512-dimensional normalized embedding vector for a natural language search query.
    Returns 1D numpy array.
    """
    _, model, tokenizer = get_clip_engine()

    try:
        if model != 'FALLBACK' and tokenizer is not None:
            inputs = tokenizer([text_query], padding=True, return_tensors="pt")
            with torch.no_grad():
                text_features = model.get_text_features(**inputs)
            # L2 Normalize vector
            text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
            return text_features.squeeze().cpu().numpy()
    except Exception as e:
        print(f"[CLIP Text Embedding Error] {e}")

    # Fallback pseudo-semantic vector from text hash
    return _heuristic_text_vector(text_query)

def calculate_cosine_similarity(vec1, vec2):
    """
    Compute Cosine Similarity between two 1D normalized numpy vectors.
    """
    if vec1 is None or vec2 is None:
        return 0.0
    try:
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        dot = np.dot(vec1, vec2)
        sim = dot / (norm1 * norm2)
        return float(np.clip(sim, 0.0, 1.0))
    except Exception as e:
        print(f"[Cosine Similarity Error] {e}")
        return 0.0

def save_embedding_file(embedding_vec, save_path):
    """
    Save embedding vector as a .npy binary numpy file.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    np.save(save_path, embedding_vec.astype(np.float32))

def load_embedding_file(npy_path):
    """
    Load embedding vector from .npy file.
    """
    if os.path.exists(npy_path):
        try:
            return np.load(npy_path)
        except Exception:
            pass
    return None

def _heuristic_image_vector(image_path):
    """
    Fallback deterministic 512-d feature vector derived from OpenCV HSV color histogram.
    """
    import cv2
    vec = np.zeros(512, dtype=np.float32)
    try:
        img = cv2.imread(image_path)
        if img is not None:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            hist_h = cv2.calcHist([hsv], [0], None, [170], [0, 180]).flatten()
            hist_s = cv2.calcHist([hsv], [1], None, [170], [0, 256]).flatten()
            hist_v = cv2.calcHist([hsv], [2], None, [172], [0, 256]).flatten()
            combined = np.concatenate([hist_h, hist_s, hist_v])
            vec = combined / (np.linalg.norm(combined) + 1e-7)
    except Exception:
        np.random.seed(abs(hash(image_path)) % 10000)
        vec = np.random.randn(512).astype(np.float32)
        vec /= np.linalg.norm(vec)
    return vec

def _heuristic_text_vector(text):
    np.random.seed(abs(hash(text.lower().strip())) % 10000)
    vec = np.random.randn(512).astype(np.float32)
    return vec / np.linalg.norm(vec)
