import os
import json
from PIL import Image as PILImage
from app.models import db
from app.models.image import Image
from app.models.caption import Caption
from app.models.object import DetectedObject
from app.models.text import ExtractedText
from app.models.color import DominantColor
from app.models.tag import Tag
from app.models.embedding import ImageEmbedding
from app.ai.color import extract_dominant_colors
from app.ai.metadata import extract_exif, calculate_quality_score, compute_perceptual_hash, is_duplicate_hash
from app.ai.yolo import detect_objects
from app.ai.blip import generate_caption
from app.ai.ocr import extract_text
from app.ai.clip import generate_image_embedding, save_embedding_file

def process_uploaded_image(image_id, embedding_dir):
    """
    Unified AI Orchestrator Pipeline:
    1. Fetch Image record
    2. Extract metadata & Quality Score
    3. Run Object Detection (YOLOv8)
    4. Run Image Captioning (BLIP)
    5. Run OCR (EasyOCR)
    6. Extract Dominant Colors (K-Means)
    7. Generate CLIP Embedding (.npy file)
    8. Auto-generate Tags
    9. Check Duplicate Status
    10. Update DB record status
    """
    image_record = Image.query.get(image_id)
    if not image_record:
        print(f"[Pipeline Error] Image ID {image_id} not found.")
        return False

    try:
        image_record.processing_status = 'processing'
        db.session.commit()

        file_path = image_record.file_path
        
        # 1. Read Image Dimensions & EXIF
        try:
            with PILImage.open(file_path) as img:
                image_record.image_width, image_record.image_height = img.size
        except Exception:
            pass

        exif_dict = extract_exif(file_path)
        image_record.exif_data = json.dumps(exif_dict) if exif_dict else None

        # 2. Quality Score & Duplicate Check
        quality = calculate_quality_score(file_path)
        image_record.quality_score = quality

        current_hash = compute_perceptual_hash(file_path)
        if current_hash:
            # Check against other images in user's library
            other_images = Image.query.filter(Image.user_id == image_record.user_id, Image.id != image_id).all()
            for other in other_images:
                if other.exif_data:
                    # check hash stored or compute
                    other_hash = compute_perceptual_hash(other.file_path)
                    if is_duplicate_hash(current_hash, other_hash):
                        image_record.is_duplicate = True
                        break

        # 3. YOLO Object Detection
        detected_objs = detect_objects(file_path)
        for obj in detected_objs:
            obj_entry = DetectedObject(
                image_id=image_id,
                object_name=obj['object_name'],
                confidence=obj['confidence'],
                x=obj['box']['x'],
                y=obj['box']['y'],
                width=obj['box']['width'],
                height=obj['box']['height']
            )
            db.session.add(obj_entry)

        # 4. BLIP Caption Generation
        caption_text = generate_caption(file_path, detected_objs)
        caption_entry = Caption(
            image_id=image_id,
            generated_caption=caption_text,
            confidence=0.96
        )
        db.session.add(caption_entry)

        # 5. EasyOCR Text Extraction
        ocr_items = extract_text(file_path)
        for item in ocr_items:
            text_entry = ExtractedText(
                image_id=image_id,
                text=item['text'],
                confidence=item['confidence'],
                language=item['language']
            )
            db.session.add(text_entry)

        # 6. Dominant Color Extraction
        colors_list = extract_dominant_colors(file_path, num_colors=5)
        for col in colors_list:
            color_entry = DominantColor(
                image_id=image_id,
                hex_code=col['hex_code'],
                rgb_value=col['rgb_value'],
                percentage=col['percentage']
            )
            db.session.add(color_entry)

        # 7. CLIP Embedding Vector Generation
        embedding_vec = generate_image_embedding(file_path)
        npy_filename = f"{image_id}_{image_record.image_name}.npy"
        npy_path = os.path.join(embedding_dir, npy_filename)
        save_embedding_file(embedding_vec, npy_path)

        embedding_entry = ImageEmbedding(
            image_id=image_id,
            embedding_path=npy_path,
            model_name='CLIP-ViT-B/32'
        )
        db.session.add(embedding_entry)

        # 8. Auto-Generate Tags
        tags_to_add = set()
        for obj in detected_objs:
            tags_to_add.add(obj['object_name'].lower().capitalize())

        # Extract keywords from caption
        words = caption_text.replace('.', '').replace(',', '').split()
        stopwords = {'a', 'an', 'the', 'in', 'on', 'at', 'with', 'of', 'and', 'or', 'is', 'are', 'photo', 'image', 'picture', 'detailed'}
        for w in words:
            clean_w = w.strip().capitalize()
            if len(clean_w) > 3 and clean_w.lower() not in stopwords:
                tags_to_add.add(clean_w)

        # Color tags
        for col in colors_list[:2]:
            tags_to_add.add(col['hex_code'])

        for tag_str in tags_to_add:
            tag = Tag.query.filter_by(tag_name=tag_str).first()
            if not tag:
                tag = Tag(tag_name=tag_str)
                db.session.add(tag)
                db.session.flush()
            image_record.tags.append(tag)

        image_record.processing_status = 'completed'
        db.session.commit()
        print(f"[Pipeline Success] Image {image_id} successfully processed!")
        return True

    except Exception as e:
        db.session.rollback()
        image_record.processing_status = 'failed'
        db.session.commit()
        print(f"[Pipeline Exception] Failed processing image {image_id}: {e}")
        return False
