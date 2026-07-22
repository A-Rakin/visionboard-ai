import torch
from PIL import Image as PILImage

_blip_processor = None
_blip_model = None

def get_blip_pipeline():
    global _blip_processor, _blip_model
    if _blip_model is None:
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            print("[BLIP Engine] Loading Salesforce/blip-image-captioning-base...")
            _blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            _blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            _blip_model.eval()
        except Exception as e:
            print(f"[BLIP Engine Warning] Could not load BLIP transformers model ({e}). Using Heuristic Fallback Captioner.")
            _blip_model = 'FALLBACK'
    return _blip_processor, _blip_model

def generate_caption(image_path, detected_objects=None):
    """
    Generate natural language caption for an image.
    """
    processor, model = get_blip_pipeline()
    
    try:
        if model != 'FALLBACK' and processor is not None:
            raw_image = PILImage.open(image_path).convert('RGB')
            inputs = processor(raw_image, return_tensors="pt")
            with torch.no_grad():
                out = model.generate(**inputs, max_new_tokens=50)
            caption = processor.decode(out[0], skip_special_tokens=True)
            if caption:
                return caption.capitalize() + "."
    except Exception as e:
        print(f"[BLIP Caption Error] {e}")

    # Heuristic Fallback Captioner based on detected objects and visual context
    return _heuristic_fallback_caption(detected_objects)

def _heuristic_fallback_caption(detected_objects=None):
    if detected_objects:
        obj_names = [obj['object_name'].lower() for obj in detected_objects[:3]]
        if len(obj_names) == 1:
            return f"A detailed photo featuring a {obj_names[0]}."
        elif len(obj_names) == 2:
            return f"An image displaying a {obj_names[0]} and a {obj_names[1]}."
        elif len(obj_names) >= 3:
            return f"A vibrant composition featuring a {obj_names[0]}, {obj_names[1]}, and {obj_names[2]}."
    
    return "A high resolution digital image captured in natural lighting."
