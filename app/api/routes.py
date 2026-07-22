import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_file, url_for
from werkzeug.utils import secure_filename
from app.models import db
from app.models.image import Image
from app.models.caption import Caption
from app.models.object import DetectedObject
from app.models.text import ExtractedText
from app.models.color import DominantColor
from app.ai.pipeline import process_uploaded_image
from app.ai.clip import generate_text_embedding, load_embedding_file, calculate_cosine_similarity
from app.services.pdf_report import generate_ai_pdf_report

api_bp = Blueprint('api', __name__, url_prefix='/api')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@api_bp.route('/upload', methods=['POST'])
def api_upload():
    """
    Upload an image for full AI analysis pipeline processing.
    ---
    tags:
      - VisionBoard AI API
    consumes:
      - multipart/form-data
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: Image file to upload (JPG, PNG, WEBP)
    responses:
      200:
        description: Successfully uploaded and processed image
      400:
        description: Invalid request or file format
    """
    if 'image' not in request.files and 'file' not in request.files:
        return jsonify({'error': 'No image file provided in request.'}), 400

    file = request.files.get('image') or request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'Empty filename.'}), 400

    if file and allowed_file(file.filename):
        orig_filename = secure_filename(file.filename)
        ext = orig_filename.rsplit('.', 1)[1].lower()
        unique_name = f"api_{uuid.uuid4().hex}.{ext}"
        
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        file.save(save_path)

        # Default user ID = 1 for API calls if unauthenticated
        user_id = 1

        new_image = Image(
            user_id=user_id,
            image_name=unique_name,
            original_filename=orig_filename,
            file_path=save_path,
            processing_status='pending'
        )
        db.session.add(new_image)
        db.session.commit()

        # Run AI Pipeline synchronously for API
        process_uploaded_image(new_image.id, current_app.config['EMBEDDING_FOLDER'])

        return jsonify({
            'status': 'success',
            'image_id': new_image.id,
            'data': new_image.to_dict(include_details=True)
        }), 200

    return jsonify({'error': 'Unsupported file type.'}), 400

@api_bp.route('/search', methods=['GET', 'POST'])
def api_search():
    """
    Perform natural language vector similarity or color search.
    ---
    tags:
      - VisionBoard AI API
    parameters:
      - name: q
        in: query
        type: string
        description: Natural language text query (e.g. 'Laptop on desk', 'Red sports car')
    responses:
      200:
        description: List of matching images ranked by cosine similarity
    """
    query_text = request.args.get('q', '').strip() or (request.json.get('q') if request.is_json else '')
    if not query_text:
        return jsonify({'error': 'Please provide a search query parameter `q`.'}), 400

    text_vec = generate_text_embedding(query_text)
    all_images = Image.query.all()
    
    scored_list = []
    for img in all_images:
        if img.embedding:
            img_vec = load_embedding_file(img.embedding.embedding_path)
            if img_vec is not None:
                sim = calculate_cosine_similarity(text_vec, img_vec)
                scored_list.append({
                    'similarity_score': round(sim * 100, 2),
                    'image': img.to_dict(include_details=True)
                })

    scored_list.sort(key=lambda x: x['similarity_score'], reverse=True)
    return jsonify({
        'query': query_text,
        'count': len(scored_list),
        'results': scored_list[:15]
    }), 200

@api_bp.route('/caption/<int:image_id>', methods=['GET'])
def api_caption(image_id):
    """
    Retrieve generated BLIP AI caption for an image.
    """
    img = Image.query.get_or_404(image_id)
    caption = img.captions[0].generated_caption if img.captions else ''
    return jsonify({
        'image_id': img.id,
        'caption': caption,
        'confidence': img.captions[0].confidence if img.captions else 0.0
    })

@api_bp.route('/ocr/<int:image_id>', methods=['GET'])
def api_ocr(image_id):
    """
    Retrieve extracted OCR text for an image.
    """
    img = Image.query.get_or_404(image_id)
    return jsonify({
        'image_id': img.id,
        'extracted_text': [t.to_dict() for t in img.texts]
    })

@api_bp.route('/object/<int:image_id>', methods=['GET'])
def api_object(image_id):
    """
    Retrieve YOLOv8 detected objects & normalized bounding boxes for an image.
    """
    img = Image.query.get_or_404(image_id)
    return jsonify({
        'image_id': img.id,
        'detected_objects': [obj.to_dict() for obj in img.objects]
    })

@api_bp.route('/colors/<int:image_id>', methods=['GET'])
def api_colors(image_id):
    """
    Retrieve K-Means dominant color palette for an image.
    """
    img = Image.query.get_or_404(image_id)
    return jsonify({
        'image_id': img.id,
        'colors': [c.to_dict() for c in img.colors]
    })

@api_bp.route('/reports/<int:image_id>', methods=['GET'])
def api_report(image_id):
    """
    Generate and download PDF AI Report for an image.
    """
    img = Image.query.get_or_404(image_id)
    pdf_filename = f"api_report_{img.id}.pdf"
    pdf_path = os.path.join(current_app.config['REPORT_FOLDER'], pdf_filename)
    generate_ai_pdf_report(img, pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name=f"VisionBoard_Report_{img.id}.pdf")
